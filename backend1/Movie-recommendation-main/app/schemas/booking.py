import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.show import ShowWithDetailsResponse

class BookingCreate(BaseModel):
    show_id: str
    seat_ids: List[str]
    user_name: Optional[str] = "Guest"

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    show_id: str
    movie: str
    theater: str
    show_date: str
    show_time: str
    seats: List[str]
    total_price: int
    user_name: str
    created_at: datetime.datetime
    qr_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
