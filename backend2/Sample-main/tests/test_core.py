"""Tests for core deterministic logic (no LLM calls)."""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models import Movie, Show, Seat, UserPreference
from backend.recommendation import (
    violates_hard_constraints,
    filter_hard_constraints,
    calculate_satisfaction,
)
from backend.consensus import rank_shows
from backend.seats import find_best_seats


# ─── Helper fixtures ───

def _make_seat(row: str, num: int, status: str = "available") -> Seat:
    return Seat(id=f"{row}{num}", row=row, number=num, status=status)


def _make_seats(rows: str = "ABCD", cols: int = 8) -> list[Seat]:
    seats = []
    for r in rows:
        for n in range(1, cols + 1):
            seats.append(_make_seat(r, n))
    return seats


MOVIE_COMEDY_HINDI = Movie(
    id="m1", title="Hasi Toh Phasi", genres=["comedy"],
    language="Hindi", runtime_minutes=165, rating=7.2,
)

MOVIE_HORROR = Movie(
    id="m4", title="Bhoot Bangla", genres=["horror"],
    language="Hindi", runtime_minutes=110, rating=6.5,
)

MOVIE_ACTION_ENG = Movie(
    id="m3", title="Rogue Protocol", genres=["action", "thriller"],
    language="English", runtime_minutes=140, rating=8.1,
)

SHOW_CHEAP_EARLY = Show(
    id="s1", movie_id="m1", cinema="PVR", screen=1,
    time="14:00", price=250, seats=_make_seats(),
)

SHOW_HORROR = Show(
    id="s7", movie_id="m4", cinema="PVR", screen=1,
    time="22:00", price=200, seats=_make_seats(),
)

SHOW_EXPENSIVE = Show(
    id="s5", movie_id="m3", cinema="PVR", screen=3,
    time="21:00", price=550, seats=_make_seats(),
)


# ─── Tests: Hard constraints ───

def test_no_horror_constraint():
    """'avoid_genre' should reject horror movies."""
    pref = UserPreference(
        avoid_genres=["horror"],
        hard_constraints=["avoid_genre"],
    )
    assert violates_hard_constraints(MOVIE_HORROR, SHOW_HORROR, pref) is True
    assert violates_hard_constraints(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref) is False


def test_max_price_constraint():
    """'max_price' should reject shows over ₹500."""
    pref = UserPreference(
        max_price=500,
        hard_constraints=["max_price"],
    )
    assert violates_hard_constraints(MOVIE_ACTION_ENG, SHOW_EXPENSIVE, pref) is True
    assert violates_hard_constraints(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref) is False


def test_after_time_constraint():
    """'after_time' should reject shows before 19:00."""
    pref = UserPreference(
        after_time="19:00",
        hard_constraints=["after_time"],
    )
    # 14:00 is before 19:00 → violated
    assert violates_hard_constraints(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref) is True
    # 22:00 is after 19:00 → ok
    assert violates_hard_constraints(MOVIE_HORROR, SHOW_HORROR, pref) is False


# ─── Tests: Satisfaction scoring ───

def test_satisfaction_score_range():
    """Satisfaction scores must be between 0 and 1."""
    pref = UserPreference(
        preferred_genres=["comedy"],
        preferred_languages=["Hindi"],
    )
    score = calculate_satisfaction(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref)
    assert 0.0 <= score <= 1.0


def test_genre_match_boosts_score():
    """Matching preferred genre should give higher score."""
    pref_match = UserPreference(preferred_genres=["comedy"])
    pref_miss = UserPreference(preferred_genres=["thriller"])

    score_match = calculate_satisfaction(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref_match)
    score_miss = calculate_satisfaction(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref_miss)

    assert score_match > score_miss


# ─── Tests: Group consensus ───

