from typing import Annotated
from fastapi import APIRouter, status
from fastapi.params import Depends

from web_server.handlers.scheduler_handler import (
    SchedulerHandler,
    get_scheduler_handler,
)
from web_server.types.operating_room import (
    OperationRegistrationBody,
    OperationRegistrationStruct,
    OperationRequestStruct,
)


router = APIRouter(
    prefix="/v1/api/operation-room",
    tags=["operation-room"],
)


@router.post(
    "/register",
    summary="request an operation room for a surgery",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=OperationRegistrationStruct | OperationRequestStruct,
)
async def post_register(
    scheduler_handler: Annotated[SchedulerHandler, Depends(get_scheduler_handler)],
    body: OperationRegistrationBody,
) -> OperationRegistrationStruct | OperationRequestStruct:
    return scheduler_handler.request_operation(body.doctor_id)
