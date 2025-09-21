# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"
    debug: bool = False

    database_url: str

    # Polling and timeout configurations
    http_timeout_seconds: float = 5.0
    poll_concurrency: int = 10
    poll_interval_seconds: int = 60
    poll_timeout_seconds: int = 20
    slow_threshold_ms: int = 2000

    # JWT authentication settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
