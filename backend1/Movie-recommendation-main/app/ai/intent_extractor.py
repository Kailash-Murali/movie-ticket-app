import re
import datetime
import logging
from typing import Optional, Dict, Any
from app.schemas.intent import UserIntent
from app.ai.llm_client import llm_client

logger = logging.getLogger("cinemate.intent")

CURRENT_DATE = "2026-08-12"

SYSTEM_PROMPT = """
You are an intent extraction AI for CineMate movie ticket booking system.
Convert user natural-language prompts into a JSON matching the following schema strictly:

JSON Schema:
{
  "genres": list of strings or null (e.g. ["Comedy", "Action", "Family", "Thriller", "Sci-Fi"]),
  "moods": list of strings or null (e.g. ["funny", "exciting", "relaxing", "feel-good", "lighthearted", "family-friendly"]),
  "language": string or null (e.g. "English", "Hindi", "Tamil", "Telugu"),
  "max_runtime": integer minutes or null (e.g. 120 for "under 2 hours" / "not too long"),
  "min_rating": float or null (e.g. 8.0 for "highly rated"),
  "date": string YYYY-MM-DD or null (use "2026-08-12" for "tonight"/"today", "2026-08-13" for "tomorrow"),
  "min_time": string HH:MM 24h format or null (e.g. "20:00" for "after 8 PM", "21:00" for "after 9 PM"),
  "max_time": string HH:MM 24h format or null (e.g. "23:00" for "before 11 PM"),
  "max_price": integer or null (e.g. 500 for "under 500", 400 for "under 400"),
  "group_size": integer (default 1, "going with 4 friends" = 5 total people),
  "format": string or null (e.g. "IMAX", "2D"),
  "theater_preference": string or null,
  "seat_preference": string or null (e.g. "best_view", "together", "cheapest", "aisle", "recliner")
}

Natural language rules:
- "make me laugh" / "something funny" -> genres: ["Comedy"], moods: ["funny"]
- "something light" -> moods: ["lighthearted", "feel-good"]
- "movie for my parents, nothing too intense" -> genres: ["Family"], moods: ["feel-good", "family-friendly"]
- "not too long" -> max_runtime: 120
- "highly rated" -> min_rating: 8.0
- "going with N friends" -> group_size: N + 1

Return ONLY valid JSON.
"""

def extract_intent(user_message: str, previous_intent: Optional[UserIntent] = None) -> UserIntent:
    """
    Extracts structured user intent using LLM with deterministic rule fallback and session intent merging.
    """
    if not user_message or not user_message.strip():
        return previous_intent or UserIntent()

    extracted = None
    try:
        llm_output = llm_client.generate_json(user_message, SYSTEM_PROMPT)
        if llm_output and isinstance(llm_output, dict):
            try:
                extracted = UserIntent(**llm_output)
                extracted = _normalize_intent(extracted, user_message)
            except Exception as e:
                logger.warning(f"Pydantic validation of LLM output failed: {e}. Falling back to rule parser.")
    except Exception as e:
        logger.error(f"Unexpected error in LLM intent client: {e}. Using rule fallback.")

    if not extracted:
        extracted = parse_intent_rules(user_message)

    if previous_intent:
        return merge_user_intents(previous_intent, extracted, user_message)

    return extracted

def merge_user_intents(prev: UserIntent, new_intent: UserIntent, raw_message: str) -> UserIntent:
    """
    Merges follow-up constraints into existing session intent.
    E.g. "Find something funny" -> "Nothing animated" -> "Under 400"
    """
    lower = raw_message.lower()

    # Create merged dict starting from previous intent
    merged_dict = prev.model_dump()

    # Handle explicit exclusions like "nothing animated", "no horror", etc.
    if "nothing animated" in lower or "no animation" in lower:
        if merged_dict.get("genres"):
            merged_dict["genres"] = [g for g in merged_dict["genres"] if g.lower() != "animation"]
            if not merged_dict["genres"]:
                merged_dict["genres"] = None

    # Merge non-null fields from new_intent
    new_dict = new_intent.model_dump()
    for field, val in new_dict.items():
        if val is not None and field != "group_size":
            if field == "genres" and merged_dict.get("genres") and "nothing animated" not in lower:
                # Combine unique genres
                combined = list(set(merged_dict["genres"] + val))
                merged_dict["genres"] = combined
            elif field == "moods" and merged_dict.get("moods"):
                combined = list(set(merged_dict["moods"] + val))
                merged_dict["moods"] = combined
            else:
                merged_dict[field] = val

    # Merge group_size if new explicitly > 1
    if new_intent.group_size and new_intent.group_size > 1:
        merged_dict["group_size"] = new_intent.group_size

    return UserIntent(**merged_dict)

