from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    """
    Create a new movie seat booking with atomic database transaction and price calculation.
    """
    booking = BookingService.create_booking(
        db, 
        show_id=payload.show_id, 
        seat_ids=payload.seat_ids, 
        user_name=payload.user_name
    )
    details = BookingService.get_booking_by_id(db, booking.id)
    return details

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_by_id(booking_id: str, db: Session = Depends(get_db)):
    """
    Retrieve booking digital ticket and QR data by booking ID.
    """
    details = BookingService.get_booking_by_id(db, booking_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking '{booking_id}' not found.")
    return details
