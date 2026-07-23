from unittest.mock import patch

from src.infrastructure.config import Settings
from src.infrastructure.sentry import configure_sentry


def _settings(**overrides: str) -> Settings:
    defaults: dict[str, str] = {
        "postgres_user": "test_user",
        "postgres_password": "test_password",
        "postgres_db": "test_db",
    }
    return Settings(_env_file=None, **{**defaults, **overrides})


def test_configure_sentry_skips_init_when_dsn_is_empty() -> None:
    with patch("src.infrastructure.sentry.sentry_sdk.init") as mock_init:
        configure_sentry(_settings())

    mock_init.assert_not_called()


def test_configure_sentry_initializes_when_dsn_is_set() -> None:
    settings = _settings(
        sentry_dsn="https://example@sentry.io/1",
        environment="prod",
        sentry_traces_sample_rate="0.2",
    )

    with patch("src.infrastructure.sentry.sentry_sdk.init") as mock_init:
        configure_sentry(settings)

    mock_init.assert_called_once_with(
        dsn="https://example@sentry.io/1",
        environment="prod",
        traces_sample_rate=0.2,
    )
