from fastapi.testclient import TestClient

from race_engineer.api import app


def test_dashboard_is_available() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Race Engineer AI" in response.text
    assert "Backtest evidence" in response.text


def test_backtest_endpoint_is_documented() -> None:
    schema = TestClient(app).get("/openapi.json").json()
    assert "/evaluation/backtest" in schema["paths"]


def test_cutoff_evaluation_endpoint_is_documented() -> None:
    schema = TestClient(app).get("/openapi.json").json()
    assert "/evaluation/cutoffs" in schema["paths"]
