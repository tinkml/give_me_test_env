from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["local", "dev", "prod"] = "local"

    channels_config_path: str = "config/channels.yml"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "stands-bot-postgres"
    postgres_port: int = 5432

    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 0.0

    elastic_apm_server_url: str | None = None
    elastic_apm_service_name: str = "stands-bot"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
