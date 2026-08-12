from typing import List, Dict, Any
from app.models.movie import Movie
from app.schemas.intent import UserIntent

def score_movie(movie: Movie, intent: UserIntent, weights: Dict[str, float] = None) -> Dict[str, Any]:
    if weights is None:
        weights = {
            "genre": 30.0,
            "mood": 20.0,
            "runtime": 15.0,
            "rating": 15.0,
            "language": 10.0,
            "format": 10.0
        }

    score = 0.0
    reasons = []

    # 1. Genre score (30 points)
    if intent.genres and movie.genre:
        movie_genres_lower = [g.lower() for g in movie.genre]
        matched_genres = [g for g in intent.genres if g.lower() in movie_genres_lower]
        if matched_genres:
            genre_ratio = len(matched_genres) / max(len(intent.genres), 1)
            added = weights["genre"] * genre_ratio
            score += added
            reasons.append(f"Matches genre: {', '.join(matched_genres)}")
    else:
        score += weights["genre"] * 0.5  # Neutral default score

    # 2. Mood score (20 points)
    if intent.moods and movie.mood_tags:
        movie_moods_lower = [m.lower() for m in movie.mood_tags]
        matched_moods = [m for m in intent.moods if m.lower() in movie_moods_lower]
        if matched_moods:
            mood_ratio = len(matched_moods) / max(len(intent.moods), 1)
            added = weights["mood"] * mood_ratio
            score += added
            reasons.append(f"Matches requested mood: {', '.join(matched_moods)}")
    else:
        score += weights["mood"] * 0.5

    # 3. Runtime score (15 points)
    if intent.max_runtime:
        if movie.runtime <= intent.max_runtime:
            score += weights["runtime"]
            reasons.append(f"Runtime ({movie.runtime} mins) is within your limit ({intent.max_runtime} mins)")
        else:
            overage = movie.runtime - intent.max_runtime
            penalty = min(weights["runtime"], overage * 0.5)
            score += max(0.0, weights["runtime"] - penalty)
    else:
        score += weights["runtime"] * 0.8

    # 4. Rating score (15 points)
    if intent.min_rating:
        if movie.rating >= intent.min_rating:
            score += weights["rating"]
            reasons.append(f"High rating of {movie.rating}/10 (exceeds {intent.min_rating})")
        else:
            rating_diff = intent.min_rating - movie.rating
            score += max(0.0, weights["rating"] - (rating_diff * 5.0))
    else:
        # Scale by rating out of 10
        score += weights["rating"] * (movie.rating / 10.0)
        if movie.rating >= 8.0:
            reasons.append(f"Critically acclaimed rating of {movie.rating}/10")

    # 5. Language score (10 points)
    if intent.language:
        if intent.language.lower() in movie.language.lower():
            score += weights["language"]
            reasons.append(f"Available in requested language ({movie.language})")
    else:
        score += weights["language"]

    # 6. Format score (10 points)
    if intent.format:
        movie_formats_lower = [f.lower() for f in movie.formats]
        if intent.format.lower() in movie_formats_lower:
            score += weights["format"]
            reasons.append(f"Available in {intent.format.upper()} format")
    else:
        score += weights["format"]

    final_score = round(min(100.0, score), 1)

    return {
        "movie_id": movie.id,
        "score": final_score,
        "reasons": reasons
    }

def rank_movies(movies: List[Movie], intent: UserIntent, top_k: int = 3) -> List[Dict[str, Any]]:
    scored = []
    for m in movies:
        res = score_movie(m, intent)
        scored.append({
            "movie": m,
            "score": res["score"],
            "reasons": res["reasons"]
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
