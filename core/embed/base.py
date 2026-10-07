from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    """Модель эмбеддингов (bge-m3 на машине разработчика) или поддельная для тестов."""

    @property
    def dim(self) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...
