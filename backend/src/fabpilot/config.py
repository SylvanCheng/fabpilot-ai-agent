"""Application settings, loaded from environment variables / `.env`.

Every deployment-specific value (DB URLs, LLM endpoint, model name) lives here so that
switching between Ollama (dev) and vLLM (prod) is a `.env` change, never a code change.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"

    # Read-only business DB (synthetic fab data). The role behind this URL must only have SELECT.
    business_db_url: str = Field(
        default="postgresql+psycopg://fab_reader:fab_reader@localhost:5432/fab_business"
    )
    # Application DB (users, conversations, audit log, RAG chunks with pgvector).
    app_db_url: str = Field(
        default="postgresql+psycopg://fabpilot_app:fabpilot_app@localhost:5432/fabpilot_app"
    )

    # LLM: any OpenAI-compatible endpoint. Ollama exposes /v1, vLLM serves /v1 as well.
    llm_provider: Literal["ollama", "vllm", "openai_compatible"] = "ollama"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen3:8b"
    llm_api_key: SecretStr = SecretStr("not-needed-for-ollama")
    llm_timeout_s: float = 60.0

    # Comma-separated list of origins allowed to call the API from a browser.
    cors_origins: str = "http://localhost:5000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
