import logging

from web_server.models import OperationRoom
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
