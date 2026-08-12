import json
import os
import random

# Ensure output directory exists
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

movies_data = [
    {
        "id": "M001",
        "title": "The Last Adventure",
        "genre": ["Comedy", "Adventure"],
        "language": "English",
        "runtime": 118,
        "rating": 8.2,
        "mood_tags": ["funny", "lighthearted", "exciting"],
        "age_rating": "U/A",
        "description": "A group of old friends embarks on a wild, hilarious quest across the globe.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M002",
        "title": "Laugh Out Loud",
        "genre": ["Comedy"],
        "language": "Hindi",
        "runtime": 105,
        "rating": 7.8,
        "mood_tags": ["funny", "feel-good", "relaxing"],
        "age_rating": "U",
        "description": "An accidental identity swap leads to non-stop comedy and chaos in a small town.",
        "formats": ["2D"]
    },
    {
        "id": "M003",
        "title": "Galactic Horizon",
        "genre": ["Sci-Fi", "Action"],
        "language": "English",
        "runtime": 145,
        "rating": 8.9,
        "mood_tags": ["exciting", "intense", "thought-provoking"],
        "age_rating": "U/A",
        "description": "Astronauts voyage through a wormhole in search of humanity's new home.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M004",
        "title": "Heartbeats & Coffee",
        "genre": ["Romance", "Comedy"],
        "language": "English",
        "runtime": 112,
        "rating": 7.5,
        "mood_tags": ["romantic", "funny", "feel-good"],
        "age_rating": "U/A",
        "description": "Two rival coffee shop owners unexpectedly fall in love during rainy season.",
        "formats": ["2D"]
    },
    {
        "id": "M005",
        "title": "Shadows in the Dark",
        "genre": ["Horror", "Thriller"],
        "language": "Tamil",
        "runtime": 128,
        "rating": 8.1,
        "mood_tags": ["dark", "intense"],
        "age_rating": "A",
        "description": "An abandoned mansion holds terrifying secrets that surface after midnight.",
        "formats": ["2D"]
    },
    {
        "id": "M006",
        "title": "Speed Demon",
        "genre": ["Action", "Thriller"],
        "language": "English",
        "runtime": 130,
        "rating": 8.4,
        "mood_tags": ["exciting", "intense"],
        "age_rating": "U/A",
        "description": "Underground street racers team up for an impossible heist across Europe.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M007",
        "title": "The Grand Heist",
        "genre": ["Action", "Comedy"],
        "language": "Hindi",
        "runtime": 125,
        "rating": 7.9,
        "mood_tags": ["funny", "exciting"],
        "age_rating": "U/A",
        "description": "A ragtag crew of quirky thieves attempts to rob the world's most secure museum.",
        "formats": ["2D"]
    },
    {
        "id": "M008",
        "title": "Whispers of the Forest",
        "genre": ["Drama"],
        "language": "Tamil",
        "runtime": 140,
        "rating": 8.7,
        "mood_tags": ["emotional", "thought-provoking"],
        "age_rating": "U",
        "description": "A moving tale of a village teacher fighting to save an ancient forest.",
        "formats": ["2D"]
    },
    {
        "id": "M009",
        "title": "Superstar Legacy",
        "genre": ["Action", "Drama"],
        "language": "Tamil",
        "runtime": 162,
        "rating": 8.6,
        "mood_tags": ["exciting", "emotional"],
        "age_rating": "U/A",
        "description": "A charismatic leader returns to reclaim his empire and bring justice.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M010",
        "title": "Neon City Lights",
        "genre": ["Sci-Fi", "Thriller"],
        "language": "English",
        "runtime": 115,
        "rating": 7.7,
        "mood_tags": ["intense", "dark", "thought-provoking"],
        "age_rating": "A",
        "description": "A detective in a dystopian metropolis hunts down a rogue AI clone.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M011",
        "title": "Pixel Pals",
        "genre": ["Animation", "Family", "Comedy"],
        "language": "English",
        "runtime": 94,
        "rating": 8.3,
        "mood_tags": ["funny", "feel-good", "family-friendly"],
        "age_rating": "U",
        "description": "Video game characters break out of their arcade cabinet to save the internet.",
        "formats": ["2D"]
    },
    {
        "id": "M012",
        "title": "Midnight Mystery",
        "genre": ["Thriller", "Drama"],
        "language": "Telugu",
        "runtime": 138,
        "rating": 8.0,
        "mood_tags": ["intense", "thought-provoking"],
        "age_rating": "U/A",
        "description": "A sharp investigator uncovers a web of deception in an aristocratic family.",
        "formats": ["2D"]
    },
    {
        "id": "M013",
        "title": "The Great Cooking Contest",
        "genre": ["Comedy", "Family"],
        "language": "Hindi",
        "runtime": 102,
        "rating": 7.4,
        "mood_tags": ["funny", "feel-good", "relaxing"],
        "age_rating": "U",
        "description": "A passion for food unites two rival families in a hilarious national culinary battle.",
        "formats": ["2D"]
    },
    {
        "id": "M014",
        "title": "Space Explorers",
        "genre": ["Animation", "Adventure", "Sci-Fi"],
        "language": "English",
        "runtime": 98,
        "rating": 8.0,
        "mood_tags": ["exciting", "family-friendly"],
        "age_rating": "U",
        "description": "Brave young cadets embark on an interstellar treasure hunt.",
        "formats": ["2D", "IMAX"]
    },
    {
        "id": "M015",
        "title": "Retro Romance",
        "genre": ["Romance", "Drama"],
        "language": "Tamil",
        "runtime": 135,
        "rating": 8.2,
        "mood_tags": ["romantic", "emotional"],
        "age_rating": "U",
        "description": "A nostalgic love story set in 1990s Madras told through letters.",
        "formats": ["2D"]
    },
    {
        "id": "M016",
        "title": "Cyber Code",
        "genre": ["Action", "Sci-Fi"],
        "language": "English",
        "runtime": 122,
        "rating": 7.6,
        "mood_tags": ["exciting", "intense"],
        "age_rating": "U/A",
        "description": "A genius hacker uncovers a global conspiracy threatening digital privacy.",
        "formats": ["2D"]
    },
    {
        "id": "M017",
        "title": "Family Reunion",
        "genre": ["Comedy", "Drama"],
        "language": "Telugu",
        "runtime": 140,
        "rating": 8.1,
        "mood_tags": ["funny", "feel-good", "emotional"],
        "age_rating": "U",
        "description": "Three estranged brothers come together for their father's 70th birthday.",
        "formats": ["2D"]
    },
    {
        "id": "M018",
        "title": "Haunted Villa",
        "genre": ["Horror"],
        "language": "Hindi",
        "runtime": 110,
        "rating": 6.9,
        "mood_tags": ["dark", "intense"],
        "age_rating": "A",
        "description": "College friends stay at an isolated resort during weekend getaway.",
        "formats": ["2D"]
    },
    {
        "id": "M019",
        "title": "Championship Fever",
        "genre": ["Action", "Drama"],
        "language": "Hindi",
        "runtime": 150,
        "rating": 8.5,
        "mood_tags": ["exciting", "emotional"],
        "age_rating": "U/A",
        "description": "An underdog street cricket team overcomes all odds to reach the national finals.",
        "formats": ["2D"]
    },
    {
        "id": "M020",
        "title": "The Silent Witness",
        "genre": ["Thriller"],
        "language": "English",
        "runtime": 116,
        "rating": 8.3,
        "mood_tags": ["intense", "thought-provoking"],
        "age_rating": "U/A",
        "description": "A court reporter uncovers secret wiretaps that implicate high-ranking officials.",
        "formats": ["2D"]
    }
]

