from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    stands_bot_webhook_token: str
    stand_names: str
    database_url: str

    @property
    def stand_name_list(self) -> list[str]:
        return [name.strip() for name in self.stand_names.split(",") if name.strip()]
