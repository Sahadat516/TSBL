from __future__ import annotations

import warnings
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TSBL Marketplace"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    allowed_hosts: list[str] = ["*"]

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tsbl"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    password_bcrypt_rounds: int = 12

    cors_origins: list[str] = ["http://localhost:3000"]

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@tsbl.com"
    smtp_use_tls: bool = True

    sentry_dsn: str = ""

    encryption_key: str = "change-this-in-production"

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    mfa_enabled: bool = True
    max_login_attempts: int = 5
    login_lockout_minutes: int = 30

    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10

    def check_production_defaults(self) -> None:
        if self.environment == "production":
            if self.jwt_secret_key == "change-this-in-production":
                warnings.warn("jwt_secret_key is still set to default value", RuntimeWarning)
            if self.encryption_key == "change-this-in-production":
                warnings.warn("encryption_key is still set to default value", RuntimeWarning)
            if self.debug:
                warnings.warn("debug mode is enabled in production", RuntimeWarning)


settings = Settings()
settings.check_production_defaults()
