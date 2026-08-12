# AI Movie Ticket Booking Assistant 🎬

An AI-powered movie ticket booking system that uses **Gemini** for natural-language preference extraction and **deterministic algorithms** for constraint-aware group consensus recommendations.

## Architecture

```
Streamlit ──► FastAPI ──┬──► Gemini LLM (preference extraction)
                        │       └──► Pydantic validation
                        ├──► Recommendation engine
                        │       ├──► Hard constraint filtering
                        │       ├──► Satisfaction scoring
                        │       └──► Group consensus ranking
                        ├──► Seat recommendation engine
                        └──► JSON data persistence
```

## Key Features

- **Natural Language Input**: Group members describe preferences in plain language
- **Hard vs Soft Classification**: AI separates "must have" constraints from "nice to have" preferences
- **Constraint-Aware Filtering**: Any show violating any member's hard constraint is rejected
- **Fair Consensus**: Lexicographic max-min ranking maximizes the least-satisfied member's score
- **Seat Recommendation**: Finds best contiguous block for the group based on center proximity and row preference
- **Mock Booking**: Complete booking flow with seat state persistence

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Gemini 3.5 Flash Lite |
| Validation | Pydantic |
| Storage | Local JSON files |
| Language | Python |

## Project Structure

```
movie-assistant/
├── frontend/
│   └── app.py              # Streamlit UI
├── backend/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Pydantic data models
│   ├── llm_service.py       # Gemini preference extraction
│   ├── recommendation.py    # Hard filtering + satisfaction scoring
│   ├── consensus.py         # Group consensus ranking
│   ├── seats.py             # Seat recommendation algorithm
│   └── booking.py           # Booking persistence
├── data/
│   ├── movies.json          # 8 seed movies
│   ├── shows.json           # 16 shows across 2 cinemas
│   └── bookings.json        # Booking records
├── tests/
│   └── test_core.py         # Unit tests (no LLM)
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd movie-assistant
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Run the Backend

```bash
cd movie-assistant
uvicorn backend.main:app --reload --port 8000
```

### 4. Run the Frontend (in a separate terminal)

```bash
cd movie-assistant
streamlit run frontend/app.py
```

### 5. Run Tests

```bash
cd movie-assistant
python -m pytest tests/test_core.py -v
```

## API Endpoints

### POST /recommend

Send group preferences and get ranked movie recommendations.

```json
{
  "members": [
    "I want a Hindi comedy after 7",
    "No horror and under 500",
    "We need good seats together"
  ]
}
```

### GET /shows/{show_id}/seats?group_size=3

Returns seat map with recommended contiguous block.

### POST /book

Book specific seats for a show.

```json
{
  "show_id": "s3",
  "seats": ["C4", "C5", "C6"]
}
```

## Scoring Formula

```
score = genre_score × 0.35
      + language_score × 0.25
      + runtime_score × 0.15
      + time_score × 0.15
      + rating_score × 0.10
```

## Consensus Algorithm

Rank by `(minimum_score, average_score)` descending:
1. Maximize satisfaction of the least-satisfied member
2. Break ties by maximizing average group satisfaction
