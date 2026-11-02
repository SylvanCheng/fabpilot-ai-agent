from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatModel(Protocol):
    """What the rest of the system needs from an LLM. Implemented in P1."""

    def complete(self, messages: list[ChatMessage]) -> str: ...
