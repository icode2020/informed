from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_exposes_unconfigured_auth() -> None:
    response = client.get("/v1/status")
    assert response.status_code == 200
    assert response.json()["authentication"] == "not_configured"


def test_sensitive_profile_fails_closed() -> None:
    response = client.post("/v1/profiles", json={"interests": [{"topic_id": "test"}]})
    assert response.status_code == 501
