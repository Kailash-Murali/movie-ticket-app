import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.ai.intent_extractor import extract_intent
from app.algorithms.movie_scoring import rank_movies
from app.algorithms.show_scoring import rank_shows
from app.algorithms.seat_recommendation import recommend_seats_for_show
from app.services.movie_service import MovieService
from app.services.show_service import ShowService
from app.services.seat_service import SeatService
from app.services.booking_service import BookingService
from app.ai.recommendation_explainer import (
    generate_movie_explanation,
    generate_show_explanation,
    generate_seat_explanation
)

# In-memory session store
SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: Optional[str] = None) -> Dict[str, Any]:
    if not session_id or session_id not in SESSIONS:
        session_id = session_id or str(uuid.uuid4())
        SESSIONS[session_id] = {
            "session_id": session_id,
            "selected_movie_id": None,
            "selected_show_id": None,
            "selected_seats": [],
            "group_size": 1,
            "user_intent": None
        }
    return SESSIONS[session_id]

def process_chat_message(db: Session, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    session = get_or_create_session(session_id)
    sid = session["session_id"]
    lower = message.lower()

    # Determine intent
    if any(k in lower for k in ["book", "confirm booking", "pay", "buy ticket"]):
        intent_type = "BOOK_TICKETS"
    elif any(k in lower for k in ["seat", "seats", "where to sit", "best view", "aisle"]):
        intent_type = "RECOMMEND_SEATS"
    elif any(k in lower for k in ["show", "showtime", "time", "when"]):
        intent_type = "FIND_SHOW"
    elif any(k in lower for k in ["take the first", "select movie", "first one", "second one", "option 1", "option 2", "i'll take"]):
        intent_type = "SELECT_MOVIE"
    elif any(k in lower for k in ["help", "what can you do"]):
        intent_type = "GENERAL_HELP"
    else:
        intent_type = "DISCOVER_MOVIE"

    # Execute intent logic
    if intent_type == "DISCOVER_MOVIE":
        prev_intent_dict = session.get("user_intent")
        from app.schemas.intent import UserIntent
        prev_intent = UserIntent(**prev_intent_dict) if prev_intent_dict else None

        user_intent = extract_intent(message, previous_intent=prev_intent)
        session["user_intent"] = user_intent.model_dump()
        session["group_size"] = user_intent.group_size or 1

        movies = MovieService.get_movies(
            db, 
            genre=user_intent.genres[0] if user_intent.genres else None,
            language=user_intent.language,
            max_runtime=user_intent.max_runtime,
            min_rating=user_intent.min_rating
        )
        if not movies:
            movies = MovieService.get_movies(db)

        ranked = rank_movies(movies, user_intent, top_k=3)
        if ranked:
            session["selected_movie_id"] = ranked[0]["movie"].id

        formatted_recs = [
            {
                "movie_id": item["movie"].id,
                "title": item["movie"].title,
                "genre": item["movie"].genre,
                "rating": item["movie"].rating,
                "runtime": item["movie"].runtime,
                "match_score": item["score"],
                "reasons": item["reasons"]
            }
            for item in ranked
        ]

        explanation = generate_movie_explanation(message, user_intent, ranked)
        return {
            "session_id": sid,
            "intent": "DISCOVER_MOVIE",
            "reply": explanation,
            "data": {
                "user_intent": user_intent.model_dump(),
                "recommendations": formatted_recs
            }
        }

    elif intent_type == "SELECT_MOVIE":
        # Handle "first one", "second one", etc.
        movie_id = session.get("selected_movie_id") or "M001"
        movie = MovieService.get_movie_by_id(db, movie_id)
        if movie:
            session["selected_movie_id"] = movie.id
            return {
                "session_id": sid,
                "intent": "SELECT_MOVIE",
                "reply": f"Selected '{movie.title}'! Let's find showtimes for you.",
                "data": {"movie_id": movie.id, "title": movie.title}
            }

    elif intent_type == "FIND_SHOW":
        movie_id = session.get("selected_movie_id") or "M001"
        user_intent_dict = session.get("user_intent") or {}
        from app.schemas.intent import UserIntent
        user_intent = UserIntent(**user_intent_dict) if user_intent_dict else extract_intent(message)

        shows = ShowService.get_shows(db, movie_id=movie_id, date=user_intent.date)
        if not shows:
            shows = ShowService.get_shows(db, movie_id=movie_id)

        ranked = rank_shows(shows, user_intent, group_size=session.get("group_size", 1))
        if ranked["recommended_show"]:
            rec_show = ranked["recommended_show"]["show"]
            session["selected_show_id"] = rec_show.id
            explanation = generate_show_explanation(ranked["recommended_show"])
            return {
                "session_id": sid,
                "intent": "FIND_SHOW",
                "reply": explanation,
                "data": {
                    "recommended_show": {
                        "show_id": rec_show.id,
                        "movie_id": rec_show.movie_id,
                        "theater": rec_show.theater.name if rec_show.theater else "",
                        "time": rec_show.time,
                        "format": rec_show.format,
                        "price": rec_show.price
                    }
                }
            }

    elif intent_type == "RECOMMEND_SEATS":
        show_id = session.get("selected_show_id") or "S001"
        # Extract group size or seat preference from message if provided
        intent_from_msg = extract_intent(message)
        if intent_from_msg.group_size and intent_from_msg.group_size > 1:
            session["group_size"] = intent_from_msg.group_size
        
        group_size = session.get("group_size", 2)
        seat_pref = intent_from_msg.seat_preference or "best_view"

        seats = SeatService.get_seats_by_show(db, show_id)
        rec_res = recommend_seats_for_show(seats, group_size=group_size, preference=seat_pref)

        session["selected_seats"] = rec_res["recommended_seat_ids"]
        explanation = generate_seat_explanation(rec_res["recommended_seats"], rec_res["reason"], rec_res["total_price"])

        return {
            "session_id": sid,
            "intent": "RECOMMEND_SEATS",
            "reply": explanation,
            "data": rec_res
        }

    elif intent_type == "BOOK_TICKETS":
        show_id = session.get("selected_show_id") or "S001"
        seat_ids = session.get("selected_seats")

        if not seat_ids:
            seats = SeatService.get_seats_by_show(db, show_id)
            rec_res = recommend_seats_for_show(seats, group_size=session.get("group_size", 2))
            seat_ids = rec_res["recommended_seat_ids"]

        booking = BookingService.create_booking(db, show_id=show_id, seat_ids=seat_ids)
        ticket_details = BookingService.get_booking_by_id(db, booking.id)

        return {
            "session_id": sid,
            "intent": "BOOK_TICKETS",
            "reply": f"🎉 Booking Confirmed! Your Booking ID is {booking.id}. Total: ₹{booking.total_price}.",
            "data": ticket_details
        }

    return {
        "session_id": sid,
        "intent": "GENERAL_HELP",
        "reply": "Hi! I am CineMate AI. Tell me what kind of movie you're looking for!",
        "data": {}
    }
