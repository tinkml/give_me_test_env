import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dispatcher import CommandDispatcher
from src.domain.exceptions import StandNotFoundError
from src.infrastructure.channels import ChannelConfig, ChannelsRegistry
from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base, StandModel
from src.presentation.di import get_channels_registry, get_db_session, get_dispatcher
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.routes import router


class _StubCommand:
    def __init__(self, response: str) -> None:
        self._response = response

    async def execute(self, user_name: str, argument: str) -> str:
        return self._response


def _webhook_data(**overrides: str) -> dict[str, str]:
    data = {
        "token": "valid-token",
        "channel_id": "chan1",
        "user_name": "alice",
        "text": "!list",
        "trigger_word": "!list",
    }
    return {**data, **overrides}


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_channels_registry] = lambda: ChannelsRegistry.build(
        [ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"])],
        {"WEBHOOK_TOKEN_AKB": "valid-token"},
    )
    app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher(
        {"!list": _StubCommand("1. akb1 — Свободен")}
    )
    return TestClient(app, raise_server_exceptions=False)


def test_webhook_returns_command_result_for_valid_token(client: TestClient) -> None:
    response = client.post("/webhook", data=_webhook_data())

    assert response.status_code == 200
    assert response.json() == {"text": "1. akb1 — Свободен"}


def test_webhook_rejects_invalid_token(client: TestClient) -> None:
    response = client.post("/webhook", data=_webhook_data(token="wrong-token"))

    assert response.status_code == 401


def test_webhook_passes_text_after_trigger_word_as_argument(client: TestClient) -> None:
    response = client.post("/webhook", data=_webhook_data(text="!list ignored-argument"))

    assert response.status_code == 200


def test_webhook_returns_friendly_message_and_200_when_command_raises(
    client: TestClient,
) -> None:
    class _FailingCommand:
        async def execute(self, user_name: str, argument: str) -> str:
            raise RuntimeError("db is down")

    client.app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher({"!list": _FailingCommand()})

    response = client.post("/webhook", data=_webhook_data())

    assert response.status_code == 200
    assert response.json() == {"text": "Внутренняя ошибка, попробуйте позже"}


def test_webhook_returns_stand_not_found_message(client: TestClient) -> None:
    class _NotFoundCommand:
        async def execute(self, user_name: str, argument: str) -> str:
            raise StandNotFoundError("akb1")

    client.app.dependency_overrides[get_dispatcher] = lambda: CommandDispatcher({"!take": _NotFoundCommand()})

    response = client.post("/webhook", data=_webhook_data(text="!take akb1", trigger_word="!take"))

    assert response.status_code == 200
    assert response.json() == {"text": "Стенд не найден: akb1"}


def test_webhook_logs_received_request_and_successful_dispatch(client: TestClient) -> None:
    with structlog.testing.capture_logs() as logs:
        client.post("/webhook", data=_webhook_data())

    events = [entry["event"] for entry in logs]
    assert "webhook_received" in events
    assert "command_dispatched" in events


def test_webhook_returns_unknown_trigger_word_message(client: TestClient) -> None:
    response = client.post("/webhook", data=_webhook_data(text="!unknown", trigger_word="!unknown"))

    assert response.status_code == 200
    assert response.json() == {"text": "Неизвестное триггер-слово: !unknown"}


@pytest.fixture
def multi_team_client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_channels_registry] = lambda: ChannelsRegistry.build(
        [
            ChannelConfig(team="akb", token_env="WEBHOOK_TOKEN_AKB", stands=["akb1"]),
            ChannelConfig(team="sl", token_env="WEBHOOK_TOKEN_SL", stands=["dev-1"]),
        ],
        {"WEBHOOK_TOKEN_AKB": "akb-token", "WEBHOOK_TOKEN_SL": "sl-token"},
    )

    engine = get_engine("sqlite+aiosqlite:///:memory:")
    session_factory = get_session_factory(engine)

    async def override_get_db_session() -> AsyncSession:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            session.add(StandModel(name="akb1", status="free", team="akb"))
            session.add(StandModel(name="dev-1", status="free", team="sl"))
            await session.commit()
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    return TestClient(app, raise_server_exceptions=False)


def test_webhook_with_team_token_only_sees_its_own_teams_stands(multi_team_client: TestClient) -> None:
    response = multi_team_client.post(
        "/webhook", data=_webhook_data(token="akb-token", text="--list", trigger_word="--list")
    )

    assert response.status_code == 200
    assert "akb1" in response.json()["text"]
    assert "dev-1" not in response.json()["text"]


def test_webhook_with_other_team_token_sees_only_that_teams_stands(multi_team_client: TestClient) -> None:
    response = multi_team_client.post(
        "/webhook", data=_webhook_data(token="sl-token", text="--list", trigger_word="--list")
    )

    assert response.status_code == 200
    assert "dev-1" in response.json()["text"]
    assert "akb1" not in response.json()["text"]


def test_webhook_cannot_take_a_stand_belonging_to_another_team(multi_team_client: TestClient) -> None:
    response = multi_team_client.post(
        "/webhook", data=_webhook_data(token="akb-token", text="--take dev-1", trigger_word="--take")
    )

    assert response.status_code == 200
    assert "не найден" in response.json()["text"]
