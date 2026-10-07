from __future__ import annotations

from collections.abc import Callable, Iterator

from core.llm.base import ChatMessage


class FakeChatModel:
    """Детерминированная модель для тестов: отвечает по заданной функции, без сети."""

    def __init__(self, respond: Callable[[list[ChatMessage]], str] | None = None) -> None:
        self._respond = respond or (lambda messages: messages[-1].content)
        self.calls: list[list[ChatMessage]] = []

    def complete(self, messages: list[ChatMessage]) -> str:
        self.calls.append(list(messages))
        return self._respond(messages)

    def stream(self, messages: list[ChatMessage]) -> Iterator[str]:
        yield from self.complete(messages).split(" ")