theaters_data = [
    {
        "id": "T001",
        "name": "PVR Phoenix Marketcity",
        "location": "Velachery, Chennai",
        "distance_km": 4.5,
        "formats": ["2D", "IMAX"],
        "amenities": ["Dolby Atmos", "Recliner", "Food Court"]
    },
    {
        "id": "T002",
        "name": "Luxe Cinemas Express Avenue",
        "location": "Royapettah, Chennai",
        "distance_km": 6.2,
        "formats": ["2D", "IMAX"],
        "amenities": ["Dolby Atmos", "VIP Lounge", "Recliner"]
    },
    {
        "id": "T003",
        "name": "SPI Palazzo Forum Mall",
        "location": "Vadapalani, Chennai",
        "distance_km": 3.2,
        "formats": ["2D", "IMAX"],
        "amenities": ["IMAX Laser", "Dolby Atmos", "Recliner"]
    },
    {
        "id": "T004",
        "name": "INOX National Arcot",
        "location": "Anna Nagar, Chennai",
        "distance_km": 8.7,
        "formats": ["2D"],
        "amenities": ["4K Projection", "Standard Seating"]
    },
    {
        "id": "T005",
        "name": "AGS Cinemas T. Nagar",
        "location": "T. Nagar, Chennai",
        "distance_km": 5.0,
        "formats": ["2D"],
        "amenities": ["Dolby 7.1", "Standard Seating"]
    }
]

