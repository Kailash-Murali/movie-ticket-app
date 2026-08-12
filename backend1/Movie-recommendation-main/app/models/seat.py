from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Seat(Base):
    __tablename__ = "seats"

    id = Column(String, primary_key=True, index=True)
    show_id = Column(String, ForeignKey("shows.id"), nullable=False, index=True)
    row = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    seat_code = Column(String, nullable=False)  # e.g., "D5"
    type = Column(String, nullable=False)       # Standard, Premium, Recliner
    status = Column(String, nullable=False, default="available", index=True) # available, booked
    price = Column(Integer, nullable=False)

    show = relationship("Show", back_populates="seats")
