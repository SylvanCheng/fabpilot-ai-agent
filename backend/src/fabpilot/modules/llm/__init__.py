"""LLM module: access to a chat model behind a port.

P0 ships only settings, the port and a config-report health check. The OpenAI-compatible adapter
(Ollama / vLLM) arrives in P1; callers will depend on `ChatModel`, never on a vendor SDK.
"""

from fabpilot.modules.llm.module import LlmConfigCheck
from fabpilot.modules.llm.ports import ChatMessage, ChatModel
from fabpilot.modules.llm.settings import LlmSettings

__all__ = ["ChatMessage", "ChatModel", "LlmConfigCheck", "LlmSettings"]
