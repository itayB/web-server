import sys
from uvicorn import run
from web_server.app import create_app
from web_server.settings import Settings
from web_server.utils.logger import init_logger


def main():
    init_logger()
    settings = Settings()
    app = create_app(settings)
    run(
        app,
        host=settings.host,
        port=settings.port,
        timeout_graceful_shutdown=settings.timeout_graceful_shutdown,
        access_log=False,
    )


def init():
    if __name__ == "__main__":
        sys.exit(main())


init()
