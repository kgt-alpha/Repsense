from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RepSense API"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    database_url: str = (
        "postgresql+psycopg://repsense:repsense_dev_password@localhost:5432/repsense"
    )
    jwt_secret_key: str = "development-only-change-this-secret"
    access_token_expire_minutes: int = 30
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    redis_url: str = "redis://localhost:6379/0"
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
