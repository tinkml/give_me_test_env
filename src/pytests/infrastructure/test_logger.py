import logging

import structlog

from src.infrastructure.logger import configure_logging


def test_configure_logging_uses_console_renderer_for_local_environment() -> None:
    configure_logging("local")

    handler = logging.getLogger().handlers[0]
    assert isinstance(handler.formatter.processors[-1], structlog.dev.ConsoleRenderer)


def test_configure_logging_uses_json_renderer_for_prod_environment() -> None:
    configure_logging("prod")

    handler = logging.getLogger().handlers[0]
    assert isinstance(handler.formatter.processors[-1], structlog.processors.JSONRenderer)
