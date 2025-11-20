from fastapi import status


def test_first_doctor_on_empty_hospital(client):
    response = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": "heart_surgeon_1"}
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "room_id" in response_data and "scheduled_time" in response_data


def test_same_doctor_cannot_be_scheduled_in_the_same_time_slot(client):
    doctor_id = "heart_surgeon_1"
    response1 = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": doctor_id}
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    assert "room_id" in data1 and "scheduled_time" in data1
    first_scheduled_time = data1["scheduled_time"]

    # Immediate second request should get a different time slot (not overlapping)
    response2 = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": doctor_id}
    )
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert "room_id" in data2 and "scheduled_time" in data2
    second_scheduled_time = data2["scheduled_time"]

    # Verify they have different scheduled times
    assert (
        first_scheduled_time != second_scheduled_time
    ), "Doctor should not be scheduled at the same time in two rooms"


def test_different_doctors_can_book_overlapping_times(client):
    response1 = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": "heart_surgeon_1"}
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    first_scheduled_time = data1["scheduled_time"]

    response2 = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": "heart_surgeon_2"}
    )
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    second_scheduled_time = data2["scheduled_time"]
    assert "room_id" in data1
    assert "room_id" in data2
    # Verify they have same scheduled times (given the 5 rooms available)
    assert (
        first_scheduled_time == second_scheduled_time
    ), "Doctor should not be scheduled at the same time in two rooms"
