from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatModel(Protocol):
    """Модель за OpenAI-совместимым API (Ollama, MLX) или поддельная для тестов."""

    def complete(self, messages: list[ChatMessage]) -> str: ...

    def stream(self, messages: list[ChatMessage]) -> Iterator[str]: ...
