from fastapi import status


def test_example(client):
    response = client.get("/v1/api/example/hello/World")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "success"
    assert "message" in response_data
    assert response_data["message"] == "Hello, World!"
