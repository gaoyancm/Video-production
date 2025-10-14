"""Basic smoke tests for the API."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_healthcheck_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
