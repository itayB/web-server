import pytest
from fastapi.testclient import TestClient
from web_server.services.scheduler_service import SchedulerService
from web_server.settings import Settings
from web_server.app import create_app


@pytest.fixture
def client(request):
    marker = request.node.get_closest_marker("settings")
    if marker is None:
        settings = Settings()
    else:
        settings = marker.args[0]
    app = create_app(settings)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}


@pytest.fixture
def scheduler_service():
    settings = Settings()
    return SchedulerService(settings)
