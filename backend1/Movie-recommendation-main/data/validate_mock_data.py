import json
import os
import sys

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def validate():
    movies_file = os.path.join(DATA_DIR, "movies.json")
    theaters_file = os.path.join(DATA_DIR, "theaters.json")
    shows_file = os.path.join(DATA_DIR, "shows.json")
    seats_file = os.path.join(DATA_DIR, "seats.json")
    
    for filepath, name in [(movies_file, "movies.json"), (theaters_file, "theaters.json"), 
                           (shows_file, "shows.json"), (seats_file, "seats.json")]:
        if not os.path.exists(filepath):
            print(f"ERROR: {name} does not exist at {filepath}")
            sys.exit(1)

    with open(movies_file, "r", encoding="utf-8") as f:
        movies = json.load(f)
    with open(theaters_file, "r", encoding="utf-8") as f:
        theaters = json.load(f)
    with open(shows_file, "r", encoding="utf-8") as f:
        shows = json.load(f)
    with open(seats_file, "r", encoding="utf-8") as f:
        seats = json.load(f)

    movie_ids = {m["id"] for m in movies}
    theater_ids = {t["id"] for t in theaters}
    show_ids = {s["id"] for s in shows}

    print("=== DATASET VALIDATION REPORT ===")
    print(f"[OK] Movies Count: {len(movies)} (Expected 20)")
    assert len(movies) == 20, "Should have 20 movies"
    
    print(f"[OK] Theaters Count: {len(theaters)} (Expected 5)")
    assert len(theaters) == 5, "Should have 5 theaters"
    
    print(f"[OK] Shows Count: {len(shows)}")
    assert len(shows) > 0, "Should have shows"

    print(f"[OK] Seats Count: {len(seats)}")
    assert len(seats) == len(shows) * 60, f"Each show must have 60 seats (found {len(seats)})"

    # Validate show references
    invalid_shows_movie = [s for s in shows if s["movie_id"] not in movie_ids]
    invalid_shows_theater = [s for s in shows if s["theater_id"] not in theater_ids]
    assert not invalid_shows_movie, f"Shows with invalid movie_id: {invalid_shows_movie}"
    assert not invalid_shows_theater, f"Shows with invalid theater_id: {invalid_shows_theater}"
    print("[OK] All shows properly reference existing movies and theaters.")

    # Validate seat references
    invalid_seats_show = [st for st in seats if st["show_id"] not in show_ids]
    assert not invalid_seats_show, f"Seats with invalid show_id: {invalid_seats_show}"
    print("[OK] All seats properly reference existing shows.")

    # Check seat status breakdown
    available_seats = [st for st in seats if st["status"] == "available"]
    booked_seats = [st for st in seats if st["status"] == "booked"]
    print(f"[OK] Total Seats: {len(seats)} (Available: {len(available_seats)}, Booked: {len(booked_seats)})")
    
    # Check genres & mood diversity
    genres = set()
    moods = set()
    for m in movies:
        genres.update(m.get("genre", []))
        moods.update(m.get("mood_tags", []))

    print(f"[OK] Unique Genres ({len(genres)}): {sorted(list(genres))}")
    print(f"[OK] Unique Mood Tags ({len(moods)}): {sorted(list(moods))}")
    print("\nALL VALIDATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    validate()
