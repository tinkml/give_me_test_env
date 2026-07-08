import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.presentation.di import get_dispatcher, get_settings
from src.presentation.routes import router
from src.application.dispatcher import CommandDispatcher
from src.infrastructure.config import Settings


class _StubCommand:
    def __init__(self, response: str) -> None:
        self._response = response

    async def execute(self, user_name: str, argument: str) -> str:
        return self._response


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_settings] = lambda: Settings(
        stands_bot_webhook_token="valid-token", stand_names="akb1"
    )
    app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher(
        {"!list": _StubCommand("1. akb1 — Свободен")}
    )
    return TestClient(app)


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

    client.app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher(
        {"!list": _FailingCommand()}
    )

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
