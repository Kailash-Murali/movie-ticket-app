from app.ai.intent_extractor import parse_intent_rules, extract_intent
from app.schemas.intent import UserIntent

def test_prompt_1_something_funny_tonight_after_8():
    intent = parse_intent_rules("Something funny tonight after 8")
    assert "Comedy" in intent.genres or "funny" in (intent.moods or [])
    assert intent.date == "2026-08-12"
    assert intent.min_time == "20:00"

def test_prompt_2_movie_under_2_hours():
    intent = parse_intent_rules("I want a movie under 2 hours")
    assert intent.max_runtime == 120

def test_prompt_3_highly_rated_thriller():
    intent = parse_intent_rules("Find me a highly rated thriller")
    assert "Thriller" in intent.genres
    assert intent.min_rating == 8.0

def test_prompt_4_going_with_4_friends_under_500_each():
    intent = parse_intent_rules("I'm going with 4 friends, something fun under 500 each")
    assert intent.group_size == 5
    assert intent.max_price == 500
    assert "funny" in (intent.moods or []) or "Comedy" in (intent.genres or [])

def test_prompt_5_something_relaxing_for_tonight():
    intent = parse_intent_rules("Something relaxing for tonight")
    assert "relaxing" in intent.moods
    assert intent.date == "2026-08-12"

def test_prompt_6_make_me_laugh():
    intent = parse_intent_rules("I don't care about the genre, just something that will make me laugh")
    assert "Comedy" in intent.genres or "funny" in intent.moods

def test_prompt_7_nothing_animated():
    intent = parse_intent_rules("Nothing animated")
    assert not intent.genres or "Animation" not in intent.genres

def test_prompt_8_after_9_pm_imax():
    intent = parse_intent_rules("After 9 PM, preferably IMAX")
    assert intent.min_time == "21:00"
    assert intent.format == "IMAX"

def test_prompt_9_english_under_400():
    intent = parse_intent_rules("Something in English under 400")
    assert intent.language == "English"
    assert intent.max_price == 400

def test_prompt_10_movie_for_parents_not_intense():
    intent = parse_intent_rules("Movie for my parents, nothing too intense")
    assert "Family" in intent.genres or "family-friendly" in intent.moods

def test_session_memory_intent_merging():
    # Turn 1
    intent1 = extract_intent("Find me something funny tonight")
    assert "Comedy" in intent1.genres
    assert intent1.date == "2026-08-12"

    # Turn 2: "Nothing animated"
    intent2 = extract_intent("Nothing animated", previous_intent=intent1)
    assert "Comedy" in intent2.genres
    assert "Animation" not in (intent2.genres or [])
    assert intent2.date == "2026-08-12"

    # Turn 3: "Under 400"
    intent3 = extract_intent("Under 400", previous_intent=intent2)
    assert "Comedy" in intent3.genres
    assert intent3.max_price == 400
    assert intent3.date == "2026-08-12"
