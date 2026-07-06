import pytest
from pydantic import ValidationError

from src.infrastructure.config import Settings


def test_stand_name_list_splits_and_strips_comma_separated_names() -> None:
    settings = Settings(
        _env_file=None,
        stands_bot_webhook_token="secret",
        stand_names=" akb1, slplay4 ,slplay7",
        database_url="sqlite:///:memory:",
    )

    assert settings.stand_name_list == ["akb1", "slplay4", "slplay7"]


def test_database_url_is_required() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, stands_bot_webhook_token="secret", stand_names="akb1")
