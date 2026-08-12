def test_get_shows_for_movie(client):
    response = client.get("/movies/M001/shows")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for show in data:
        assert show["movie_id"] == "M001"

def test_get_shows_with_time_filter(client):
    response = client.get("/movies/M001/shows?min_time=20:00")
    assert response.status_code == 200
    data = response.json()
    for show in data:
        assert show["time"] >= "20:00"

def test_get_seats_for_show(client):
    response = client.get("/shows/S001/seats")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 60
    # Check structure
    sample = data[0]
    assert "row" in sample
    assert "number" in sample
    assert "status" in sample
    assert sample["status"] in ["available", "booked"]
