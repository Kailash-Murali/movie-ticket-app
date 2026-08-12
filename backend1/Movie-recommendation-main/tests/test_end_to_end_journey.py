def test_complete_end_to_end_user_journey(client):
    # Step 1: User sends natural-language prompt to chat
    chat_resp1 = client.post("/chat", json={"message": "I want something funny tonight after 8 for 2 people under ₹500"})
    assert chat_resp1.status_code == 200
    res1 = chat_resp1.json()
    assert res1["intent"] == "DISCOVER_MOVIE"
    session_id = res1["session_id"]
    recommendations = res1["data"]["recommendations"]
    assert len(recommendations) > 0
    selected_movie_id = recommendations[0]["movie_id"]

    # Step 2: User selects movie
    chat_resp2 = client.post("/chat", json={"message": "I'll take the first one", "session_id": session_id})
    assert chat_resp2.status_code == 200
    res2 = chat_resp2.json()
    assert res2["intent"] == "SELECT_MOVIE"
    assert res2["data"]["movie_id"] == selected_movie_id

    # Step 3: User asks for best show
    chat_resp3 = client.post("/chat", json={"message": "What is the best show?", "session_id": session_id})
    assert chat_resp3.status_code == 200
    res3 = chat_resp3.json()
    assert res3["intent"] == "FIND_SHOW"
    selected_show_id = res3["data"]["recommended_show"]["show_id"]

    # Step 4: User asks for best seats for two
    chat_resp4 = client.post("/chat", json={"message": "Best seats for two near center", "session_id": session_id})
    assert chat_resp4.status_code == 200
    res4 = chat_resp4.json()
    assert res4["intent"] == "RECOMMEND_SEATS"
    recommended_seats = res4["data"]["recommended_seats"]
    assert len(recommended_seats) == 2

    # Step 5: User confirms booking
    chat_resp5 = client.post("/chat", json={"message": "Book them", "session_id": session_id})
    assert chat_resp5.status_code == 200
    res5 = chat_resp5.json()
    assert res5["intent"] == "BOOK_TICKETS"
    booking_id = res5["data"]["booking_id"]
    assert booking_id.startswith("CM")

    # Step 6: Process mock payment for the generated booking
    pay_resp = client.post("/payments/mock", json={"booking_id": booking_id})
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "success"
    assert "TX" in pay_resp.json()["transaction_id"]

    # Step 7: Retrieve ticket info and QR metadata
    ticket_resp = client.get(f"/bookings/{booking_id}")
    assert ticket_resp.status_code == 200
    ticket_data = ticket_resp.json()
    assert ticket_data["booking_id"] == booking_id
    assert ticket_data["status"] == "confirmed"
    assert ticket_data["qr_data"] is not None
    assert booking_id in ticket_data["qr_data"]
