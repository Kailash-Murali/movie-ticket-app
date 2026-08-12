import uuid
import random
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.show import Show
from app.models.seat import Seat
from app.models.booking import Booking, BookingSeat
from app.models.movie import Movie
from app.models.theater import Theater

class BookingService:
    @staticmethod
    def create_booking(db: Session, show_id: str, seat_ids: List[str], user_name: Optional[str] = "Guest") -> Booking:
        if not seat_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No seats selected for booking.")

        # Check for duplicate seat IDs in payload
        if len(seat_ids) != len(set(seat_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate seat IDs provided in booking request.")

        # 1. Verify show exists
        show = db.query(Show).filter(Show.id == show_id).first()
        if not show:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Show '{show_id}' not found.")

        # 2. Fetch seats with FOR UPDATE lock (if supported) or session transaction
        seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
        if len(seats) != len(seat_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more invalid seat IDs provided.")

        # 3. Verify all seats belong to the show & are available
        total_price = 0
        seat_codes = []
        for seat in seats:
            if seat.show_id != show_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Seat '{seat.seat_code}' does not belong to show '{show_id}'."
                )
            if seat.status != "available":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Seat '{seat.seat_code}' is already booked or unavailable."
                )
            total_price += seat.price
            seat_codes.append(seat.seat_code)

        # Generate unique booking ID
        booking_id = f"CM{random.randint(10000, 99999)}"
        while db.query(Booking).filter(Booking.id == booking_id).first() is not None:
            booking_id = f"CM{random.randint(10000, 99999)}"

        try:
            # 4. Mark seats as booked
            for seat in seats:
                seat.status = "booked"

            # 5. Create Booking record
            new_booking = Booking(
                id=booking_id,
                show_id=show_id,
                user_name=user_name or "Guest",
                total_price=total_price,
                status="confirmed",
                seat_codes=seat_codes
            )
            db.add(new_booking)

            # 6. Create BookingSeat records
            for seat in seats:
                b_seat = BookingSeat(
                    booking_id=booking_id,
                    seat_id=seat.id,
                    seat_code=seat.seat_code,
                    price=seat.price
                )
                db.add(b_seat)

            db.commit()
            db.refresh(new_booking)
            return new_booking

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process booking transaction: {str(e)}"
            )

    @staticmethod
    def get_booking_by_id(db: Session, booking_id: str) -> Optional[dict]:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None

        show = db.query(Show).filter(Show.id == booking.show_id).first()
        movie_title = show.movie.title if show and show.movie else "Unknown Movie"
        theater_name = show.theater.name if show and show.theater else "Unknown Theater"
        show_date = show.date if show else ""
        show_time = show.time if show else ""

        # QR payload formatting
        qr_payload = f"BOOKING:{booking.id}|MOVIE:{movie_title}|SHOW:{show_date} {show_time}|SEATS:{','.join(booking.seat_codes)}"

        return {
            "booking_id": booking.id,
            "status": booking.status,
            "show_id": booking.show_id,
            "movie": movie_title,
            "theater": theater_name,
            "show_date": show_date,
            "show_time": show_time,
            "seats": booking.seat_codes,
            "total_price": booking.total_price,
            "user_name": booking.user_name,
            "created_at": booking.created_at,
            "qr_data": qr_payload
        }
