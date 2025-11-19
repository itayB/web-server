from unittest.mock import patch, MagicMock
from web_server.__main__ import main
from web_server.settings import Settings


def test_main():
    with patch("web_server.__main__.create_app") as mock_create_app, patch(
        "web_server.__main__.run"
    ) as mock_run:
        settings = Settings()
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        main()
        mock_run.assert_called_once_with(
            mock_app,
            host=settings.host,
            port=settings.port,
            timeout_graceful_shutdown=settings.timeout_graceful_shutdown,
            access_log=False,
        )


def test_init():
    from web_server import __main__

    with patch.object(__main__, "main", return_value=51):
        with patch.object(__main__, "__name__", "__main__"):
            with patch.object(__main__.sys, "exit") as mock_exit:
                __main__.init()
                assert mock_exit.call_args[0][0] == 51
