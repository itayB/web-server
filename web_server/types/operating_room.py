from pydantic import BaseModel
from typing_extensions import TypedDict


class OperationRegistrationStruct(TypedDict):
    room_id: int
    estimated_time: int  # duration in hours


class OperationRequestStruct(TypedDict):
    queue_number: int
    request_id: str  # ?


class OperationRegistrationBody(BaseModel):
    doctor_id: (
        str  # TODO: security concern, change to jwt token later and pass from header
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "doctor_id": "heart_surgeon_1",
                },
            ]
        }
    }
