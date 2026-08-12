from typing import List, Dict, Any
from app.ai.llm_client import llm_client
from app.schemas.intent import UserIntent

SYSTEM_EXPLAINER_PROMPT = """
You are CineMate AI assistant. Explain the movie, show, or seat recommendation strictly using ONLY the provided facts.
Do NOT invent showtimes, prices, ratings, or facts not present in the backend facts list.
Keep your explanation concise, friendly, and convincing (2-3 sentences max).
"""

def generate_movie_explanation(user_prompt: str, intent: UserIntent, recommendations: List[Dict[str, Any]]) -> str:
    if not recommendations:
        return "I couldn't find an exact match for your request. Try broadening your budget or time preferences!"

    top = recommendations[0]
    movie = top["movie"]
    reasons = top["reasons"]

    facts = (
        f"Top Movie: {movie.title} ({movie.language}, {movie.runtime} mins, Rating {movie.rating}/10).\n"
        f"Genres: {', '.join(movie.genre)}.\n"
        f"Reasons: {'; '.join(reasons)}."
    )

    prompt = f"User Request: '{user_prompt}'\nFacts:\n{facts}\nProvide a warm, personalized 2-sentence recommendation explanation."

    text_resp = llm_client.generate_text(prompt, SYSTEM_EXPLAINER_PROMPT)
    if text_resp and text_resp.strip():
        return text_resp.strip()

    # Rule-based fallback explanation using factual reasons
    reason_str = " and ".join(reasons[:2]) if reasons else "it perfectly matches your movie preferences"
    return f"I highly recommend '{movie.title}'! {reason_str.capitalize()} with a strong rating of {movie.rating}/10."

def generate_show_explanation(recommended_show: Dict[str, Any]) -> str:
    if not recommended_show:
        return "No suitable shows were found for your selected criteria."

    show = recommended_show["show"]
    reasons = recommended_show["reasons"]

    movie_title = show.movie.title if show.movie else "Selected Movie"
    theater_name = show.theater.name if show.theater else "Selected Theater"

    fact_str = f"Show at {theater_name} on {show.date} at {show.time} ({show.format}, ₹{show.price}/ticket)."
    reason_str = ". ".join(reasons[:2])

    return f"The best show is at {theater_name} ({show.time}, {show.format}) for ₹{show.price}. {reason_str}."

def generate_seat_explanation(seats: List[str], reason: str, total_price: int) -> str:
    return f"Recommended seats {', '.join(seats)} for ₹{total_price}. {reason}"
