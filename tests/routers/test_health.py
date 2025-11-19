from fastapi import status
from web_server.routers.health import readiness_event


def test_liveness(client):
    response = client.get("/v1/api/health-check/liveness")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "success"


def test_readiness(client):
    response = client.get("/v1/api/health-check/readiness")
    assert response.status_code == status.HTTP_200_OK


def test_readiness_not_ready(client):
    readiness_event.clear()
    response = client.get("/v1/api/health-check/readiness")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "server is not ready"
    readiness_event.set()
