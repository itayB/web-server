import logging
from fastapi import Request
from web_server.settings import Settings


logger = logging.getLogger(__name__)


class ExampleHandler:
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        # TODO: save future services as a member variables
        self.settings = settings
        logger.info("example handler init successfully")

    def handle(self, name: str) -> str:
        return f"Hello, {name}!"


def get_example_handler(request: Request) -> ExampleHandler:
    example_handler: ExampleHandler = request.app.state.example_handler
    return example_handler
