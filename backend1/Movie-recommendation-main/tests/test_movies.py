def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_all_movies(client):
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20

def test_filter_movies_by_genre(client):
    response = client.get("/movies?genre=Comedy")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for movie in data:
        genres_lower = [g.lower() for g in movie["genre"]]
        assert "comedy" in genres_lower

def test_filter_movies_by_runtime(client):
    response = client.get("/movies?max_runtime=120")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for movie in data:
        assert movie["runtime"] <= 120

def test_get_movie_by_valid_id(client):
    response = client.get("/movies/M001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "M001"
    assert data["title"] == "The Last Adventure"

def test_get_movie_by_invalid_id(client):
    response = client.get("/movies/INVALID_ID")
    assert response.status_code == 404
