import logging
from fastapi import Request
from web_server.settings import Settings


logger = logging.getLogger(__name__)


class SchedulerHandler:
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        # TODO: save future services as a member variables
        self.settings = settings
        logger.info("scheduler handler init successfully")

    def handle(self, docker_id: str) -> str:
        return f"Hello, {docker_id}!"


def get_scheduler_handler(request: Request) -> SchedulerHandler:
    scheduler_handler: SchedulerHandler = request.app.state.scheduler_handler
    return scheduler_handler
