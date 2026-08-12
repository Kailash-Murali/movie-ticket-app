from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.intent import UserIntent
from app.schemas.recommendation import (
    MovieRecommendationResponse,
    MovieRecommendationItem,
    ShowRecommendationResponse,
    ShowRecommendationItem,
    SeatRecommendationResponse
)
from app.ai.intent_extractor import extract_intent
from app.algorithms.movie_scoring import rank_movies
from app.algorithms.show_scoring import rank_shows
from app.algorithms.seat_recommendation import recommend_seats_for_show
from app.services.movie_service import MovieService
from app.services.show_service import ShowService
from app.services.seat_service import SeatService
from app.ai.recommendation_explainer import (
    generate_movie_explanation,
    generate_show_explanation,
    generate_seat_explanation
)

router = APIRouter(prefix="/ai", tags=["AI Recommendation Engines"])

class MovieRecommendRequest(BaseModel):
    message: str

class ShowRecommendRequest(BaseModel):
    movie_id: str
    preferences: Optional[UserIntent] = None

class SeatRecommendRequest(BaseModel):
    show_id: str
    group_size: int = 2
    preference: Optional[str] = "best_view"

@router.post("/recommend", response_model=MovieRecommendationResponse)
def ai_recommend_movies(payload: MovieRecommendRequest, db: Session = Depends(get_db)):
    """
    AI Movie Recommendation: LLM Intent Extraction + DB Filtering + Weighted Movie Scoring + Facts-based LLM Explanation.
    """
    user_intent = extract_intent(payload.message)
    
    movies = MovieService.get_movies(
        db,
        genre=user_intent.genres[0] if user_intent.genres else None,
        language=user_intent.language,
        max_runtime=user_intent.max_runtime,
        min_rating=user_intent.min_rating
    )
    if not movies:
        movies = MovieService.get_movies(db) # Fallback to all movies if filter empty

    ranked = rank_movies(movies, user_intent, top_k=3)
    explanation = generate_movie_explanation(payload.message, user_intent, ranked)

    items = [
        MovieRecommendationItem(
            movie_id=item["movie"].id,
            movie=item["movie"],
            match_score=item["score"],
            reasons=item["reasons"]
        )
        for item in ranked
    ]

    return MovieRecommendationResponse(
        intent=user_intent,
        recommendations=items,
        explanation=explanation
    )

@router.post("/show-recommendation", response_model=ShowRecommendationResponse)
def ai_recommend_shows(payload: ShowRecommendRequest, db: Session = Depends(get_db)):
    """
    AI Show Recommendation: Ranks available shows for a movie based on time, budget, format, and distance.
    """
    movie = MovieService.get_movie_by_id(db, payload.movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie '{payload.movie_id}' not found.")

    intent = payload.preferences or UserIntent()
    shows = ShowService.get_shows(db, movie_id=payload.movie_id, date=intent.date)
    if not shows:
        shows = ShowService.get_shows(db, movie_id=payload.movie_id)

    ranked_res = rank_shows(shows, intent, group_size=intent.group_size or 1)

    rec_show_item = None
    if ranked_res["recommended_show"]:
        rec_item = ranked_res["recommended_show"]
        rec_show_item = ShowRecommendationItem(
            show=rec_item["show"],
            score=rec_item["score"],
            reasons=rec_item["reasons"]
        )

    alt_items = [
        ShowRecommendationItem(
            show=item["show"],
            score=item["score"],
            reasons=item["reasons"]
        )
        for item in ranked_res["alternatives"]
    ]

    explanation = generate_show_explanation(ranked_res["recommended_show"])

    return ShowRecommendationResponse(
        recommended_show=rec_show_item,
        alternatives=alt_items,
        explanation=explanation
    )

@router.post("/seat-recommendation", response_model=SeatRecommendationResponse)
def ai_recommend_seats(payload: SeatRecommendRequest, db: Session = Depends(get_db)):
    """
    AI Seat Recommendation: Deterministic seat placement scoring for group size, centering, view height & pricing.
    """
    seats = SeatService.get_seats_by_show(db, payload.show_id)
    if not seats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Show '{payload.show_id}' not found or has no seats.")

    rec_res = recommend_seats_for_show(seats, group_size=payload.group_size, preference=payload.preference)

    return SeatRecommendationResponse(
        show_id=payload.show_id,
        recommended_seats=rec_res["recommended_seats"],
        recommended_seat_ids=rec_res["recommended_seat_ids"],
        score=rec_res["score"],
        total_price=rec_res["total_price"],
        reason=rec_res["reason"]
    )
