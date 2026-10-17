from app.models import Hero


def test_create_hero_hides_secret_name(client):
    response = client.post(
        "/api/v1/heroes",
        json={"name": "Deadpond", "secret_name": "Dive Wilson"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Deadpond"
    assert "secret_name" not in response.json()
    assert response.json()["status"] == "active"


def test_list_and_read_hero(client):
    created = client.post(
        "/api/v1/heroes/",
        json={"name": "Tony", "secret_name": "Iron Man", "age": 45},
    ).json()

    response = client.get("/api/v1/heroes")
    detail = client.get(f"/api/v1/heroes/{created['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert detail.status_code == 200
    assert detail.json()["id"] == created["id"]


def test_read_missing_hero_returns_404(client):
    response = client.get("/api/v1/heroes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Hero not found"


def test_partial_update_preserves_other_fields(client):
    created = client.post(
        "/api/v1/heroes",
        json={"name": "Tony", "secret_name": "Iron Man", "age": 45},
    ).json()

    response = client.patch(
        f"/api/v1/heroes/{created['id']}",
        json={"status": "retired"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "retired"
    assert response.json()["age"] == 45


def test_invalid_age_returns_422(client):
    response = client.post(
        "/api/v1/heroes",
        json={"name": "Young", "secret_name": "Y", "age": -5},
    )

    assert response.status_code == 422


def test_unknown_team_returns_400(client):
    response = client.post(
        "/api/v1/heroes",
        json={"name": "A", "secret_name": "a", "team_id": 999},
    )

    assert response.status_code == 400


def test_delete_hero(client, session):
    hero = Hero(name="Tony", secret_name="Iron Man")
    session.add(hero)
    session.commit()
    session.refresh(hero)

    response = client.delete(f"/api/v1/heroes/{hero.id}")

    assert response.status_code == 204
