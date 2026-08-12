from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.movie import MovieResponse
from app.services.movie_service import MovieService

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("", response_model=List[MovieResponse])
def get_movies(
    genre: Optional[str] = None,
    language: Optional[str] = None,
    max_runtime: Optional[int] = None,
    min_rating: Optional[float] = None,
    mood: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all movies with optional filters (genre, language, max_runtime, min_rating, mood).
    """
    return MovieService.get_movies(
        db, 
        genre=genre, 
        language=language, 
        max_runtime=max_runtime, 
        min_rating=min_rating, 
        mood=mood
    )

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie_by_id(movie_id: str, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific movie by ID.
    """
    movie = MovieService.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie '{movie_id}' not found.")
    return movie
