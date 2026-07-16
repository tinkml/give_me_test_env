from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infrastructure.metrics import configure_metrics


def test_configure_metrics_exposes_metrics_endpoint() -> None:
    app = FastAPI()
    configure_metrics(app)
    client = TestClient(app)

    client.get("/")  # generate at least one request to instrument
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
