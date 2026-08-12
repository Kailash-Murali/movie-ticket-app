from app.models.movie import Movie
from app.models.show import Show
from app.models.theater import Theater
from app.schemas.intent import UserIntent
from app.algorithms.movie_scoring import score_movie, rank_movies
from app.algorithms.show_scoring import score_show, rank_shows

def create_sample_movie(id="M001", title="Test Movie", genre=["Comedy"], language="English", runtime=110, rating=8.5, mood_tags=["funny"], formats=["2D", "IMAX"]):
    return Movie(
        id=id,
        title=title,
        genre=genre,
        language=language,
        runtime=runtime,
        rating=rating,
        mood_tags=mood_tags,
        age_rating="U/A",
        description="Sample description",
        formats=formats
    )

def test_movie_scoring_comedy_preference():
    movie = create_sample_movie(genre=["Comedy"])
    intent = UserIntent(genres=["Comedy"])
    res = score_movie(movie, intent)
    assert res["score"] > 60.0
    assert any("Comedy" in r for r in res["reasons"])

def test_movie_scoring_runtime_constraint():
    short_movie = create_sample_movie(runtime=100)
    long_movie = create_sample_movie(runtime=160)
    intent = UserIntent(max_runtime=120)

    short_res = score_movie(short_movie, intent)
    long_res = score_movie(long_movie, intent)

    assert short_res["score"] > long_res["score"]

def test_movie_scoring_rating_constraint():
    high_rating = create_sample_movie(rating=8.8)
    low_rating = create_sample_movie(rating=6.0)
    intent = UserIntent(min_rating=8.0)

    high_res = score_movie(high_rating, intent)
    low_res = score_movie(low_rating, intent)

    assert high_res["score"] > low_res["score"]

def test_movie_scoring_language_constraint():
    tamil_movie = create_sample_movie(language="Tamil")
    hindi_movie = create_sample_movie(language="Hindi")
    intent = UserIntent(language="Tamil")

    t_res = score_movie(tamil_movie, intent)
    h_res = score_movie(hindi_movie, intent)

    assert t_res["score"] > h_res["score"]

def test_movie_scoring_mood_preference():
    relaxing_movie = create_sample_movie(mood_tags=["relaxing", "feel-good"])
    dark_movie = create_sample_movie(mood_tags=["dark", "intense"])
    intent = UserIntent(moods=["relaxing"])

    r_res = score_movie(relaxing_movie, intent)
    d_res = score_movie(dark_movie, intent)

    assert r_res["score"] > d_res["score"]

def test_movie_scoring_format_preference():
    imax_movie = create_sample_movie(formats=["2D", "IMAX"])
    standard_movie = create_sample_movie(formats=["2D"])
    intent = UserIntent(format="IMAX")

    i_res = score_movie(imax_movie, intent)
    s_res = score_movie(standard_movie, intent)

    assert i_res["score"] > s_res["score"]

def test_movie_scoring_no_match():
    # Empty movie list handling in rank_movies
    ranked = rank_movies([], UserIntent(genres=["Comedy"]))
    assert ranked == []

def test_show_scoring_time_range_and_budget():
    theater = Theater(id="T001", name="PVR", location="Chennai", distance_km=3.0, formats=["2D"], amenities=[])
    show_good = Show(id="S001", movie_id="M001", theater_id="T001", date="2026-08-12", time="20:30", format="2D", price=400, theater=theater)
    show_late = Show(id="S002", movie_id="M001", theater_id="T001", date="2026-08-12", time="23:30", format="2D", price=600, theater=theater)

    intent = UserIntent(min_time="20:00", max_time="22:00", max_price=500)

    good_res = score_show(show_good, intent)
    late_res = score_show(show_late, intent)

    assert good_res["score"] > late_res["score"]
    assert "fits your time window" in " ".join(good_res["reasons"])
    assert "exceeds budget" in " ".join(late_res["reasons"]) or "later than" in " ".join(late_res["reasons"])
