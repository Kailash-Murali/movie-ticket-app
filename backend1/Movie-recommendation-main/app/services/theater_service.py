from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.theater import Theater

class TheaterService:
    @staticmethod
    def get_theaters(db: Session) -> List[Theater]:
        return db.query(Theater).all()

    @staticmethod
    def get_theater_by_id(db: Session, theater_id: str) -> Optional[Theater]:
        return db.query(Theater).filter(Theater.id == theater_id).first()
