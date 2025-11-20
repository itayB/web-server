import logging

from web_server.settings import Settings


logger = logging.getLogger(__name__)


class ExampleService:
    def __init__(
        self,
        settings: Settings,
        *args,
        **kwargs,
    ):
        self._settings = settings

    @property
    def settings(self) -> Settings:
        return self._settings

    async def close(self):
        # TODO: close any connections or cleanup resources if needed
        pass
