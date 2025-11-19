import pytest

from web_server.settings import Settings


def test_gzip_compression_skipped(client):
    response = client.get(
        "/v1/api/health-check/liveness", headers={"Accept-Encoding": "gzip"}
    )
    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") != "gzip"


@pytest.mark.settings(Settings(compression_min_size=10))
def test_gzip_compression_enabled(client):
    response = client.get(
        "/v1/api/health-check/liveness", headers={"Accept-Encoding": "gzip"}
    )
    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") == "gzip"
