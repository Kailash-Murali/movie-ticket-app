def test_successful_multiple_seat_booking(client):
    seats_resp = client.get("/shows/S001/seats")
    avail_seats = [s["id"] for s in seats_resp.json() if s["status"] == "available"]
    assert len(avail_seats) >= 2

    booking_seats = avail_seats[:2]
    payload = {"show_id": "S001", "seat_ids": booking_seats, "user_name": "Alice"}
    
    response = client.post("/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["user_name"] == "Alice"
    assert len(data["seats"]) == 2
    assert data["total_price"] > 0

    # Retrieve ticket info
    ticket_resp = client.get(f"/bookings/{data['booking_id']}")
    assert ticket_resp.status_code == 200
    assert ticket_resp.json()["booking_id"] == data["booking_id"]

def test_booking_invalid_show_id(client):
    payload = {"show_id": "INVALID_SHOW", "seat_ids": ["S001-A1"]}
    response = client.post("/bookings", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_booking_invalid_seat_id(client):
    payload = {"show_id": "S001", "seat_ids": ["INVALID_SEAT_ID"]}
    response = client.post("/bookings", json=payload)
    assert response.status_code == 400
    assert "invalid seat" in response.json()["detail"].lower()

def test_booking_seat_belonging_to_another_show(client):
    # Try booking S002's seat for show S001
    payload = {"show_id": "S001", "seat_ids": ["S002-A1"]}
    response = client.post("/bookings", json=payload)
    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"].lower()

def test_booking_already_booked_seat(client):
    seats_resp = client.get("/shows/S003/seats")
    avail_seats = [s["id"] for s in seats_resp.json() if s["status"] == "available"]
    target_seat = [avail_seats[0]]

    # User 1 books seat
    resp1 = client.post("/bookings", json={"show_id": "S003", "seat_ids": target_seat})
    assert resp1.status_code == 201

    # User 2 tries booking the same seat
    resp2 = client.post("/bookings", json={"show_id": "S003", "seat_ids": target_seat})
    assert resp2.status_code == 400
    assert "already booked" in resp2.json()["detail"].lower()

def test_booking_duplicate_seat_ids_in_request(client):
    payload = {"show_id": "S001", "seat_ids": ["S001-A1", "S001-A1"]}
    response = client.post("/bookings", json=payload)
    assert response.status_code == 400
    assert "duplicate" in response.json()["detail"].lower()
