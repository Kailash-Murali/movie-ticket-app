from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.theater import TheaterResponse
from app.services.theater_service import TheaterService

router = APIRouter(prefix="/theaters", tags=["Theaters"])

@router.get("", response_model=List[TheaterResponse])
def get_theaters(db: Session = Depends(get_db)):
    """
    Retrieve all available cinema theaters.
    """
    return TheaterService.get_theaters(db)

@router.get("/{theater_id}", response_model=TheaterResponse)
def get_theater_by_id(theater_id: str, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific theater by ID.
    """
    theater = TheaterService.get_theater_by_id(db, theater_id)
    if not theater:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Theater '{theater_id}' not found.")
    return theater
