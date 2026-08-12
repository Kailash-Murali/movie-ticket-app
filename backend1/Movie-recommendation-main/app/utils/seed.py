import json
import os
import sys

from sqlalchemy.orm import Session
from app.database.connection import engine, SessionLocal
from app.database.base import Base
from app.models.movie import Movie
from app.models.theater import Theater
from app.models.show import Show
from app.models.seat import Seat
from app.models.booking import Booking, BookingSeat

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")

def seed_db():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("Clearing existing data...")
        db.query(BookingSeat).delete()
        db.query(Booking).delete()
        db.query(Seat).delete()
        db.query(Show).delete()
        db.query(Theater).delete()
        db.query(Movie).delete()
        db.commit()

        print("Loading mock JSON files from data directory...")
        with open(os.path.join(DATA_DIR, "movies.json"), "r", encoding="utf-8") as f:
            movies_data = json.load(f)
        with open(os.path.join(DATA_DIR, "theaters.json"), "r", encoding="utf-8") as f:
            theaters_data = json.load(f)
        with open(os.path.join(DATA_DIR, "shows.json"), "r", encoding="utf-8") as f:
            shows_data = json.load(f)
        with open(os.path.join(DATA_DIR, "seats.json"), "r", encoding="utf-8") as f:
            seats_data = json.load(f)

        print(f"Seeding {len(movies_data)} Movies...")
        for m in movies_data:
            db.add(Movie(**m))

        print(f"Seeding {len(theaters_data)} Theaters...")
        for t in theaters_data:
            db.add(Theater(**t))

        db.commit()

        print(f"Seeding {len(shows_data)} Shows...")
        for s in shows_data:
            db.add(Show(**s))

        db.commit()

        print(f"Seeding {len(seats_data)} Seats in bulk...")
        # Bulk insert seats in chunks of 2000 for database efficiency
        seat_objects = [Seat(**st) for st in seats_data]
        chunk_size = 2000
        for i in range(0, len(seat_objects), chunk_size):
            db.bulk_save_objects(seat_objects[i:i + chunk_size])
            db.commit()

        print("DB SEEDING COMPLETED SUCCESSFULLY!")
        print(f"Total Movies: {db.query(Movie).count()}")
        print(f"Total Theaters: {db.query(Theater).count()}")
        print(f"Total Shows: {db.query(Show).count()}")
        print(f"Total Seats: {db.query(Seat).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
