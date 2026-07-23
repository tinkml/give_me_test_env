from unittest.mock import patch

from fastapi import FastAPI

from src.infrastructure.apm import configure_apm
from src.infrastructure.config import Settings


def _settings(**overrides: str) -> Settings:
    defaults: dict[str, str] = {
        "postgres_user": "test_user",
        "postgres_password": "test_password",
        "postgres_db": "test_db",
    }
    return Settings(_env_file=None, **{**defaults, **overrides})


def test_configure_apm_skips_when_server_url_is_empty() -> None:
    app = FastAPI()

    with patch("src.infrastructure.apm.Client") as mock_client:
        configure_apm(app, _settings())

    mock_client.assert_not_called()
    assert not any(m.cls.__name__ == "ElasticAPM" for m in app.user_middleware)


def test_configure_apm_adds_middleware_when_server_url_is_set() -> None:
    app = FastAPI()
    settings = _settings(
        elastic_apm_server_url="http://apm-server:8200",
        elastic_apm_service_name="stands-bot",
        environment="prod",
    )

    with patch("src.infrastructure.apm.Client") as mock_client:
        configure_apm(app, settings)

    mock_client.assert_called_once_with(
        {
            "SERVICE_NAME": "stands-bot",
            "SERVER_URL": "http://apm-server:8200",
            "ENVIRONMENT": "prod",
        }
    )
    assert any(m.cls.__name__ == "ElasticAPM" for m in app.user_middleware)
