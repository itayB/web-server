from typing import Annotated
from fastapi import APIRouter, status
from fastapi.params import Depends

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
    # example_handler: Annotated[ExampleHandler, Depends(get_example_handler)],
    body: OperationRegistrationBody,
) -> OperationRegistrationStruct | OperationRequestStruct:
    body.doctor_id
    # TODO: implement the logic to register an operation room
    return {
        "room_id": 1,
        "estimated_time": 2,
    }
