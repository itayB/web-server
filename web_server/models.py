from typing import Literal
from datetime import datetime
from pydantic import BaseModel, model_validator


SURGERY_TYPE = Literal["heart", "brain"]
MACHINE_TYPE = Literal["MRI", "CT", "ECG"]


class Hospital(BaseModel):
    num_of_operation_rooms: int

    @model_validator(mode="after")
    def positive(self):
        if self.num_of_operation_rooms <= 0:
            raise ValueError("At least one operation room is required.")
        return self


class Doctor(BaseModel):
    id: int
    name: str
    specialty: SURGERY_TYPE


class OperationRoom(BaseModel):
    id: int
    machines: list[MACHINE_TYPE]

    def has_machine(self, machine: MACHINE_TYPE) -> bool:
        return machine in self.machines


class SurgeryRequirements(BaseModel):
    """Requirements and duration logic for each surgery type."""

    surgery_type: SURGERY_TYPE
    required_machines: list[MACHINE_TYPE]
    base_duration_hours: int
    duration_with_optional_machine: dict[MACHINE_TYPE, int] | None = None

    def get_duration(self, room: OperationRoom) -> int:
        """Calculate surgery duration based on available equipment in the room."""
        if self.duration_with_optional_machine:
            for machine, duration in self.duration_with_optional_machine.items():
                if room.has_machine(machine):
                    return duration
        return self.base_duration_hours

    def is_room_compatible(self, room: OperationRoom) -> bool:
        """Check if a room has all required machines for this surgery."""
        return all(room.has_machine(machine) for machine in self.required_machines)


# Surgery type configurations
HEART_SURGERY_REQUIREMENTS = SurgeryRequirements(
    surgery_type="heart",
    required_machines=["ECG"],
    base_duration_hours=3,
)

BRAIN_SURGERY_REQUIREMENTS = SurgeryRequirements(
    surgery_type="brain",
    required_machines=["MRI"],
    base_duration_hours=3,
    duration_with_optional_machine={"CT": 2},  # 2 hours with CT, 3 hours without
)


class ScheduledOperation(BaseModel):
    """Represents a scheduled surgery operation."""

    doctor_id: str
    room_id: int
    surgery_type: SURGERY_TYPE
    start_time: datetime
    end_time: datetime

    def overlaps_with(self, other: "ScheduledOperation") -> bool:
        """Check if this operation overlaps with another operation in the same room."""
        if self.room_id != other.room_id:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time
