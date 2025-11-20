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


def test_same_doctor_for_more_than_a_week(client):
    # Test that scheduling a doctor for all available slots in a week eventually results in a queue.
    doctor_id = "heart_surgeon_1"
    scheduled_operations = []
    queue_response = None

    # Keep requesting operations until we get a queue response
    # Working hours are 10:00-18:00, heart surgery takes 3 hours
    # So maximum ~2 operations per day * 7 days = ~14 operations per week
    max_attempts = 50  # limit to avoid infinite loop

    for i in range(max_attempts):
        response = client.post(
            "/v1/api/operation-room/register", json={"doctor_id": doctor_id}
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Request {i+1} failed with status {response.status_code}"
        data = response.json()

        if "queue_number" in data:
            queue_response = data
            break
        else:
            assert "room_id" in data
            assert "scheduled_time" in data
            assert "estimated_time" in data
            scheduled_operations.append(data)

    # Assert that we eventually got a queue response
    assert (
        queue_response is not None
    ), "Expected to receive a queue response after filling the week"

    # Verify queue response properties
    assert "queue_number" in queue_response
    assert "request_id" in queue_response
    assert queue_response["queue_number"] > 0
    assert isinstance(queue_response["request_id"], str)

    # Verify we scheduled multiple operations before hitting the queue
    assert (
        len(scheduled_operations) > 13
    ), "Should have scheduled at least one operation before queue"

    # Verify all scheduled operations have valid data
    scheduled_times = []
    for op in scheduled_operations:
        assert op["room_id"] > 0
        assert op["estimated_time"] == 3  # Heart surgery takes 3 hours
        scheduled_times.append(op["scheduled_time"])

    # Verify all scheduled times are unique (no double-booking of the same doctor)
    assert len(scheduled_times) == len(
        set(scheduled_times)
    ), "Doctor should not be double-booked at the same time"


def test_invalid_doctor_id(client):
    doctor_id = "non_existent_doctor"
    response = client.post(
        "/v1/api/operation-room/register", json={"doctor_id": doctor_id}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert data["detail"] == f"Doctor with id '{doctor_id}' not found"
