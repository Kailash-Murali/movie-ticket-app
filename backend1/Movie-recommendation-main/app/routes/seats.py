from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.seat import SeatResponse
from app.services.seat_service import SeatService

router = APIRouter(prefix="/shows", tags=["Seats"])

@router.get("/{show_id}/seats", response_model=List[SeatResponse])
def get_show_seats(show_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full seat map for a specific show including row, number, seat type, price, and status (available/booked).
    """
    seats = SeatService.get_seats_by_show(db, show_id)
    if not seats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No seats found for show '{show_id}'.")
    return seats
