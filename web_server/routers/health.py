from asyncio import Event
from fastapi import APIRouter, HTTPException, status
from web_server.types.health import ReturnHealthCheckStruct


readiness_event = Event()

router = APIRouter(
    prefix="/v1/api/health-check",
    tags=["health-check"],
)


@router.get(
    "/liveness",
    summary="Perform a Liveness Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ReturnHealthCheckStruct,
)
async def liveness() -> ReturnHealthCheckStruct:
    return {"status": "success"}


@router.get(
    "/readiness",
    summary="Perform a Readiness Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=ReturnHealthCheckStruct,
)
async def readiness() -> ReturnHealthCheckStruct:
    if not readiness_event.is_set():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server is not ready",
        )
    return {"status": "success"}
