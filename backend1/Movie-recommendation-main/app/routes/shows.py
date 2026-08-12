from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.show import ShowResponse, ShowWithDetailsResponse
from app.services.show_service import ShowService

router = APIRouter(tags=["Shows"])

@router.get("/movies/{movie_id}/shows", response_model=List[ShowWithDetailsResponse])
def get_movie_shows(
    movie_id: str,
    date: Optional[str] = None,
    min_time: Optional[str] = None,
    max_price: Optional[int] = None,
    format: Optional[str] = None,
    theater_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all available shows for a specific movie with filtering options.
    """
    return ShowService.get_shows(
        db,
        movie_id=movie_id,
        theater_id=theater_id,
        date=date,
        min_time=min_time,
        max_price=max_price,
        format=format
    )

@router.get("/shows/{show_id}", response_model=ShowWithDetailsResponse)
def get_show_by_id(show_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single show details by show ID.
    """
    show = ShowService.get_show_by_id(db, show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Show '{show_id}' not found.")
    return show
