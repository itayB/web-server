from typing import Literal
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

    surgery_type: SURGERY_TYPE
    is_occupied: bool = False
