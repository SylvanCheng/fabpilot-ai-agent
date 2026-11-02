"""Settings base and application-wide settings.

Each module owns its own settings class (cohesion: config lives next to the code that uses it);
they all inherit `EnvSettings` so every value comes from env vars / `.env`, never from code.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(EnvSettings):
    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    # Comma-separated origins allowed to call the API from a browser.
    cors_origins: str = "http://localhost:5080"
    # Application DB (agent-owned data: conversations, audit, RAG). Shared infrastructure;
    # each module that stores data owns its own tables in it.
    app_db_url: str = "postgresql+psycopg://fabpilot_app:fabpilot_app@localhost:5432/fabpilot_app"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()
