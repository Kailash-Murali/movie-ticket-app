from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.movie import Movie

class MovieService:
    @staticmethod
    def get_movies(
        db: Session,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        max_runtime: Optional[int] = None,
        min_rating: Optional[float] = None,
        mood: Optional[str] = None
    ) -> List[Movie]:
        query = db.query(Movie)

        if language:
            query = query.filter(Movie.language.ilike(f"%{language}%"))
        if max_runtime:
            query = query.filter(Movie.runtime <= max_runtime)
        if min_rating:
            query = query.filter(Movie.rating >= min_rating)

        movies = query.all()

        # In-memory filter for JSON list fields (genre and mood_tags) to support any DB dialect
        if genre:
            target_genre = genre.lower()
            movies = [
                m for m in movies 
                if any(target_genre in g.lower() for g in (m.genre or []))
            ]

        if mood:
            target_mood = mood.lower()
            movies = [
                m for m in movies 
                if any(target_mood in md.lower() for md in (m.mood_tags or []))
            ]

        return movies

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: str) -> Optional[Movie]:
        return db.query(Movie).filter(Movie.id == movie_id).first()
