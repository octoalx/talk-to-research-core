"""Эмбеддинги: общий интерфейс и поддельная реализация для тестов."""

from core.embed.base import Embedder
from core.embed.fake import FakeEmbedder

__all__ = ["Embedder", "FakeEmbedder"]
