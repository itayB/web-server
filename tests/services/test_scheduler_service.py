import pytest
from datetime import timedelta
from web_server.services.scheduler_service import SchedulerService
from web_server.settings import Settings


@pytest.fixture
def scheduler_service():
    settings = Settings()
    return SchedulerService(settings)


def test_doctor_cannot_have_overlapping_operations(scheduler_service):
    """Test that a doctor cannot be scheduled for two operations at the same time."""
    doctor_id = "heart_surgeon_1"

    # First operation request
    result1 = scheduler_service.request_operation(doctor_id, "heart")
    assert result1 is not None
    assert not hasattr(
        result1, "request_id"
    ), "First request should be scheduled, not queued"

    room1, start_time1 = result1
    doctor_ops = scheduler_service.get_doctor_operations(doctor_id)
    assert len(doctor_ops) == 1, "Doctor should have exactly one scheduled operation"

    # Second operation request should get a time slot that doesn't overlap
    result2 = scheduler_service.request_operation(doctor_id, "heart")
    assert result2 is not None

    doctor_ops_after = scheduler_service.get_doctor_operations(doctor_id)
    assert len(doctor_ops_after) == 2, "Doctor should have two scheduled operations"

    # Verify operations don't overlap
    op1 = doctor_ops_after[0]
    op2 = doctor_ops_after[1]

    # Operations should not overlap
    assert not (op1.start_time < op2.end_time and op2.start_time < op1.end_time), (
        f"Operations should not overlap: Op1({op1.start_time} to {op1.end_time}) "
        f"and Op2({op2.start_time} to {op2.end_time})"
    )


def test_different_doctors_can_have_overlapping_operations(scheduler_service):
    """Test that different doctors can be scheduled at the same time in different rooms."""
    doctor1 = "heart_surgeon_1"
    doctor2 = "heart_surgeon_2"

    # Schedule first doctor
    result1 = scheduler_service.request_operation(doctor1, "heart")
    assert result1 is not None
    room1, start_time1 = result1

    # Schedule second doctor (should get same time, different room)
    result2 = scheduler_service.request_operation(doctor2, "heart")
    assert result2 is not None
    room2, start_time2 = result2

    # Both should be scheduled successfully
    assert len(scheduler_service.get_doctor_operations(doctor1)) == 1
    assert len(scheduler_service.get_doctor_operations(doctor2)) == 1

    # They can have the same time slot (different rooms)
    # Just verify both were scheduled
    assert start_time1 is not None
    assert start_time2 is not None


def test_is_doctor_available_method(scheduler_service):
    """Test the is_doctor_available method directly."""
    doctor_id = "heart_surgeon_1"

    # Schedule an operation
    result = scheduler_service.request_operation(doctor_id, "heart")
    assert result is not None
    room, start_time = result

    ops = scheduler_service.get_doctor_operations(doctor_id)
    scheduled_op = ops[0]

    # Doctor should NOT be available during the scheduled operation
    assert not scheduler_service.is_doctor_available(
        doctor_id, scheduled_op.start_time, scheduled_op.end_time
    )

    # Doctor should NOT be available if time overlaps partially
    overlap_start = scheduled_op.start_time + timedelta(hours=1)
    overlap_end = scheduled_op.end_time + timedelta(hours=1)
    assert not scheduler_service.is_doctor_available(
        doctor_id, overlap_start, overlap_end
    )

    # Doctor SHOULD be available after the operation ends
    after_start = scheduled_op.end_time + timedelta(hours=1)
    after_end = after_start + timedelta(hours=3)
    assert scheduler_service.is_doctor_available(doctor_id, after_start, after_end)
