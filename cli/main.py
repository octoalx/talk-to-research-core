"""Командная строка ядра. Команды появляются по вехам плана (docs/PLAN.md)."""

from __future__ import annotations

import argparse
import sys

from core import __version__
from core.config import load_config
from core.store import connect
from core.structure.units import split_units


def _check(_: argparse.Namespace) -> int:
    cfg = load_config()
    conn = connect()
    (vec_version,) = conn.execute("select vec_version()").fetchone()
    (sqlite_version,) = conn.execute("select sqlite_version()").fetchone()
    print(f"talk-to-research-core {__version__}")
    print(f"SQLite {sqlite_version}, sqlite-vec {vec_version}")
    print(f"модель: {cfg.llm.model} @ {cfg.llm.base_url}, контекст {cfg.llm.context_tokens}")
    return 0


def _units(args: argparse.Namespace) -> int:
    with open(args.path, encoding="utf-8") as f:
        doc = split_units(f.read())
    for unit in doc.units:
        head = unit.number or unit.label
        snippet = " ".join((unit.title or unit.text).split())[:60]
        print(f"{'  ' * (unit.level - 1)}{head} {snippet}".rstrip())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ttr", description="Ядро talk-to-research")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="проверить окружение: SQLite, sqlite-vec, настройки")
    check.set_defaults(func=_check)
    units = sub.add_parser("units", help="разделить документ на юридические единицы и напечатать дерево")
    units.add_argument("path", help="путь к файлу Markdown")
    units.set_defaults(func=_units)
    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
