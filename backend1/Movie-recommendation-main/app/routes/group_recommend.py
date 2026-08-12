"""Group consensus recommendation — adapted from Backend2's approach.

Parses N natural-language member preferences, filters hard constraints,
scores satisfaction per member, and ranks by lexicographic (min_score, avg_score).
"""

from statistics import mean
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.ai.intent_extractor import extract_intent
from app.services.movie_service import MovieService
from app.services.show_service import ShowService
from app.schemas.intent import UserIntent

router = APIRouter(prefix="/ai", tags=["AI Recommendation Engines"])


class GroupRecommendRequest(BaseModel):
    members: List[str]
    date: Optional[str] = None


class GroupRecommendation(BaseModel):
    movie_id: str
    show_id: str
    movie_title: str
    theater: str
    time: str
    format: str
    price: int
    individual_scores: List[float]
    minimum_score: float
    average_score: float
    reasons: List[str]


class GroupRecommendResponse(BaseModel):
    parsed_intents: List[UserIntent]
    recommendations: List[GroupRecommendation]


def _time_to_minutes(t: str) -> int:
    parts = t.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _violates_hard_constraints(movie, show, intent: UserIntent) -> bool:
    """Check if a show violates any hard constraint from this member."""
    # Genre avoidance (if user explicitly avoids genres)
    # Budget constraint
    if intent.max_price is not None and show.price > intent.max_price:
        return True
    # Time constraint
    if intent.min_time:
        show_mins = _time_to_minutes(show.time)
        pref_mins = _time_to_minutes(intent.min_time)
        if show_mins < pref_mins:
            return True
    if intent.max_time:
        show_mins = _time_to_minutes(show.time)
        pref_mins = _time_to_minutes(intent.max_time)
        if show_mins > pref_mins:
            return True
    # Runtime constraint
    if intent.max_runtime is not None and movie.runtime > intent.max_runtime:
        return True
    return False


def _calculate_satisfaction(movie, show, intent: UserIntent) -> float:
    """Score [0, 1] for a single member and a candidate show."""
    # Genre score (weight 0.35)
    genre_score = 0.5
    if intent.genres:
        movie_genres = [g.lower() for g in (movie.genre or [])]
        matched = sum(1 for g in intent.genres if g.lower() in movie_genres)
        genre_score = matched / len(intent.genres)

    # Language score (weight 0.25)
    lang_score = 0.5
    if intent.language:
        lang_score = 1.0 if intent.language.lower() in movie.language.lower() else 0.2

    # Runtime score (weight 0.15)
    runtime_score = 0.5
    if intent.max_runtime is not None:
        if movie.runtime <= intent.max_runtime:
            runtime_score = 1.0
        else:
            over = movie.runtime - intent.max_runtime
            runtime_score = max(0.0, 1.0 - (over / 60.0))

    # Time score (weight 0.15)
    time_score = 0.5
    if intent.min_time:
        show_mins = _time_to_minutes(show.time)
        pref_mins = _time_to_minutes(intent.min_time)
        if show_mins >= pref_mins:
            time_score = 1.0
        else:
            diff = pref_mins - show_mins
            time_score = max(0.0, 1.0 - (diff / 180.0))

    # Rating score (weight 0.10)
    rating_score = movie.rating / 10.0

    score = (
        genre_score * 0.35
        + lang_score * 0.25
        + runtime_score * 0.15
        + time_score * 0.15
        + rating_score * 0.10
    )
    return round(min(1.0, max(0.0, score)), 4)


@router.post("/group-recommend", response_model=GroupRecommendResponse)
def group_recommend(payload: GroupRecommendRequest, db: Session = Depends(get_db)):
    """Parse group member preferences, filter hard constraints, rank by consensus."""
    if not payload.members:
        return GroupRecommendResponse(parsed_intents=[], recommendations=[])

    # Step 1: Parse each member's intent
    intents = [extract_intent(statement) for statement in payload.members]

    # Step 2: Load all movies and shows
    movies = MovieService.get_movies(db)
    movie_map = {m.id: m for m in movies}

    shows = ShowService.get_shows(db, date=payload.date)
    if not shows:
        shows = ShowService.get_shows(db)

    # Step 3: Filter shows violating any member's hard constraints
    valid_pairs = []
    for show in shows:
        movie = movie_map.get(show.movie_id)
        if not movie:
            continue
        rejected = False
        for intent in intents:
            if _violates_hard_constraints(movie, show, intent):
                rejected = True
                break
        if not rejected:
            valid_pairs.append((movie, show))

    # Step 4: Score each valid pair for each member
    candidates = []
    for movie, show in valid_pairs:
        scores = [_calculate_satisfaction(movie, show, intent) for intent in intents]
        min_score = min(scores)
        avg_score = round(mean(scores), 4)

        reasons = ["Satisfies all group members' hard constraints"]
        all_preferred = set()
        for intent in intents:
            if intent.genres:
                all_preferred.update(g.lower() for g in intent.genres)
        matched_genres = [g for g in (movie.genre or []) if g.lower() in all_preferred]
        if matched_genres:
            reasons.append(f"Matches preferred genres: {', '.join(matched_genres)}")
        if min_score >= 0.7:
            reasons.append(f"High minimum satisfaction ({min_score:.0%})")
        reasons.append(f"₹{show.price}/person at {show.time}")

        theater_name = show.theater.name if show.theater else ""
        candidates.append(GroupRecommendation(
            movie_id=movie.id,
            show_id=show.id,
            movie_title=movie.title,
            theater=theater_name,
            time=show.time,
            format=show.format,
            price=show.price,
            individual_scores=scores,
            minimum_score=min_score,
            average_score=avg_score,
            reasons=reasons,
        ))

    # Step 5: Lexicographic sort by (min_score, avg_score) descending
    candidates.sort(key=lambda r: (r.minimum_score, r.average_score), reverse=True)

    return GroupRecommendResponse(
        parsed_intents=intents,
        recommendations=candidates[:5],
    )
