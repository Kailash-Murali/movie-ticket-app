from pydantic import BaseModel, ConfigDict
from typing import List

class TheaterBase(BaseModel):
    id: str
    name: str
    location: str
    distance_km: float
    formats: List[str]
    amenities: List[str]

    model_config = ConfigDict(from_attributes=True)

class TheaterResponse(TheaterBase):
    pass
