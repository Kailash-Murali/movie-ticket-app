from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    genre = Column(JSON, nullable=False)  # List of genre strings
    language = Column(String, nullable=False, index=True)
    runtime = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    mood_tags = Column(JSON, nullable=False)  # List of mood tags
    age_rating = Column(String, nullable=False)
    description = Column(String, nullable=False)
    formats = Column(JSON, nullable=False)  # List of formats e.g. ["2D", "IMAX"]

    shows = relationship("Show", back_populates="movie", cascade="all, delete-orphan")
