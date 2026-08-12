"""Gemini LLM service for natural-language preference extraction."""

import json
import os
from dotenv import load_dotenv
from google import genai
from backend.models import UserPreference

load_dotenv()

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """You are a movie preference extraction assistant.

Given a person's natural-language statement about their movie preferences, extract structured information.

Return ONLY valid JSON with these fields:
{
  "preferred_genres": [],
  "avoid_genres": [],
  "preferred_languages": [],
  "after_time": null,
  "max_price": null,
  "max_runtime": null,
  "seat_preference": null,
  "hard_constraints": [],
  "soft_preferences": []
}

Rules:
- hard_constraints: things the person MUST have or MUST NOT have. Do not use natural language for hard constraints. Use ONLY these canonical identifiers:
  - "avoid_genre" (e.g. "No horror")
  - "language" (e.g. "Must be Hindi")
  - "after_time" (e.g. "Nothing before 7 PM")
  - "max_price" (e.g. "Maximum ₹500")
  - "max_runtime" (e.g. "Under 2 hours")
  - "adjacent_seats" (e.g. "We need to sit together")
- soft_preferences: things the person prefers but can compromise on. Phrases like "prefer comedy", "would like Hindi", "something short".
- after_time: extract as "HH:MM" 24-hour format if they mention a time constraint (e.g., "after 7" → "19:00", "after 7 PM" → "19:00").
- max_price: extract as integer if they mention a price limit (e.g., "under 500" → 500).
- max_runtime: extract as integer minutes if they mention runtime limit.
- seat_preference: extract seat location preference if mentioned (e.g., "middle seats", "back row").
- Genres should be lowercase: comedy, action, thriller, horror, drama, romance, family.
- Languages should be capitalized: Hindi, English, Tamil, etc.

Return ONLY the JSON object, no markdown, no explanation."""


def parse_preference(statement: str) -> UserPreference:
    """Parse a natural language preference statement into a UserPreference.

    Calls Gemini, validates with Pydantic. Retries once on failure.
    """
    client = _get_client()

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"{_SYSTEM_PROMPT}\n\nUser statement: \"{statement}\"",
            )

            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                lines = raw.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                raw = "\n".join(lines)

            data = json.loads(raw)
            return UserPreference(**data)

        except Exception as e:
            if attempt == 0:
                continue  # retry once
            raise RuntimeError(
                f"Failed to parse preference after 2 attempts: {e}"
            ) from e

    # Unreachable, but satisfies type checker
    raise RuntimeError("Failed to parse preference")


def generate_explanation(recommendation_data: dict) -> str:
    """Optionally generate a short explanation for why a recommendation ranked where it did."""
    client = _get_client()
    try:
        prompt = (
            "Given this movie recommendation data, write a brief 2-3 sentence explanation "
            "of why this movie was the best group match. Focus on constraint satisfaction "
            "and fairness.\n\n"
            f"Data: {json.dumps(recommendation_data)}"
        )
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        return "This option satisfies all group constraints with the best balance of individual satisfaction."