def generate_shows_and_seats():
    random.seed(42)  # For deterministic seed reproducibility
    dates = ["2026-08-12", "2026-08-13", "2026-08-14"]
    times = ["10:30", "13:45", "17:15", "20:30", "21:45", "22:15"]
    
    shows = []
    seats = []
    
    show_id_counter = 1
    
    for movie in movies_data:
        movie_id = movie["id"]
        movie_formats = movie["formats"]
        
        # Select 2-3 theaters for each movie
        selected_theaters = random.sample(theaters_data, k=random.choice([2, 3]))
        
        for theater in selected_theaters:
            theater_id = theater["id"]
            # Common formats between movie & theater
            available_formats = [f for f in movie_formats if f in theater["formats"]]
            if not available_formats:
                available_formats = ["2D"]
                
            for date in dates:
                # Pick 2 times per day for this movie at this theater
                selected_times = random.sample(times, k=2)
                for show_time in selected_times:
                    show_format = random.choice(available_formats)
                    
                    # Base price based on format
                    base_price = 400 if show_format == "IMAX" else 220
                    # Slight variation by theater
                    if theater["id"] in ["T001", "T002"]:
                        base_price += 50
                        
                    show_id = f"S{show_id_counter:03d}"
                    shows.append({
                        "id": show_id,
                        "movie_id": movie_id,
                        "theater_id": theater_id,
                        "date": date,
                        "time": show_time,
                        "format": show_format,
                        "price": base_price
                    })
                    
                    # Generate 60 seats (Rows A-F, Seats 1-10) for this show
                    rows = ["A", "B", "C", "D", "E", "F"]
                    
                    # Determine occupancy rate for show (e.g., S001 is 80% booked, S005 is sold out, S010 is sparse)
                    if show_id_counter % 12 == 0:
                        occupancy_rate = 1.0  # Sold out
                    elif show_id_counter % 3 == 0:
                        occupancy_rate = 0.75  # Heavily booked
                    elif show_id_counter % 2 == 0:
                        occupancy_rate = 0.40  # Moderately booked
                    else:
                        occupancy_rate = 0.15  # Lightly booked
                        
                    for row in rows:
                        for num in range(1, 11):
                            seat_code = f"{row}{num}"
                            seat_id = f"{show_id}-{seat_code}"
                            
                            # Seat type logic: A-B Standard, C-D Premium, E-F Recliner
                            if row in ["A", "B"]:
                                seat_type = "Standard"
                                price_offset = 0
                            elif row in ["C", "D"]:
                                seat_type = "Premium"
                                price_offset = 60
                            else:
                                seat_type = "Recliner"
                                price_offset = 150
                                
                            seat_price = base_price + price_offset
                            
                            # Determine booking status
                            is_booked = random.random() < occupancy_rate
                            status = "booked" if is_booked else "available"
                            
                            seats.append({
                                "id": seat_id,
                                "show_id": show_id,
                                "row": row,
                                "number": num,
                                "seat_code": seat_code,
                                "type": seat_type,
                                "status": status,
                                "price": seat_price
                            })
                            
                    show_id_counter += 1

    return shows, seats

def main():
    shows_data, seats_data = generate_shows_and_seats()
    
    with open(os.path.join(DATA_DIR, "movies.json"), "w", encoding="utf-8") as f:
        json.dump(movies_data, f, indent=2)
        
    with open(os.path.join(DATA_DIR, "theaters.json"), "w", encoding="utf-8") as f:
        json.dump(theaters_data, f, indent=2)
        
    with open(os.path.join(DATA_DIR, "shows.json"), "w", encoding="utf-8") as f:
        json.dump(shows_data, f, indent=2)
        
    with open(os.path.join(DATA_DIR, "seats.json"), "w", encoding="utf-8") as f:
        json.dump(seats_data, f, indent=2)
        
    print(f"Generated:")
    print(f"  Movies: {len(movies_data)}")
    print(f"  Theaters: {len(theaters_data)}")
    print(f"  Shows: {len(shows_data)}")
    print(f"  Seats: {len(seats_data)}")

if __name__ == "__main__":
    main()
