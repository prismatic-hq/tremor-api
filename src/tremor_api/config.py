from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

DB_SCHEMA = "tremor"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"
    port: int = 5432
    name: str = "prismatic"
    user: str = "prismatic"
    password: SecretStr

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
        )


class StewardSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STEWARD_")

    url: str = "http://steward-api:8000"
    timeout_seconds: float = 2.0
