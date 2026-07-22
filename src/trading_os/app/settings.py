from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Environment = Environment.DEVELOPMENT
    live_mode_requested: bool = False
    database_url: str = "postgresql+asyncpg://trading:trading@localhost:5432/trading"
    valkey_url: str = "redis://localhost:6379/0"
    kite_api_key: SecretStr | None = None
    kite_access_token: SecretStr | None = None
    alpaca_api_key: SecretStr | None = None
    alpaca_secret_key: SecretStr | None = None
    alpaca_paper: bool = True
