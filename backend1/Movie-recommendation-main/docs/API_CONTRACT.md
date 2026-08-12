# CineMate AI - Frontend API Contract Specification

This document provides complete specification for all REST API endpoints exposed by the CineMate AI backend. Frontend developers can integrate directly using this document.

Base URL: `http://localhost:8000`

---

## 1. System Health

### `GET /health`
- **Purpose**: Check server status and API availability.
- **Request**: None
- **Response**: `200 OK`
```json
{
  "status": "ok",
  "app": "CineMate AI",
  "version": "1.0.0"
}
```

---

## 2. Movie Catalog

### `GET /movies`
- **Purpose**: Query catalog of movies with optional filters.
- **Query Parameters**:
  - `genre` (string, optional): e.g. `"Comedy"`
  - `language` (string, optional): e.g. `"English"`, `"Tamil"`, `"Hindi"`
  - `max_runtime` (int, optional): e.g. `120`
  - `min_rating` (float, optional): e.g. `8.0`
  - `mood` (string, optional): e.g. `"funny"`, `"exciting"`
- **Response**: `200 OK` (Array of Movie objects)
```json
[
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
  }
]
```

### `GET /movies/{movie_id}`
- **Purpose**: Retrieve details for a single movie.
- **Path Parameter**: `movie_id` (string, required) - e.g. `"M001"`
- **Response**: `200 OK` or `404 Not Found`
```json
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
}
```

---

## 3. Shows & Theater Schedule

### `GET /movies/{movie_id}/shows`
- **Purpose**: Retrieve showtimes for a specific movie.
- **Path Parameter**: `movie_id` (string, required)
- **Query Parameters**:
  - `date` (string, optional): `YYYY-MM-DD` (e.g. `"2026-08-12"`)
  - `min_time` (string, optional): `HH:MM` (e.g. `"20:00"`)
  - `max_price` (int, optional): e.g. `500`
  - `format` (string, optional): `"2D"` or `"IMAX"`
  - `theater_id` (string, optional): e.g. `"T001"`
- **Response**: `200 OK`
```json
[
  {
    "id": "S001",
    "movie_id": "M001",
    "theater_id": "T001",
    "date": "2026-08-12",
    "time": "20:30",
    "format": "IMAX",
    "price": 450,
    "movie": { "id": "M001", "title": "The Last Adventure", "rating": 8.2 },
    "theater": { "id": "T001", "name": "PVR Phoenix Marketcity", "location": "Velachery, Chennai", "distance_km": 4.5 }
  }
]
```

### `GET /shows/{show_id}/seats`
- **Purpose**: Retrieve full seat map and availability for a show.
- **Path Parameter**: `show_id` (string, required) - e.g. `"S001"`
- **Response**: `200 OK`
```json
[
  {
    "id": "S001-A1",
    "show_id": "S001",
    "row": "A",
    "number": 1,
    "seat_code": "A1",
    "type": "Standard",
    "status": "available",
    "price": 450
  }
]
```

---

## 4. AI Recommendation Endpoints

### `POST /ai/recommend`
- **Purpose**: Parse natural-language user prompt, filter DB, score movies, and generate natural-language explanation.
- **Request Body**:
```json
{
  "message": "I'm going with 4 friends tonight. Something funny, under 2 hours, after 8 PM, under ₹500."
}
```
- **Response**: `200 OK`
```json
{
  "intent": {
    "genres": ["Comedy"],
    "moods": ["funny"],
    "max_runtime": 120,
    "min_time": "20:00",
    "max_price": 500,
    "group_size": 5
  },
  "recommendations": [
    {
      "movie_id": "M001",
      "movie": { "id": "M001", "title": "The Last Adventure", "rating": 8.2 },
      "match_score": 94.0,
      "reasons": ["Matches genre: Comedy", "Runtime (118 mins) is within your limit (120 mins)"]
    }
  ],
  "explanation": "I highly recommend 'The Last Adventure'! Matches genre: Comedy and requested mood: funny with a strong rating of 8.2/10."
}
```

### `POST /ai/show-recommendation`
- **Purpose**: Recommend top show for a movie based on preferences.
- **Request Body**:
```json
{
  "movie_id": "M001",
  "preferences": {
    "date": "2026-08-12",
    "min_time": "20:00",
    "max_price": 500
  }
}
```

### `POST /ai/seat-recommendation`
- **Purpose**: Deterministically recommend best contiguous group seats.
- **Request Body**:
```json
{
  "show_id": "S001",
  "group_size": 2,
  "preference": "best_view"
}
```

---

## 5. Conversational Assistant

### `POST /chat`
- **Purpose**: Unified multi-turn conversational session endpoint.
- **Request Body**:
```json
{
  "message": "I'll take the first one",
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```
- **Response**: `200 OK`
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "intent": "SELECT_MOVIE",
  "reply": "Selected 'The Last Adventure'! Let's find showtimes for you.",
  "data": {
    "movie_id": "M001",
    "title": "The Last Adventure"
  }
}
```

---

## 6. Booking & Payments

### `POST /bookings`
- **Purpose**: Create a movie ticket booking with atomic seat reservation.
- **Request Body**:
```json
{
  "show_id": "S001",
  "seat_ids": ["S001-D5", "S001-D6"],
  "user_name": "John Doe"
}
```
- **Response**: `201 Created`
```json
{
  "booking_id": "CM48291",
  "status": "confirmed",
  "show_id": "S001",
  "movie": "The Last Adventure",
  "theater": "PVR Phoenix Marketcity",
  "show_date": "2026-08-12",
  "show_time": "20:30",
  "seats": ["D5", "D6"],
  "total_price": 900,
  "user_name": "John Doe",
  "created_at": "2026-08-12T10:55:00.000Z",
  "qr_data": "BOOKING:CM48291|MOVIE:The Last Adventure|SHOW:2026-08-12 20:30|SEATS:D5,D6"
}
```
- **Errors**:
  - `400 Bad Request`: Seats already booked, invalid seats, or duplicate seat IDs.
  - `404 Not Found`: Show not found.

### `GET /bookings/{booking_id}`
- **Purpose**: Retrieve ticket information for rendering digital ticket & QR code.

### `POST /payments/mock`
- **Purpose**: Process mock payment for a booking ID.
- **Request Body**: `{"booking_id": "CM48291"}`
- **Response**: `{"status": "success", "transaction_id": "TX123456", "booking_id": "CM48291"}`
