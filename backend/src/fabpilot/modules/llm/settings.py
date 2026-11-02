from typing import Literal

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from fabpilot.core.settings import EnvSettings


class LlmSettings(EnvSettings):
    """Env vars `LLM_*`. Switching Ollama (dev) <-> vLLM (prod) is a `.env` change only."""

    model_config = SettingsConfigDict({**EnvSettings.model_config, "env_prefix": "LLM_"})

    provider: Literal["ollama", "vllm", "openai_compatible"] = "ollama"
    base_url: str = "http://localhost:11434/v1"
    model: str = "qwen3:8b"
    api_key: SecretStr = SecretStr("not-needed-for-ollama")
    timeout_s: float = 60.0
