import logging
from typing import cast
from fastapi import Request, HTTPException

from web_server.models import QueueEntry, SURGERY_TYPE
from web_server.services.doctor_service import DoctorService
from web_server.services.scheduler_service import SchedulerService
from web_server.settings import Settings
from web_server.types.operating_room import (
    OperationRegistrationStruct,
    OperationRequestStruct,
)


logger = logging.getLogger(__name__)


class SchedulerHandler:
    def __init__(
        self,
        settings: Settings,
        doctor_service: DoctorService,
        scheduler_service: SchedulerService,
        *args,
        **kwargs,
    ):
        self.settings = settings
        self.doctor_service = doctor_service
        self.scheduler_service = scheduler_service
        logger.info("Scheduler handler init successfully")

    def request_operation(
        self, doctor_id: str
    ) -> OperationRegistrationStruct | OperationRequestStruct:
        try:
            specialty = self.doctor_service.get_specialty(doctor_id)
            logger.info(
                f"Doctor {doctor_id} requested operation (specialty: {specialty})"
            )

            result = self.scheduler_service.request_operation(
                doctor_id, cast(SURGERY_TYPE, specialty)
            )

            if isinstance(result, QueueEntry):
                queue_response: OperationRequestStruct = {
                    "queue_number": result.queue_position,
                    "request_id": result.request_id,
                }
                logger.info(
                    f"Doctor {doctor_id} added to queue at position {result.queue_position}"
                )
                return queue_response
            else:
                room, start_time = result
                scheduled_response: OperationRegistrationStruct = {
                    "room_id": room.id,
                    "scheduled_time": start_time.isoformat(),
                }
                logger.info(
                    f"Doctor {doctor_id} scheduled in room {room.id} at {start_time}"
                )
                return scheduled_response

        except Exception as e:
            logger.error(
                f"Error processing operation request for doctor {doctor_id}: {e}"
            )
            raise HTTPException(status_code=400, detail=str(e))


def get_scheduler_handler(request: Request) -> SchedulerHandler:
    scheduler_handler: SchedulerHandler = request.app.state.scheduler_handler
    return scheduler_handler
