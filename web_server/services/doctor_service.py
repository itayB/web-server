import logging

from web_server.models import Doctor
from web_server.settings import Settings


logger = logging.getLogger(__name__)


class DoctorService:
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        self._settings = settings
        self.db = {
            f"doctor_heart_{i}": Doctor(id=i, name=f"Doctor {i}", specialty="heart")
            for i in range(1, 3)
        } | {
            f"doctor_brain_{i}": Doctor(id=i, name=f"Doctor {i}", specialty="brain")
            for i in range(4, 6)
        }

    def get_specialty(self, doctor_id: str) -> str:
        # TODO: handle non existing doctor_id
        return self.db[doctor_id].specialty
