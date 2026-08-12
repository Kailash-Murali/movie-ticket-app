def test_ai_movie_recommendation_endpoint(client):
    payload = {"message": "I'm going with 4 friends tonight. Something funny, under 2 hours, after 8 PM, under ₹500."}
    response = client.post("/ai/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert "explanation" in data
    assert data["intent"]["max_runtime"] == 120

def test_ai_show_recommendation_endpoint(client):
    payload = {"movie_id": "M001"}
    response = client.post("/ai/show-recommendation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_show"] is not None
    assert "explanation" in data

def test_ai_seat_recommendation_endpoint(client):
    payload = {"show_id": "S001", "group_size": 2, "preference": "best_view"}
    response = client.post("/ai/seat-recommendation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_seats"]) == 2
    assert data["score"] > 0

def test_chat_conversational_flow(client):
    # Step 1: Discover movies
    resp1 = client.post("/chat", json={"message": "Funny movie tonight after 8"})
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["intent"] == "DISCOVER_MOVIE"
    session_id = d1["session_id"]

    # Step 2: Recommend seats
    resp2 = client.post("/chat", json={"message": "Find best seats for 2 people", "session_id": session_id})
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["intent"] == "RECOMMEND_SEATS"

    # Step 3: Book tickets
    resp3 = client.post("/chat", json={"message": "Book them", "session_id": session_id})
    assert resp3.status_code == 200
    d3 = resp3.json()
    assert d3["intent"] == "BOOK_TICKETS"
    assert "booking_id" in d3["data"]
