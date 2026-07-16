import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infrastructure.db import get_engine, get_session_factory
from src.infrastructure.models import Base
from src.presentation.di import get_db_session
from src.presentation.health import router


@pytest.fixture
def app() -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)
    return fastapi_app


def test_liveness_always_returns_ok(app: FastAPI) -> None:
    client = TestClient(app)

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_returns_ok_when_database_reachable(app: FastAPI) -> None:
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = get_session_factory(engine)

    async def override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_session
    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_503_when_database_unreachable(app: FastAPI) -> None:
    class _BrokenSession:
        async def execute(self, *_args, **_kwargs):
            raise ConnectionError("db unreachable")

    async def override_session():
        yield _BrokenSession()

    app.dependency_overrides[get_db_session] = override_session
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
