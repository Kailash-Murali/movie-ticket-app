"""Group consensus ranking using lexicographic max-min."""

from statistics import mean
from backend.models import Movie, Show, UserPreference, Recommendation
from backend.recommendation import filter_hard_constraints, calculate_satisfaction


def rank_shows(
    movies: list[Movie],
    shows: list[Show],
    preferences: list[UserPreference],
    top_n: int = 3,
) -> list[Recommendation]:
    """Rank shows using lexicographic (minimum_score, average_score) consensus.

    1. Filter out shows violating any hard constraint.
    2. Score every remaining show for every person.
    3. Rank descending by (min_score, avg_score).
    4. Return top_n recommendations.
    """
    movie_map = {m.id: m for m in movies}
    valid_pairs = filter_hard_constraints(movies, shows, preferences)

    if not valid_pairs:
        return []

    candidates: list[Recommendation] = []

    for movie, show in valid_pairs:
        scores = [
            calculate_satisfaction(movie, show, pref)
            for pref in preferences
        ]

        min_score = min(scores)
        avg_score = round(mean(scores), 4)

        reasons = _build_reasons(movie, show, scores, min_score, avg_score, preferences)

        candidates.append(
            Recommendation(
                movie_id=movie.id,
                show_id=show.id,
                movie_title=movie.title,
                cinema=show.cinema,
                time=show.time,
                price=show.price,
                individual_scores=scores,
                minimum_score=min_score,
                average_score=avg_score,
                reasons=reasons,
            )
        )

    # Lexicographic sort: maximize (min_score, avg_score)
    candidates.sort(key=lambda r: (r.minimum_score, r.average_score), reverse=True)

    return candidates[:top_n]


def _build_reasons(
    movie: Movie,
    show: Show,
    scores: list[float],
    min_score: float,
    avg_score: float,
    preferences: list[UserPreference],
) -> list[str]:
    """Build human-readable reasons for a recommendation."""
    reasons = ["Satisfies all hard constraints from every group member"]

    # Genre match info
    all_preferred = set()
    for p in preferences:
        all_preferred.update(g.lower() for g in p.preferred_genres)
    matched_genres = [g for g in movie.genres if g.lower() in all_preferred]
    if matched_genres:
        reasons.append(f"Matches preferred genres: {', '.join(matched_genres)}")

    # Language match
    lang_prefs = set()
    for p in preferences:
        lang_prefs.update(l.lower() for l in p.preferred_languages)
    if movie.language.lower() in lang_prefs:
        reasons.append(f"Language match: {movie.language}")

    # Fairness commentary
    if min_score >= 0.7:
        reasons.append(f"High minimum satisfaction ({min_score:.0%}) — fair for everyone")
    elif min_score >= 0.5:
        reasons.append(f"Moderate minimum satisfaction ({min_score:.0%})")

    if avg_score >= 0.8:
        reasons.append(f"Strong average satisfaction ({avg_score:.0%})")

    # Price note
    reasons.append(f"₹{show.price}/person at {show.cinema}, {show.time}")

    return reasons
