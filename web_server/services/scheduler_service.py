import asyncio
import logging
import uuid
from datetime import datetime, timedelta

from web_server.models import (
    OperationRoom,
    QueueEntry,
    ScheduledOperation,
    SurgeryRequirements,
    HEART_SURGERY_REQUIREMENTS,
    BRAIN_SURGERY_REQUIREMENTS,
    SURGERY_TYPE,
)
from web_server.settings import Settings


logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        self._settings = settings
        # Initialize the 5 operating rooms with their specific equipment
        self.operating_rooms: dict[int, OperationRoom] = {
            1: OperationRoom(id=1, machines=["MRI", "CT", "ECG"]),
            2: OperationRoom(id=2, machines=["CT", "MRI"]),
            3: OperationRoom(id=3, machines=["CT", "MRI"]),
            4: OperationRoom(id=4, machines=["MRI", "ECG"]),
            5: OperationRoom(id=5, machines=["MRI", "ECG"]),
        }
        # Store scheduled operations
        self.scheduled_operations: list[ScheduledOperation] = []
        # Queue for requests when no slots available
        self.operation_queue: list[QueueEntry] = []
        # Working hours configuration
        self.work_start_hour = 10  # 10:00
        self.work_end_hour = 18  # 18:00
        self.max_schedule_days = 7  # 1 week ahead
        logger.info(f"Initialized {len(self.operating_rooms)} operating rooms")

    @property
    def settings(self) -> Settings:
        return self._settings

    def get_surgery_requirements(
        self, surgery_type: SURGERY_TYPE
    ) -> SurgeryRequirements:
        """Get the requirements for a specific surgery type."""
        if surgery_type == "heart":
            return HEART_SURGERY_REQUIREMENTS
        elif surgery_type == "brain":
            return BRAIN_SURGERY_REQUIREMENTS
        else:
            raise ValueError(f"Unknown surgery type: {surgery_type}")

    def get_compatible_rooms(self, surgery_type: SURGERY_TYPE) -> list[OperationRoom]:
        """Get all rooms compatible with a specific surgery type."""
        requirements = self.get_surgery_requirements(surgery_type)
        return [
            room
            for room in self.operating_rooms.values()
            if requirements.is_room_compatible(room)
        ]

    def get_surgery_duration(
        self, surgery_type: SURGERY_TYPE, room: OperationRoom
    ) -> int:
        """Calculate surgery duration for a specific surgery type in a specific room."""
        requirements = self.get_surgery_requirements(surgery_type)
        return requirements.get_duration(room)

    def is_within_working_hours(self, start_time: datetime, end_time: datetime) -> bool:
        """Check if a time slot is within working hours (10:00-18:00)."""
        if start_time.hour < self.work_start_hour:
            return False
        if end_time.hour > self.work_end_hour:
            return False
        if end_time.hour == self.work_end_hour and end_time.minute > 0:
            return False
        return True

    def get_room_operations(self, room_id: int) -> list[ScheduledOperation]:
        """Get all scheduled operations for a specific room."""
        return [op for op in self.scheduled_operations if op.room_id == room_id]

    def is_room_available(
        self, room_id: int, start_time: datetime, end_time: datetime
    ) -> bool:
        room_operations = self.get_room_operations(room_id)
        proposed_operation = ScheduledOperation(
            doctor_id="temp",
            room_id=room_id,
            surgery_type="heart",
            start_time=start_time,
            end_time=end_time,
        )
        return not any(proposed_operation.overlaps_with(op) for op in room_operations)

    def find_next_available_slot(
        self,
        room: OperationRoom,
        surgery_type: SURGERY_TYPE,
        from_time: datetime | None = None,
    ) -> datetime | None:
        """Find the next available time slot for a surgery in a specific room."""
        if from_time is None:
            from_time = datetime.now()

        duration_hours = self.get_surgery_duration(surgery_type, room)
        max_end_date = from_time + timedelta(days=self.max_schedule_days)

        # Start searching from the next possible slot (round up to next hour during working hours)
        current_time = from_time.replace(minute=0, second=0, microsecond=0)
        if current_time < from_time:
            current_time += timedelta(hours=1)

        # Ensure we start at or after work hours
        if current_time.hour < self.work_start_hour:
            current_time = current_time.replace(hour=self.work_start_hour)
        elif current_time.hour >= self.work_end_hour:
            # Move to next day's start
            current_time = (current_time + timedelta(days=1)).replace(
                hour=self.work_start_hour
            )

        while current_time < max_end_date:
            end_time = current_time + timedelta(hours=duration_hours)

            # Check if within working hours
            if self.is_within_working_hours(current_time, end_time):
                # Check if room is available
                if self.is_room_available(room.id, current_time, end_time):
                    return current_time

            # Try next hour
            current_time += timedelta(hours=1)

            # Skip to next day if we've passed working hours
            if current_time.hour >= self.work_end_hour:
                current_time = (current_time + timedelta(days=1)).replace(
                    hour=self.work_start_hour
                )

        return None  # No available slot in the next week

    def schedule_operation(
        self, doctor_id: str, surgery_type: SURGERY_TYPE
    ) -> tuple[OperationRoom, datetime] | None:
        compatible_rooms = self.get_compatible_rooms(surgery_type)

        if not compatible_rooms:
            logger.error(f"No compatible rooms found for surgery type: {surgery_type}")
            return None

        # Find the earliest available slot across all compatible rooms
        best_slot: tuple[OperationRoom, datetime] | None = None
        earliest_time: datetime | None = None

        for room in compatible_rooms:
            slot_time = self.find_next_available_slot(room, surgery_type)
            if slot_time and (earliest_time is None or slot_time < earliest_time):
                earliest_time = slot_time
                best_slot = (room, slot_time)

        if best_slot is None:
            logger.warning(
                f"No available slots in the next {self.max_schedule_days} days"
            )
            return None

        # Schedule the operation
        room, start_time = best_slot
        duration_hours = self.get_surgery_duration(surgery_type, room)
        end_time = start_time + timedelta(hours=duration_hours)

        scheduled_op = ScheduledOperation(
            doctor_id=doctor_id,
            room_id=room.id,
            surgery_type=surgery_type,
            start_time=start_time,
            end_time=end_time,
        )
        self.scheduled_operations.append(scheduled_op)
        logger.info(
            f"Scheduled {surgery_type} surgery for doctor {doctor_id} in room {room.id} "
            f"from {start_time} to {end_time}"
        )

        return best_slot

    def add_to_queue(self, doctor_id: str, surgery_type: SURGERY_TYPE) -> QueueEntry:
        # Add a request to the queue (when no slots are available).
        request_id = str(uuid.uuid4())
        queue_position = len(self.operation_queue) + 1

        queue_entry = QueueEntry(
            request_id=request_id,
            doctor_id=doctor_id,
            surgery_type=surgery_type,
            timestamp=datetime.now(),
            queue_position=queue_position,
        )

        self.operation_queue.append(queue_entry)
        logger.info(
            f"Added {surgery_type} surgery request for doctor {doctor_id} to queue "
            f"at position {queue_position} (request_id: {request_id})"
        )

        return queue_entry

    def process_queue(self) -> list[tuple[QueueEntry, OperationRoom, datetime]]:
        """Process the queue and schedule any requests that now have available slots.

        Returns a list of tuples containing (queue_entry, room, start_time) for successfully scheduled operations.
        This can be called lazily on new requests or periodically by a background scheduler.
        """
        scheduled_from_queue: list[tuple[QueueEntry, OperationRoom, datetime]] = []
        remaining_queue: list[QueueEntry] = []

        for entry in self.operation_queue:
            # Try to schedule this queued request
            result = self.schedule_operation(entry.doctor_id, entry.surgery_type)

            if result is not None:
                room, start_time = result
                scheduled_from_queue.append((entry, room, start_time))
                logger.info(
                    f"Dequeued and scheduled request {entry.request_id} for doctor {entry.doctor_id} "
                    f"in room {room.id} at {start_time}"
                )
            else:
                # Still no slot available, keep in queue
                remaining_queue.append(entry)

        # Update queue with only the remaining entries and recalculate positions
        self.operation_queue = remaining_queue
        for idx, entry in enumerate(self.operation_queue, start=1):
            entry.queue_position = idx

        if scheduled_from_queue:
            logger.info(
                f"Processed queue: {len(scheduled_from_queue)} requests scheduled, {len(remaining_queue)} remain"
            )

        return scheduled_from_queue

    def request_operation(
        self, doctor_id: str, surgery_type: SURGERY_TYPE
    ) -> tuple[OperationRoom, datetime] | QueueEntry:
        """Main entry point: Request an operation slot.

        Returns either:
        - (room, start_time) if successfully scheduled
        - QueueEntry if no slots available and added to queue
        """
        # First, try to process any pending queue entries (lazy dequeue)
        self.process_queue()

        # Try to schedule the new request
        result = self.schedule_operation(doctor_id, surgery_type)

        if result is not None:
            # Successfully scheduled
            return result
        else:
            # No slots available, add to queue
            return self.add_to_queue(doctor_id, surgery_type)


async def periodic_queue_processor(
    scheduler_service: SchedulerService, interval_seconds: int
) -> None:
    logger.info(f"Starting background queue processor (interval: {interval_seconds}s)")

    while True:
        try:
            if len(scheduler_service.operation_queue) > 0:
                result = scheduler_service.process_queue()
                if result:
                    logger.info(
                        f"Background queue processing: scheduled {len(result):,} operations, "
                        f"{len(scheduler_service.operation_queue):,} remain in queue"
                    )
            logger.info("Background queue processor sleeping...")
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Queue processor shutting down gracefully")
            raise
        except Exception:
            logger.exception("Error in background queue processor")
