from typing import Annotated
from fastapi import APIRouter, status
from fastapi.params import Depends

from web_server.handlers.example_handler import ExampleHandler, get_example_handler


router = APIRouter(
    prefix="/v1/api/example",
    tags=["example"],
)


@router.get(
    "/hello/{name}",
    summary="Example request",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
)
async def get_example(
    example_handler: Annotated[ExampleHandler, Depends(get_example_handler)],
    name: str,
):
    greeting = example_handler.handle(name)
    return {
        "status": "success",
        "message": greeting,
    }
