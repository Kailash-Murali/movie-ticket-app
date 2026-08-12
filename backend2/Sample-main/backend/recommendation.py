"""Deterministic recommendation engine: hard filtering + satisfaction scoring."""

from backend.models import Movie, Show, UserPreference
from backend.seats import find_best_seats


def _time_to_minutes(t: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    parts = t.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def violates_hard_constraints(
    movie: Movie, show: Show, pref: UserPreference
) -> bool:
    """Return True if this show violates any hard constraint from this person."""
    if "avoid_genre" in pref.hard_constraints:
        for g in pref.avoid_genres:
            if g.lower() in [mg.lower() for mg in movie.genres]:
                return True

    if "language" in pref.hard_constraints:
        if pref.preferred_languages:
            if movie.language.lower() not in [l.lower() for l in pref.preferred_languages]:
                return True

    if "after_time" in pref.hard_constraints:
        if pref.after_time:
            show_mins = _time_to_minutes(show.time)
            pref_mins = _time_to_minutes(pref.after_time)
            if show_mins < pref_mins:
                return True

    if "max_price" in pref.hard_constraints:
        if pref.max_price is not None:
            if show.price > pref.max_price:
                return True

    if "max_runtime" in pref.hard_constraints:
        if pref.max_runtime is not None:
            if movie.runtime_minutes > pref.max_runtime:
                return True

    return False


def filter_hard_constraints(
    movies: list[Movie],
    shows: list[Show],
    preferences: list[UserPreference],
) -> list[tuple[Movie, Show]]:
    """Remove any movie+show pair that violates any group member's hard constraint."""
    movie_map = {m.id: m for m in movies}
    valid = []
    
    group_size = len(preferences)
    requires_adjacent = any("adjacent_seats" in p.hard_constraints for p in preferences)

    for show in shows:
        movie = movie_map.get(show.movie_id)
        if movie is None:
            continue
            
        if requires_adjacent:
            if find_best_seats(show.seats, group_size) is None:
                continue

        rejected = False
        for pref in preferences:
            if violates_hard_constraints(movie, show, pref):
                rejected = True
                break
        if not rejected:
            valid.append((movie, show))
    return valid


def calculate_satisfaction(
    movie: Movie, show: Show, pref: UserPreference
) -> float:
    """Calculate satisfaction score [0, 1] for a single person and a candidate show.

    score = genre_score * 0.35
           + language_score * 0.25
           + runtime_score * 0.15
           + time_score * 0.15
           + rating_score * 0.10
    """
    # --- Genre score ---
    genre_score = 0.5  # neutral default
    if pref.preferred_genres:
        matched = sum(
            1 for g in pref.preferred_genres
            if g.lower() in [mg.lower() for mg in movie.genres]
        )
        genre_score = matched / len(pref.preferred_genres) if pref.preferred_genres else 0.5
    # Penalty for soft-avoided genres
    for sp in pref.soft_preferences:
        sp_lower = sp.lower()
        if "avoid" in sp_lower or "no " in sp_lower:
            for genre in movie.genres:
                if genre.lower() in sp_lower:
                    genre_score *= 0.5

    # --- Language score ---
    language_score = 0.5  # neutral default
    if pref.preferred_languages:
        if movie.language.lower() in [l.lower() for l in pref.preferred_languages]:
            language_score = 1.0
        else:
            language_score = 0.2

    # --- Runtime score ---
    runtime_score = 0.5  # neutral default
    if pref.max_runtime is not None:
        if movie.runtime_minutes <= pref.max_runtime:
            runtime_score = 1.0
        else:
            # Soft over-limit penalty
            over = movie.runtime_minutes - pref.max_runtime
            runtime_score = max(0.0, 1.0 - (over / 60.0))
    # Boost for "short movie" soft pref
    for sp in pref.soft_preferences:
        if "short" in sp.lower():
            runtime_score = max(0.0, 1.0 - (movie.runtime_minutes / 120.0))

    # --- Time score ---
    time_score = 0.5  # neutral
    if pref.after_time:
        show_mins = _time_to_minutes(show.time)
        pref_mins = _time_to_minutes(pref.after_time)
        if show_mins >= pref_mins:
            time_score = 1.0
        else:
            diff = pref_mins - show_mins
            time_score = max(0.0, 1.0 - (diff / 180.0))
    # Boost for "later show" soft preference
    for sp in pref.soft_preferences:
        if "later" in sp.lower() or "late" in sp.lower() or "evening" in sp.lower():
            show_mins = _time_to_minutes(show.time)
            time_score = min(1.0, show_mins / (22 * 60))  # later = better

    # --- Rating score ---
    # Normalize 0-10 to 0-1
    rating_score = movie.rating / 10.0
    # Boost for "highly rated" soft preference
    for sp in pref.soft_preferences:
        if "rated" in sp.lower() or "rating" in sp.lower():
            rating_score = movie.rating / 10.0  # already done, but emphasize

    # --- Weighted sum ---
    score = (
        genre_score * 0.35
        + language_score * 0.25
        + runtime_score * 0.15
        + time_score * 0.15
        + rating_score * 0.10
    )

    return round(min(1.0, max(0.0, score)), 4)
