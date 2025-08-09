# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"
    debug: bool
    database_url: str
    poll_interval_seconds: int = 60
    poll_timeout_seconds: int = 20
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    slow_threshold_ms: int = 2000
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_pass: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
