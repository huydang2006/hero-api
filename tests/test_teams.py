def test_create_duplicate_team_returns_409(client):
    body = {"name": "Avengers", "headquarters": "New York"}

    first = client.post("/api/v1/teams", json=body)
    second = client.post("/api/v1/teams", json=body)

    assert first.status_code == 201
    assert second.status_code == 409


def test_team_heroes_endpoint(client):
    team = client.post(
        "/api/v1/teams",
        json={"name": "Avengers", "headquarters": "New York"},
    ).json()
    client.post(
        "/api/v1/heroes",
        json={
            "name": "Tony",
            "secret_name": "Iron Man",
            "team_id": team["id"],
        },
    )

    response = client.get(f"/api/v1/teams/{team['id']}/heroes")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Tony"


def test_missing_team_heroes_returns_404(client):
    response = client.get("/api/v1/teams/999/heroes")

    assert response.status_code == 404
