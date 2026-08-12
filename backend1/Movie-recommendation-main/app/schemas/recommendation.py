from pydantic import BaseModel
from typing import List, Optional
from app.schemas.movie import MovieResponse
from app.schemas.show import ShowWithDetailsResponse
from app.schemas.intent import UserIntent

class MovieRecommendationItem(BaseModel):
    movie_id: str
    movie: MovieResponse
    match_score: float
    reasons: List[str]

class MovieRecommendationResponse(BaseModel):
    intent: Optional[UserIntent] = None
    recommendations: List[MovieRecommendationItem]
    explanation: str

class ShowRecommendationItem(BaseModel):
    show: ShowWithDetailsResponse
    score: float
    reasons: List[str]

class ShowRecommendationResponse(BaseModel):
    recommended_show: Optional[ShowRecommendationItem] = None
    alternatives: List[ShowRecommendationItem] = []
    explanation: str

class SeatRecommendationResponse(BaseModel):
    show_id: str
    recommended_seats: List[str] # e.g. ["D5", "D6"]
    recommended_seat_ids: List[str] # Full seat database IDs
    score: float
    total_price: int
    reason: str
