import logging
import sys

from uvicorn.config import LOGGING_CONFIG

from web_server.settings import Settings


def init_logger():
    settings = Settings()
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.setFormatter(
        Formatter(
            fmt="%(asctime)-15s %(process)-2s %(thread)d %(levelname)-18.18s %(message)s [%(filename)s:%(lineno)d]"
        )
    )
    logging.root.addHandler(log_handler)
    logging.root.setLevel(settings.log_severity)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    LOGGING_CONFIG["loggers"]["uvicorn"]["level"] = "WARN"
    LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] = "WARN"
    LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] = "WARN"


class Formatter(logging.Formatter):
    @classmethod
    def _get_level_color(cls, levelno):
        default = "\033[0m"
        return {
            logging.DEBUG: "\033[0;96m",
            logging.INFO: "\033[0;92m",
            logging.WARNING: "\033[0;33m",
            logging.WARN: "\033[0;33m",
            logging.ERROR: "\033[0;31m",
        }.get(levelno, default)

    def format(self, record):
        record.levelname = (
            f"{self._get_level_color(record.levelno)}{record.levelname}\033[0m"
        )
        return super().format(record)
