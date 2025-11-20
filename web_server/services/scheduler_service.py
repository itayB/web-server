import logging

from web_server.models import (
    OperationRoom,
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
        logger.info(f"Initialized {len(self.operating_rooms)} operating rooms")

    @property
    def settings(self) -> Settings:
        return self._settings

    def get_operating_room(self, room_id: int) -> OperationRoom | None:
        return self.operating_rooms.get(room_id)

    def get_all_operating_rooms(self) -> list[OperationRoom]:
        return list(self.operating_rooms.values())

    def get_rooms_with_machine(self, machine: str) -> list[OperationRoom]:
        return [
            room
            for room in self.operating_rooms.values()
            if room.has_machine(machine)  # type: ignore
        ]

    def get_surgery_requirements(self, surgery_type: SURGERY_TYPE) -> SurgeryRequirements:
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

    def get_surgery_duration(self, surgery_type: SURGERY_TYPE, room: OperationRoom) -> int:
        """Calculate surgery duration for a specific surgery type in a specific room."""
        requirements = self.get_surgery_requirements(surgery_type)
        return requirements.get_duration(room)
