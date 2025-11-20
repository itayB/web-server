import logging
from fastapi import Request
from web_server.services.doctor_service import DoctorService
from web_server.settings import Settings


logger = logging.getLogger(__name__)


class SchedulerHandler:
    def __init__(
        self,
        settings: Settings,
        doctor_service: DoctorService,
        *args,
        **kwargs,
    ):
        self.settings = settings
        self.doctor_service = doctor_service
        logger.info("scheduler handler init successfully")

    def schedule(self, doctor_id: str) -> str:
        specialty = self.doctor_service.get_specialty(doctor_id)
        message = f"Hello, {doctor_id} - special in {specialty}!"
        logger.info(message)
        return message


def get_scheduler_handler(request: Request) -> SchedulerHandler:
    scheduler_handler: SchedulerHandler = request.app.state.scheduler_handler
    return scheduler_handler
