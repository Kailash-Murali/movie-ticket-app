from app.ai.intent_extractor import parse_intent_rules

def test_1_funny_tonight_after_8():
    prompt = "I want something funny tonight after 8."
    intent = parse_intent_rules(prompt)
    assert "Comedy" in intent.genres
    assert intent.date == "2026-08-12"
    assert intent.min_time == "20:00"

def test_2_going_with_4_friends():
    prompt = "I'm going with 4 friends."
    intent = parse_intent_rules(prompt)
    assert intent.group_size == 5

def test_3_under_500_rupees():
    prompt = "Something under 500 rupees."
    intent = parse_intent_rules(prompt)
    assert intent.max_price == 500

def test_4_nothing_longer_than_2_hours():
    prompt = "Nothing longer than 2 hours."
    intent = parse_intent_rules(prompt)
    assert intent.max_runtime == 120

def test_5_want_imax():
    prompt = "I want IMAX."
    intent = parse_intent_rules(prompt)
    assert intent.format == "IMAX"

def test_6_relaxing_and_feel_good():
    prompt = "I want something relaxing and feel-good."
    intent = parse_intent_rules(prompt)
    assert "relaxing" in intent.moods
    assert "feel-good" in intent.moods

def test_7_movie_for_parents():
    prompt = "I want a movie for my parents."
    intent = parse_intent_rules(prompt)
    assert "Family" in intent.genres or "family-friendly" in intent.moods

def test_8_best_seats_for_two_aisle():
    prompt = "Best seats for two near the aisle."
    intent = parse_intent_rules(prompt)
    assert intent.group_size == 2
    assert intent.seat_preference == "aisle"

def test_9_tomorrow_evening():
    prompt = "Tomorrow evening."
    intent = parse_intent_rules(prompt)
    assert intent.date == "2026-08-13"
    assert intent.min_time == "17:00"

def test_10_after_8_but_before_11():
    prompt = "After 8 but before 11."
    intent = parse_intent_rules(prompt)
    assert intent.min_time == "20:00"
    assert intent.max_time == "23:00"
