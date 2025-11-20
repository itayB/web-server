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
        # Temporary in-memory database of doctors
        self.db = {
            f"heart_surgeon_{i}": Doctor(id=i, name=f"Doctor {i}", specialty="heart")
            for i in range(1, 3)
        } | {
            f"brain_surgeon_{i}": Doctor(id=i, name=f"Doctor {i}", specialty="brain")
            for i in range(4, 6)
        }
        logger.info("doctor service init successfully")

    def get_doctor(self, doctor_id: str) -> Doctor:
        doctor = self.db.get(doctor_id)
        if doctor is None:
            logger.warning(f"Doctor with id '{doctor_id}' not found")
            raise Exception(f"Doctor with id '{doctor_id}' not found")
        return doctor

    def get_specialty(self, doctor_id: str) -> str:
        return self.get_doctor(doctor_id).specialty
