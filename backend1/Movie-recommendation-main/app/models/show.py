from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(String, primary_key=True, index=True)
    movie_id = Column(String, ForeignKey("movies.id"), nullable=False, index=True)
    theater_id = Column(String, ForeignKey("theaters.id"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    time = Column(String, nullable=False, index=True)  # HH:MM format
    format = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    movie = relationship("Movie", back_populates="shows")
    theater = relationship("Theater", back_populates="shows")
    seats = relationship("Seat", back_populates="show", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="show")
