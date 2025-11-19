from typing import Literal
from typing_extensions import TypedDict


STATUS = Literal["success", "error", "partial", "unknown"]

class ReturnHealthCheckStruct(TypedDict):
    status: STATUS
