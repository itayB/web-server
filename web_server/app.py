import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from web_server.handlers.example_handler import ExampleHandler
from web_server.routers.health import router as health_router
from web_server.routers.example import router as example_router
from web_server.settings import Settings
from web_server.routers.health import readiness_event

logger = logging.getLogger(__name__)


def create_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.example_handler = ExampleHandler(settings=settings)
        readiness_event.set()
        logger.info(f"Starting web server on {settings.host}:{settings.port}...")
        yield
        readiness_event.clear()
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
    app.include_router(health_router)
    app.include_router(example_router)

    return app
