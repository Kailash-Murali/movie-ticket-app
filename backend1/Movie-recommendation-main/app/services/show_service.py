from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.show import Show

class ShowService:
    @staticmethod
    def get_shows(
        db: Session,
        movie_id: Optional[str] = None,
        theater_id: Optional[str] = None,
        date: Optional[str] = None,
        min_time: Optional[str] = None,
        max_price: Optional[int] = None,
        format: Optional[str] = None
    ) -> List[Show]:
        query = db.query(Show)

        if movie_id:
            query = query.filter(Show.movie_id == movie_id)
        if theater_id:
            query = query.filter(Show.theater_id == theater_id)
        if date:
            query = query.filter(Show.date == date)
        if min_time:
            query = query.filter(Show.time >= min_time)
        if max_price:
            query = query.filter(Show.price <= max_price)
        if format:
            query = query.filter(Show.format.ilike(f"%{format}%"))

        return query.order_by(Show.date, Show.time).all()

    @staticmethod
    def get_show_by_id(db: Session, show_id: str) -> Optional[Show]:
        return db.query(Show).filter(Show.id == show_id).first()
