import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True)
    show_id = Column(String, ForeignKey("shows.id"), nullable=False, index=True)
    user_name = Column(String, nullable=True, default="Guest")
    total_price = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="confirmed") # confirmed, cancelled
    seat_codes = Column(JSON, nullable=False) # List of seat codes e.g. ["D5", "D6"]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    show = relationship("Show", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False, index=True)
    seat_id = Column(String, ForeignKey("seats.id"), nullable=False, index=True)
    seat_code = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

    booking = relationship("Booking", back_populates="booking_seats")
