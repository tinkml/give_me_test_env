import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.dispatcher import CommandDispatcher
from src.domain.exceptions import StandNotFoundError
from src.infrastructure.config import Settings
from src.presentation.di import get_dispatcher, get_settings
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.routes import router


class _StubCommand:
    def __init__(self, response: str) -> None:
        self._response = response

    async def execute(self, user_name: str, argument: str) -> str:
        return self._response


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_settings] = lambda: Settings(
        stands_bot_webhook_token="valid-token", stand_names="akb1"
    )
    app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher(
        {"!list": _StubCommand("1. akb1 — Свободен")}
    )
    return TestClient(app, raise_server_exceptions=False)


def test_webhook_returns_command_result_for_valid_token(client: TestClient) -> None:
    response = client.post(
        "/webhook",
        data={
            "token": "valid-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!list",
            "trigger_word": "!list",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"text": "1. akb1 — Свободен"}


def test_webhook_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/webhook",
        data={
            "token": "wrong-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!list",
            "trigger_word": "!list",
        },
    )

    assert response.status_code == 401


def test_webhook_passes_text_after_trigger_word_as_argument(client: TestClient) -> None:
    response = client.post(
        "/webhook",
        data={
            "token": "valid-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!list ignored-argument",
            "trigger_word": "!list",
        },
    )

    assert response.status_code == 200


def test_webhook_returns_friendly_message_and_200_when_command_raises(
    client: TestClient,
) -> None:
    class _FailingCommand:
        async def execute(self, user_name: str, argument: str) -> str:
            raise RuntimeError("db is down")

    client.app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher({"!list": _FailingCommand()})

    response = client.post(
        "/webhook",
        data={
            "token": "valid-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!list",
            "trigger_word": "!list",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Внутренняя ошибка, попробуйте позже"}


def test_webhook_returns_stand_not_found_message(client: TestClient) -> None:
    class _NotFoundCommand:
        async def execute(self, user_name: str, argument: str) -> str:
            raise StandNotFoundError("akb1")

    client.app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher({"!take": _NotFoundCommand()})

    response = client.post(
        "/webhook",
        data={
            "token": "valid-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!take akb1",
            "trigger_word": "!take",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Стенд не найден: akb1"}


def test_webhook_logs_received_request_and_successful_dispatch(client: TestClient) -> None:
    with structlog.testing.capture_logs() as logs:
        client.post(
            "/webhook",
            data={
                "token": "valid-token",
                "channel_id": "chan1",
                "user_name": "alice",
                "text": "!list",
                "trigger_word": "!list",
            },
        )

    events = [entry["event"] for entry in logs]
    assert "webhook_received" in events
    assert "command_dispatched" in events


def test_webhook_returns_unknown_trigger_word_message(client: TestClient) -> None:
    response = client.post(
        "/webhook",
        data={
            "token": "valid-token",
            "channel_id": "chan1",
            "user_name": "alice",
            "text": "!unknown",
            "trigger_word": "!unknown",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Неизвестное триггер-слово: !unknown"}
