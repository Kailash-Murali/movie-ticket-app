from pydantic import BaseModel, Field
from typing import List, Optional

class UserIntent(BaseModel):
    genres: Optional[List[str]] = Field(default=None, description="Preferred genres e.g. Comedy, Action")
    moods: Optional[List[str]] = Field(default=None, description="Preferred mood tags e.g. funny, exciting")
    language: Optional[str] = Field(default=None, description="Preferred language e.g. English, Hindi, Tamil")
    max_runtime: Optional[int] = Field(default=None, description="Maximum runtime in minutes e.g. 120")
    min_rating: Optional[float] = Field(default=None, description="Minimum IMDB/User rating e.g. 8.0")
    date: Optional[str] = Field(default=None, description="Target show date YYYY-MM-DD")
    min_time: Optional[str] = Field(default=None, description="Minimum show time HH:MM 24h format e.g. 20:00")
    max_time: Optional[str] = Field(default=None, description="Maximum show time HH:MM 24h format e.g. 23:00")
    max_price: Optional[int] = Field(default=None, description="Maximum budget per person in INR e.g. 500")
    group_size: Optional[int] = Field(default=1, description="Total number of people in group")
    format: Optional[str] = Field(default=None, description="Preferred format e.g. IMAX, 2D")
    theater_preference: Optional[str] = Field(default=None, description="Preferred theater or location keyword")
    seat_preference: Optional[str] = Field(default=None, description="Seat preference e.g. best_view, center, recliner, cheapest")
