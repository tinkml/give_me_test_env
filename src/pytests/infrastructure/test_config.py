import pytest
from pydantic import ValidationError

from src.infrastructure.config import Settings


def _settings(**overrides: str) -> Settings:
    defaults: dict[str, str] = {
        "stands_bot_webhook_token": "secret",
        "stand_names": "akb1",
        "postgres_user": "test_user",
        "postgres_password": "test_password",
        "postgres_db": "test_db",
    }
    return Settings(_env_file=None, **{**defaults, **overrides})


def test_stand_name_list_splits_and_strips_comma_separated_names() -> None:
    settings = _settings(stand_names=" akb1, slplay4 ,slplay7")

    assert settings.stand_name_list == ["akb1", "slplay4", "slplay7"]


def test_postgres_credentials_are_required() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, stands_bot_webhook_token="secret", stand_names="akb1")


def test_database_url_is_built_from_postgres_parts() -> None:
    settings = _settings(
        postgres_user="bob",
        postgres_password="hunter2",
        postgres_db="stands",
        postgres_host="db-host",
        postgres_port="6543",
    )

    assert settings.database_url == "postgresql+psycopg://bob:hunter2@db-host:6543/stands"


def test_postgres_host_and_port_have_docker_compose_defaults() -> None:
    settings = _settings()

    assert settings.postgres_host == "stands-bot-postgres"
    assert settings.postgres_port == 5432


def test_environment_defaults_to_local() -> None:
    settings = _settings()

    assert settings.environment == "local"


def test_sentry_and_apm_are_disabled_by_default() -> None:
    settings = _settings()

    assert settings.sentry_dsn is None
    assert settings.elastic_apm_server_url is None
