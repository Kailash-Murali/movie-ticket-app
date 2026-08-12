"""Pydantic data models for the movie booking assistant."""

from pydantic import BaseModel, Field
from typing import Literal


# ---------- Data layer ----------

class Movie(BaseModel):
    id: str
    title: str
    genres: list[str]
    language: str
    runtime_minutes: int
    rating: float


class Seat(BaseModel):
    id: str
    row: str
    number: int
    status: Literal["available", "booked"]


class Show(BaseModel):
    id: str
    movie_id: str
    cinema: str
    screen: int
    time: str          # "HH:MM"
    price: int
    seats: list[Seat]


# ---------- Preference models ----------

class UserPreference(BaseModel):
    preferred_genres: list[str] = Field(default_factory=list)
    avoid_genres: list[str] = Field(default_factory=list)
    preferred_languages: list[str] = Field(default_factory=list)
    after_time: str | None = None          # "HH:MM"
    max_price: int | None = None
    max_runtime: int | None = None
    seat_preference: str | None = None
    hard_constraints: list[str] = Field(default_factory=list)
    soft_preferences: list[str] = Field(default_factory=list)


# ---------- Recommendation models ----------

class Recommendation(BaseModel):
    movie_id: str
    show_id: str
    movie_title: str = ""
    cinema: str = ""
    time: str = ""
    price: int = 0
    individual_scores: list[float]
    minimum_score: float
    average_score: float
    reasons: list[str]


# ---------- Booking models ----------

class Booking(BaseModel):
    booking_id: str
    show_id: str
    seats: list[str]
    total_price: int
    status: str


# ---------- API request / response ----------

class RecommendRequest(BaseModel):
    members: list[str]


class RecommendResponse(BaseModel):
    parsed_preferences: list[UserPreference]
    recommendations: list[Recommendation]


class BookRequest(BaseModel):
    show_id: str
    seats: list[str]


class SeatBlock(BaseModel):
    seats: list[str]
    score: float


class SeatsResponse(BaseModel):
    seats: list[Seat]
    recommended_block: SeatBlock | None = None
