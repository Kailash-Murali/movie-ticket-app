from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.movie import MovieResponse
from app.schemas.theater import TheaterResponse

class ShowBase(BaseModel):
    id: str
    movie_id: str
    theater_id: str
    date: str
    time: str
    format: str
    price: int

    model_config = ConfigDict(from_attributes=True)

class ShowResponse(ShowBase):
    pass

class ShowWithDetailsResponse(ShowBase):
    movie: Optional[MovieResponse] = None
    theater: Optional[TheaterResponse] = None
