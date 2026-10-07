"""Настройки ядра: config.toml плюс переопределение переменными окружения.

Переменная TTR_<РАЗДЕЛ>_<КЛЮЧ> заменяет значение [раздел] ключ, тип берётся
из значения в файле (целые числа остаются целыми).
"""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENV_PREFIX = "TTR_"
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "config.toml"


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    model: str
    context_tokens: int


@dataclass(frozen=True)
class EmbedConfig:
    model: str
    dim: int


@dataclass(frozen=True)
class SearchConfig:
    top_k: int


@dataclass(frozen=True)
class Config:
    data_dir: Path
    llm: LLMConfig
    embed: EmbedConfig
    search: SearchConfig


def _apply_env(raw: dict[str, dict[str, Any]], env: Mapping[str, str]) -> None:
    for section, values in raw.items():
        for key, current in values.items():
            name = f"{ENV_PREFIX}{section}_{key}".upper()
            if name not in env:
                continue
            value = env[name]
            values[key] = int(value) if isinstance(current, int) else value


def load_config(path: Path = DEFAULT_PATH, env: Mapping[str, str] | None = None) -> Config:
    with path.open("rb") as f:
        raw: dict[str, dict[str, Any]] = tomllib.load(f)
    _apply_env(raw, os.environ if env is None else env)
    return Config(
        data_dir=Path(raw["paths"]["data_dir"]),
        llm=LLMConfig(**raw["llm"]),
        embed=EmbedConfig(**raw["embed"]),
        search=SearchConfig(**raw["search"]),
    )
