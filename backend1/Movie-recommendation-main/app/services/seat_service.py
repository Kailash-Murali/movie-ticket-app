from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.seat import Seat

class SeatService:
    @staticmethod
    def get_seats_by_show(db: Session, show_id: str) -> List[Seat]:
        return db.query(Seat).filter(Seat.show_id == show_id).order_by(Seat.row, Seat.number).all()

    @staticmethod
    def get_seat_by_id(db: Session, seat_id: str) -> Optional[Seat]:
        return db.query(Seat).filter(Seat.id == seat_id).first()
