import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.booking_service import BookingService

router = APIRouter(prefix="/payments", tags=["Payments"])

class MockPaymentRequest(BaseModel):
    booking_id: str

class MockPaymentResponse(BaseModel):
    status: str
    transaction_id: str
    booking_id: str
    message: str

@router.post("/mock", response_model=MockPaymentResponse)
def process_mock_payment(payload: MockPaymentRequest, db: Session = Depends(get_db)):
    """
    Process a mock payment for a booking.
    """
    booking = BookingService.get_booking_by_id(db, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking '{payload.booking_id}' not found.")

    tx_id = f"TX{uuid.uuid4().hex[:8].upper()}"
    return {
        "status": "success",
        "transaction_id": tx_id,
        "booking_id": payload.booking_id,
        "message": f"Payment of ₹{booking['total_price']} successfully processed!"
    }
