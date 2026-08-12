"""Booking persistence: save/load bookings to bookings.json."""

import json
import os
import uuid
from pathlib import Path
from backend.models import Booking, Show

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
SHOWS_FILE = DATA_DIR / "shows.json"


def _load_bookings() -> list[dict]:
    if not BOOKINGS_FILE.exists():
        return []
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)


def _save_bookings(bookings: list[dict]) -> None:
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2)


def _load_shows() -> list[dict]:
    with open(SHOWS_FILE, "r") as f:
        return json.load(f)


def _save_shows(shows: list[dict]) -> None:
    with open(SHOWS_FILE, "w") as f:
        json.dump(shows, f, indent=2)


def create_booking(show_id: str, seat_ids: list[str]) -> Booking:
    """Create a booking: mark seats as booked, persist to bookings.json.

    Raises ValueError for invalid show, already-booked seats, or unavailable seats.
    """
    if not seat_ids:
        raise ValueError("At least one seat must be selected")

    if len(seat_ids) != len(set(seat_ids)):
        raise ValueError("Duplicate seats are not allowed")

    shows_data = _load_shows()
    show_dict = None
    show_idx = None

    for i, s in enumerate(shows_data):
        if s["id"] == show_id:
            show_dict = s
            show_idx = i
            break

    if show_dict is None:
        raise ValueError(f"Invalid show ID: {show_id}")

    # Validate seats exist and are available
    seat_map = {seat["id"]: seat for seat in show_dict["seats"]}
    for sid in seat_ids:
        if sid not in seat_map:
            raise ValueError(f"Seat {sid} does not exist in show {show_id}")
        if seat_map[sid]["status"] == "booked":
            raise ValueError(f"Seat {sid} is already booked")

    # Mark seats as booked
    for seat in show_dict["seats"]:
        if seat["id"] in seat_ids:
            seat["status"] = "booked"

    shows_data[show_idx] = show_dict
    _save_shows(shows_data)

    # Create booking record
    bookings = _load_bookings()
    booking_id = f"B{len(bookings) + 1:03d}"
    total_price = show_dict["price"] * len(seat_ids)

    booking = Booking(
        booking_id=booking_id,
        show_id=show_id,
        seats=seat_ids,
        total_price=total_price,
        status="confirmed",
    )

    bookings.append(booking.model_dump())
    _save_bookings(bookings)

    return booking
