from fastapi.testclient import TestClient

from race_engineer.api import app


def test_dashboard_is_available() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Race Engineer AI" in response.text