def parse_intent_rules(text: str) -> UserIntent:
    lower = text.lower()

    # Genres & Special handling
    genres = []
    genre_keywords = {
        "comedy": "Comedy", "funny": "Comedy", "laugh": "Comedy", "fun": "Comedy",
        "action": "Action", "adventure": "Adventure", "sci-fi": "Sci-Fi",
        "scifi": "Sci-Fi", "romance": "Romance", "romantic": "Romance",
        "thriller": "Thriller", "horror": "Horror", "scary": "Horror",
        "drama": "Drama", "animation": "Animation", "family": "Family"
    }

    if "nothing animated" not in lower and "no animation" not in lower:
        for kw, target in genre_keywords.items():
            if kw in lower and target not in genres:
                genres.append(target)

    if any(k in lower for k in ["parents", "family", "kids"]) and "Family" not in genres:
        genres.append("Family")

    # Moods
    moods = []
    if "make me laugh" in lower or "funny" in lower or " fun " in lower or lower.endswith(" fun") or "something fun" in lower:
        moods.append("funny")
    if "light" in lower or "lighthearted" in lower:
        if "lighthearted" not in moods:
            moods.append("lighthearted")
        if "feel-good" not in moods:
            moods.append("feel-good")
    if "feel-good" in lower or "feelgood" in lower or "feel good" in lower:
        if "feel-good" not in moods:
            moods.append("feel-good")
    if "relaxing" in lower:
        moods.append("relaxing")
    if any(k in lower for k in ["parents", "family"]) and "nothing too intense" in lower:
        moods.append("feel-good")
        moods.append("family-friendly")

    for m in ["exciting", "emotional", "intense", "dark"]:
        if m in lower and m not in moods:
            moods.append(m)

    # Language
    language = None
    for lang in ["english", "hindi", "tamil", "telugu"]:
        if lang in lower:
            language = lang.capitalize()
            break

    # Max Runtime (e.g. "not too long", "under 2 hours", "nothing longer than 2 hours")
    max_runtime = None
    if "not too long" in lower or "not longer than 2 hours" in lower or "under 2 hours" in lower or "under two hours" in lower:
        max_runtime = 120
    else:
        runtime_match = re.search(r'(?:under|not longer than|nothing longer than|max|within)\s*(\d+)\s*(?:hours|hrs|hour|hr)', lower)
        if runtime_match:
            max_runtime = int(runtime_match.group(1)) * 60
        else:
            mins_match = re.search(r'(\d+)\s*(?:mins|minutes|min)', lower)
            if mins_match:
                max_runtime = int(mins_match.group(1))

    # Min Rating (e.g. "highly rated", "rating above 8")
    min_rating = None
    if "highly rated" in lower:
        min_rating = 8.0
    else:
        rating_match = re.search(r'rating\s*(?:above|>|of)?\s*(\d+(?:\.\d+)?)', lower)
        if rating_match:
            min_rating = float(rating_match.group(1))

    # Date ("tonight", "today", "tomorrow")
    date = None
    if "tonight" in lower or "today" in lower:
        date = CURRENT_DATE
    elif "tomorrow" in lower:
        date = "2026-08-13"

    # Time Bounds
    min_time = None
    max_time = None

    range_match = re.search(r'after\s*(\d{1,2})(?::(\d{2}))?\s*(?:pm|am)?\s*(?:but\s*)?before\s*(\d{1,2})(?::(\d{2}))?\s*(pm|am)?', lower)
    if range_match:
        min_hr = int(range_match.group(1))
        min_hr = min_hr + 12 if min_hr < 12 else min_hr
        min_time = f"{min_hr:02d}:00"

        max_hr = int(range_match.group(3))
        max_hr = max_hr + 12 if max_hr < 12 else max_hr
        max_time = f"{max_hr:02d}:00"
    else:
        time_match = re.search(r'after\s*(\d{1,2})(?::(\d{2}))?\s*(pm|am)?', lower)
        if time_match:
            hr = int(time_match.group(1))
            mins = time_match.group(2) or "00"
            ampm = time_match.group(3)
            if (ampm == "pm" or ampm is None) and hr in [7, 8, 9, 10, 11] and hr < 12:
                hr += 12
            min_time = f"{hr:02d}:{mins}"
        elif "evening" in lower:
            min_time = "17:00"

    # Max Price (e.g. "under 500", "under 400", "under 500 each")
    max_price = None
    price_match = re.search(r'(?:under|below|less than|budget|₹|rs\.?)\s*(\d+)', lower)
    if price_match:
        max_price = int(price_match.group(1))

    # Group Size
    group_size = 1
    friends_match = re.search(r'(?:with|plus)\s*(\d+)\s*friends', lower)
    if friends_match:
        group_size = int(friends_match.group(1)) + 1
    else:
        num_word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for word, val in num_word_map.items():
            if f"for {word}" in lower or f"with {word}" in lower:
                group_size = val
                break
        if group_size == 1:
            people_match = re.search(r'(?:for|with)\s*(\d+)\s*(?:people|persons|seats|friends|us)?', lower)
            if people_match:
                group_size = int(people_match.group(1))

    # Format
    fmt = "IMAX" if "imax" in lower else None

    # Seat Preference
    seat_pref = "best_view"
    if "aisle" in lower:
        seat_pref = "aisle"
    elif "cheap" in lower or "budget" in lower:
        seat_pref = "cheapest"
    elif "recliner" in lower:
        seat_pref = "recliner"

    return UserIntent(
        genres=genres or None,
        moods=moods or None,
        language=language,
        max_runtime=max_runtime,
        min_rating=min_rating,
        date=date,
        min_time=min_time,
        max_time=max_time,
        max_price=max_price,
        group_size=group_size,
        format=fmt,
        theater_preference=None,
        seat_preference=seat_pref
    )

def _normalize_intent(intent: UserIntent, raw_text: str) -> UserIntent:
    lower = raw_text.lower()
    if "friends" in lower and intent.group_size:
        m = re.search(r'(\d+)\s*friends', lower)
        if m and intent.group_size == int(m.group(1)):
            intent.group_size = int(m.group(1)) + 1
    return intent
