import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from web_server.handlers.example_handler import ExampleHandler
from web_server.handlers.scheduler_handler import SchedulerHandler
from web_server.routers.operation_room import router as operation_room_router
from web_server.routers.health import router as health_router
from web_server.routers.example import router as example_router
from web_server.services.doctor_service import DoctorService
from web_server.services.scheduler_service import (
    SchedulerService,
    periodic_queue_processor,
)
from web_server.settings import Settings
from web_server.routers.health import readiness_event

logger = logging.getLogger(__name__)


def create_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Initializing application lifespan...")
        app.state.settings = settings
        app.state.example_handler = ExampleHandler(settings=settings)
        doctor_service = DoctorService(settings=settings)
        scheduler_service = SchedulerService(settings=settings)
        app.state.scheduler_handler = SchedulerHandler(
            settings, doctor_service, scheduler_service
        )

        # Start background queue processor if enabled
        queue_processor_task = None
        if settings.enable_background_queue_processor:
            queue_processor_task = asyncio.create_task(
                periodic_queue_processor(
                    scheduler_service, settings.queue_processor_interval_seconds
                )
            )
            logger.info("Background queue processor started")

        readiness_event.set()
        logger.info(f"Starting web server on {settings.host}:{settings.port}...")

        yield
        readiness_event.clear()

        # Cleanup: cancel background tasks if running
        if queue_processor_task is not None:
            logger.info("Stopping background queue processor...")
            queue_processor_task.cancel()
            try:
                await queue_processor_task
            except asyncio.CancelledError:
                logger.info("Background queue processor stopped")

        logger.warning("Preparing for shutdown - waiting for in flight requests")
        await asyncio.sleep(0.1)
        logger.warning("Closing server - bye bye")

    return lifespan


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Web Server",
        version=settings.app_version,
        lifespan=create_lifespan(settings),
    )
    app.add_middleware(GZipMiddleware, minimum_size=settings.compression_min_size)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.allow_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(operation_room_router)
    app.include_router(health_router)
    app.include_router(example_router)

    return app
