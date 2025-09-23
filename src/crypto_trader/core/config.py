from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    database_url: AnyUrl | str = "postgresql+asyncpg://trader:trader@localhost:5432/trader"
    redis_url: AnyUrl | str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8080

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
