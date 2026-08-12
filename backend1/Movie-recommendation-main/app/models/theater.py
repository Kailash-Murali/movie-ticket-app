from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Theater(Base):
    __tablename__ = "theaters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    formats = Column(JSON, nullable=False)  # List of formats e.g. ["2D", "IMAX"]
    amenities = Column(JSON, nullable=False)  # List of amenities e.g. ["Dolby Atmos", "Recliner"]

    shows = relationship("Show", back_populates="theater", cascade="all, delete-orphan")
