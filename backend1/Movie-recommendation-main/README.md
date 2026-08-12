# CineMate AI: AI-Powered Movie Ticket Booking Assistant Backend

CineMate AI is a complete backend and AI system for an intelligent movie ticket booking assistant. It transforms natural-language requests into structured movie recommendations, optimal showtime selections, group seat placements, and ticket bookings.

---

## 1. Architecture Overview

CineMate AI strictly adheres to the principle of:
- **Database (PostgreSQL / SQLite)** = Source of truth for availability, pricing, and records.
- **Backend Algorithms** = Deterministic filtering, weighted movie scoring, showtime ranking, and group seat placement.
- **LLM (Configurable Provider)** = Natural-language understanding, intent extraction, and factual explanations.

```
[User Request] 
      │
      ▼
[LLM Intent Extractor] ──► Structured UserIntent (Genres, Runtime, Budget, Time, Seats)
      │
      ▼
[SQLAlchemy DB Query] ──► Filter Candidate Movies / Shows / Seats
      │
      ▼
[Deterministic Algorithms] ──► Weighted Scoring & Seat Layout Placement
      │
      ▼
[LLM Explainer & Chat Orchestrator] ──► Facts-Based Explanation & Digital Ticket
```

---

## 2. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, PostgreSQL / SQLite, Alembic
- **AI Layer**: Configurable LLM Client (Gemini / OpenAI) with deterministic rule fallbacks
- **Testing**: pytest, FastAPI TestClient
- **Environment**: python-dotenv, Pydantic-Settings

---

## 3. Directory Structure

```
Movie-recommendation/
├── app/
│   ├── main.py                   # FastAPI entrypoint, middleware, health check
│   ├── core/
│   │   ├── config.py             # Settings (Pydantic-Settings & .env)
│   ├── database/
│   │   ├── connection.py         # SQLAlchemy Engine & Session Local
│   │   └── base.py               # Declarative Base
│   ├── models/
│   │   ├── movie.py              # Movie ORM
│   │   ├── theater.py            # Theater ORM
│   │   ├── show.py               # Show ORM
│   │   ├── seat.py               # Seat ORM
│   │   └── booking.py            # Booking & BookingSeat ORM
│   ├── schemas/
│   │   ├── movie.py              # Pydantic schemas
│   │   ├── theater.py
│   │   ├── show.py
│   │   ├── seat.py
│   │   ├── booking.py
│   │   ├── intent.py             # UserIntent schema
│   │   └── recommendation.py     # AI & recommendation response schemas
│   ├── routes/
│   │   ├── movies.py             # GET /movies, GET /movies/{id}
│   │   ├── theaters.py           # GET /theaters, GET /theaters/{id}
│   │   ├── shows.py              # GET /movies/{id}/shows, GET /shows/{id}
│   │   ├── seats.py              # GET /shows/{id}/seats
│   │   ├── bookings.py           # POST /bookings, GET /bookings/{id}
│   │   ├── payments.py           # POST /payments/mock
│   │   ├── ai.py                 # Recommendation endpoints
│   │   └── chat.py               # Conversational orchestrator
│   ├── services/
│   │   ├── movie_service.py
│   │   ├── theater_service.py
│   │   ├── show_service.py
│   │   ├── seat_service.py
│   │   └── booking_service.py
│   ├── algorithms/
│   │   ├── movie_scoring.py      # Weighted movie scoring engine
│   │   ├── seat_recommendation.py# Deterministic group seating algorithm
│   │   └── show_scoring.py       # Showtime & distance ranking engine
│   ├── ai/
│   │   ├── llm_client.py         # Provider client (Gemini / OpenAI / Mock)
│   │   ├── intent_extractor.py   # Intent parser & safe fallback
│   │   ├── recommendation_explainer.py # Facts-only natural language explainer
│   │   └── chat_orchestrator.py  # Session state & dialogue manager
│   └── utils/
│       └── seed.py               # DB seeder from JSON data
├── data/
│   ├── movies.json               # 20 diverse movies dataset
│   ├── theaters.json             # 5 realistic theaters
│   ├── shows.json                # 290+ shows across 3 dates
│   ├── seats.json                # 17,640+ seats generated
│   ├── generate_mock_data.py
│   └── validate_mock_data.py
├── alembic/                      # Alembic migrations
├── tests/                        # 20 Pytest unit & integration tests
├── .env
├── .env.example
├── seed.py                       # Seeder root script
├── requirements.txt
└── README.md
```

---

## 4. Setup Instructions

### Environment & Dependencies

1. Clone or navigate to the repository directory:
```bash
cd Movie-recommendation
```

2. Install dependencies:
```bash
py -3 -m pip install -r requirements.txt
```

3. Configure `.env`:
```env
DATABASE_URL=sqlite:///./cinemate.db
# For PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cinemate_db

LLM_API_KEY=your-gemini-or-openai-key
LLM_MODEL=gemini-1.5-flash
LLM_PROVIDER=gemini
```

---

## 5. Database Seeding & Migration

Run database migrations and seed script:

```bash
# Seed standard database with 20 movies, 5 theaters, 294 shows, 17,640 seats
py -3 seed.py
```

---

## 6. Running the API Server

Start the FastAPI server using Uvicorn:

```bash
py -3 -m uvicorn app.main:app --reload --port 8000
```

- Interactive Swagger API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

## 7. Core Frontend API Contracts

| Endpoint | Method | Description |
|---|---|---|
| `/movies` | GET | Retrieve movies with optional filters (`genre`, `language`, `max_runtime`, `min_rating`, `mood`) |
| `/movies/{id}` | GET | Retrieve single movie details |
| `/movies/{id}/shows` | GET | Retrieve shows for a movie filtered by `date`, `min_time`, `max_price`, `format` |
| `/shows/{id}/seats` | GET | Retrieve full seat map (rows A-F, status, type, price) |
| `/ai/recommend` | POST | Movie recommendation pipeline (intent extraction + scoring + explanation) |
| `/ai/show-recommendation` | POST | Rank best showtime for a movie |
| `/ai/seat-recommendation` | POST | Rank best group seats (view, center, aisle, budget) |
| `/bookings` | POST | Transactional booking with backend price calculation & seat locks |
| `/bookings/{id}` | GET | Retrieve digital ticket and QR payload |
| `/payments/mock` | POST | Process mock payment transaction |
| `/chat` | POST | Conversational multi-turn assistant session endpoint |

---

## 8. Example AI Conversation Flow

```json
// User Prompt: "I'm going with 4 friends tonight. We want something funny, not longer than 2 hours, after 8 PM, and under ₹500 per person."

POST /chat
{
  "message": "I'm going with 4 friends tonight. Something funny, under 2 hours, after 8 PM, under 500"
}

// System Response:
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "intent": "DISCOVER_MOVIE",
  "reply": "I highly recommend 'The Last Adventure'! Matches genre: Comedy and requested mood: funny with a strong rating of 8.2/10.",
  "data": {
    "user_intent": {
      "genres": ["Comedy"],
      "moods": ["funny"],
      "max_runtime": 120,
      "min_time": "20:00",
      "max_price": 500,
      "group_size": 5
    },
    "recommendations": [...]
  }
}
```

---

## 9. Running Tests

Run the complete test suite:

```bash
py -3 -m pytest -v
```

All 20 tests covering movies, shows, seat recommendations, scoring algorithms, transactional bookings, double-booking prevention, intent extraction, and chat orchestration will run and pass.
