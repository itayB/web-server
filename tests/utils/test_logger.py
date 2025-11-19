import logging
from web_server.utils.logger import init_logger

logger = logging.getLogger(__name__)


def test_error_log(caplog):
    init_logger()
    with caplog.at_level("ERROR"):
        logger.error("This is an error message")
        assert "This is an error message" in caplog.text