def test_consensus_ranking_order():
    """Recommendations should be sorted by (min_score, avg_score) descending."""
    movies = [MOVIE_COMEDY_HINDI, MOVIE_HORROR, MOVIE_ACTION_ENG]
    shows = [SHOW_CHEAP_EARLY, SHOW_HORROR, SHOW_EXPENSIVE]
    prefs = [
        UserPreference(preferred_genres=["comedy"], preferred_languages=["Hindi"]),
        UserPreference(avoid_genres=["horror"], hard_constraints=["avoid_genre"]),
    ]

    recs = rank_shows(movies, shows, prefs, top_n=3)

    # Horror should be filtered out
    rec_movie_ids = [r.movie_id for r in recs]
    assert "m4" not in rec_movie_ids, "Horror should be filtered by hard constraint"

    # Remaining should be sorted by min_score desc
    if len(recs) >= 2:
        assert recs[0].minimum_score >= recs[1].minimum_score


# ─── Tests: Seat algorithm ───

def test_seat_finds_contiguous_block():
    """Should find a contiguous block of available seats."""
    seats = _make_seats("C", 8)
    block = find_best_seats(seats, 3)
    assert block is not None
    assert len(block.seats) == 3


def test_seat_avoids_booked():
    """Block must not contain booked seats."""
    seats = [
        _make_seat("C", 1),
        _make_seat("C", 2),
        _make_seat("C", 3, "booked"),
        _make_seat("C", 4),
        _make_seat("C", 5),
        _make_seat("C", 6),
    ]
    block = find_best_seats(seats, 3)
    assert block is not None
    # The block should not include C3
    assert "C3" not in block.seats


def test_no_seats_available():
    """Should return None when no contiguous block fits."""
    seats = [
        _make_seat("A", 1, "booked"),
        _make_seat("A", 2),
        _make_seat("A", 3, "booked"),
    ]
    block = find_best_seats(seats, 2)
    assert block is None


def test_adjacent_seats_constraint():
    """'adjacent_seats' should reject shows without enough contiguous seats."""
    bad_seats = [
        _make_seat("A", 1, "available"),
        _make_seat("A", 2, "booked"),
        _make_seat("A", 3, "available"),
        _make_seat("A", 4, "available"),
        _make_seat("A", 5, "booked"),
    ]
    show_bad = Show(
        id="s_bad", movie_id="m1", cinema="PVR", screen=1,
        time="14:00", price=250, seats=bad_seats,
    )
    good_seats = [
        _make_seat("B", 1, "available"),
        _make_seat("B", 2, "available"),
        _make_seat("B", 3, "available"),
        _make_seat("B", 4, "booked"),
    ]
    show_good = Show(
        id="s_good", movie_id="m1", cinema="PVR", screen=1,
        time="14:00", price=250, seats=good_seats,
    )
    
    prefs = [
        UserPreference(hard_constraints=["adjacent_seats"]),
        UserPreference(),
        UserPreference(),
    ]
    movies = [MOVIE_COMEDY_HINDI]
    shows = [show_bad, show_good]
    valid = filter_hard_constraints(movies, shows, prefs)
    
    assert len(valid) == 1
    assert valid[0][1].id == "s_good"

def test_neutral_runtime_score():
    """Unspecified runtime should receive 0.5 score."""
    pref = UserPreference()
    score = calculate_satisfaction(MOVIE_COMEDY_HINDI, SHOW_CHEAP_EARLY, pref)
    # genre(0.5)*0.35 + lang(0.5)*0.25 + runtime(0.5)*0.15 + time(0.5)*0.15 + rating(0.72)*0.10
    # = 0.175 + 0.125 + 0.075 + 0.075 + 0.072 = 0.522
    assert score == 0.522

def test_booking_validation():
    """Booking should reject empty or duplicate seats."""
    from backend.booking import create_booking
    try:
        create_booking("s1", [])
        assert False, "Should have rejected empty seats"
    except ValueError as e:
        assert "At least one seat" in str(e)
        
    try:
        create_booking("s1", ["A1", "A1"])
        assert False, "Should have rejected duplicate seats"
    except ValueError as e:
        assert "Duplicate seats" in str(e)

# ─── Run ───

if __name__ == "__main__":
    tests = [
        test_no_horror_constraint,
        test_max_price_constraint,
        test_after_time_constraint,
        test_satisfaction_score_range,
        test_genre_match_boosts_score,
        test_consensus_ranking_order,
        test_seat_finds_contiguous_block,
        test_seat_avoids_booked,
        test_no_seats_available,
        test_adjacent_seats_constraint,
        test_neutral_runtime_score,
        test_booking_validation,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
