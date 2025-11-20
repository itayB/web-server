from fastapi import status


def test_first_doctor_on_empty_hospital(client):
    response = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": "heart_surgeon_1"}
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "room_id" in response_data and "scheduled_time" in response_data
