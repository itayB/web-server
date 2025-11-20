from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_severity: str = Field(default="INFO", description="Logger severity")
    app_version: str = Field(default="0.1.0", description="Application version")
    host: str = Field(default="0.0.0.0", description="Listen address")
    port: int = Field(default=8080, description="Listen port")
    timeout_graceful_shutdown: int = Field(
        default=30, description="time in seconds graceful before shutdown"
    )
    allow_origin: str = Field(default="*", description="CORS allow origin")
    compression_min_size: int = Field(
        default=1000,
        description="Minimum response size in bytes to enable gzip compression",
    )
    # Operating Room Scheduler settings
    enable_background_queue_processor: bool = Field(
        default=True, description="Enable background queue processing"
    )
    queue_processor_interval_seconds: int = Field(
        default=60, description="Interval in seconds for background queue processing"
    )
