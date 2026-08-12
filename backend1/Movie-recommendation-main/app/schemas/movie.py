from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class MovieBase(BaseModel):
    id: str
    title: str
    genre: List[str]
    language: str
    runtime: int
    rating: float
    mood_tags: List[str]
    age_rating: str
    description: str
    formats: List[str]

    model_config = ConfigDict(from_attributes=True)

class MovieResponse(MovieBase):
    pass
