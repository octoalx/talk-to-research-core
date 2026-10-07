"""Клиент модели: общий интерфейс и поддельная реализация для тестов."""

from core.llm.base import ChatMessage, ChatModel
from core.llm.fake import FakeChatModel

__all__ = ["ChatMessage", "ChatModel", "FakeChatModel"]
