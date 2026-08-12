"""FastAPI backend for the movie booking assistant."""

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    Movie, Show, Seat, UserPreference,
    RecommendRequest, RecommendResponse, Recommendation,
    BookRequest, Booking, SeatsResponse, SeatBlock,
)
from backend.llm_service import parse_preference
from backend.consensus import rank_shows
from backend.seats import find_best_seats
from backend.booking import create_booking

app = FastAPI(title="AI Movie Booking Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_movies() -> list[Movie]:
    with open(DATA_DIR / "movies.json") as f:
        return [Movie(**m) for m in json.load(f)]


def _load_shows() -> list[Show]:
    with open(DATA_DIR / "shows.json") as f:
        return [Show(**s) for s in json.load(f)]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """Parse group preferences via LLM, filter, score, and rank shows."""
    if not req.members:
        raise HTTPException(status_code=400, detail="At least one member preference required")

    # Step 1: Parse each member's preference via Gemini
    parsed: list[UserPreference] = []
    for statement in req.members:
        try:
            pref = parse_preference(statement)
            parsed.append(pref)
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=f"LLM parsing failed: {e}")

    # Step 2: Load data
    movies = _load_movies()
    shows = _load_shows()

    # Step 3: Rank using consensus engine
    recommendations = rank_shows(movies, shows, parsed, top_n=3)

    if not recommendations:
        # No shows satisfy all hard constraints
        return RecommendResponse(
            parsed_preferences=parsed,
            recommendations=[],
        )

    return RecommendResponse(
        parsed_preferences=parsed,
        recommendations=recommendations,
    )


@app.get("/shows/{show_id}/seats", response_model=SeatsResponse)
def get_seats(show_id: str, group_size: int = 3):
    """Return seats for a show with recommended seat block."""
    shows = _load_shows()
    show = next((s for s in shows if s.id == show_id), None)

    if show is None:
        raise HTTPException(status_code=404, detail=f"Show {show_id} not found")

    recommended = find_best_seats(show.seats, group_size)

    return SeatsResponse(
        seats=show.seats,
        recommended_block=recommended,
    )


@app.post("/book", response_model=Booking)
def book(req: BookRequest):
    """Book seats for a show."""
    try:
        booking = create_booking(req.show_id, req.seats)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
