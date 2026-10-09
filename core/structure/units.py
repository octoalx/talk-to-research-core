"""Деление документа на юридические единицы с адресами (M3, цель 2).

Единицы строятся по маркерам из find_numbering: каждая единица — строки от
своего маркера до следующего. Текст до первого маркера — «преамбула».
Строка заголовка («## 6. Срок действия», «Статья 15. Название») в текст
единицы не входит: номер и название лежат в полях number и title. У пункта
в тексте («6.2. Если ...») номер отрезается, остальное начинает текст.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.structure.numbering import Marker, find_numbering

PREAMBLE = "преамбула"

_TITLE = re.compile(r"^#\s+(?P<title>.*?)\s*#*\s*$")
_ABBREV = {"пункт": "п.", "раздел": "разд.", "статья": "ст.", "глава": "гл."}
# Родитель по слову: статья — в главе, глава — в разделе. Поиск вверх по
# тексту останавливается на единице старшего уровня из этого же ряда.
_KEYWORD_RANKS = ("раздел", "глава", "статья")


@dataclass(frozen=True)
class Unit:
    """Юридическая единица документа.

    id — порядковый номер с 0; number — номер как в тексте («6.2», «6»,
    у преамбулы пусто); label — «пункт», «раздел», «статья», «глава» или
    «преамбула»; title — название раздела или пустая строка; text — строки
    единицы без пустых строк по краям; parent — id родителя или None;
    level — глубина вложенности (у единицы без родителя — 1); line_start,
    line_end — номера строк с 0, конец включительно.
    """

    id: int
    number: str
    label: str
    title: str
    text: str
    parent: int | None
    level: int
    line_start: int
    line_end: int


@dataclass(frozen=True)
class Document:
    """Документ: title — текст первого заголовка «# ...» или пустая строка."""

    title: str
    units: list[Unit]


def split_units(text: str) -> Document:
    """Разделить текст документа на юридические единицы."""
    lines = text.splitlines()
    markers = find_numbering(text)
    units: list[Unit] = []

    first = markers[0].line if markers else len(lines)
    span = _trim(lines, 0, first)
    if span is not None:
        start, end = span
        units.append(Unit(0, "", PREAMBLE, "", _join(lines[start : end + 1]), None, 1, start, end))

    for i, marker in enumerate(markers):
        stop = markers[i + 1].line if i + 1 < len(markers) else len(lines)
        body = _trim(lines, marker.line + 1, stop)
        line_end = body[1] if body is not None else marker.line
        chunk = [_strip_number(lines[marker.line], marker)] if _inline(marker) else []
        chunk += lines[marker.line + 1 : line_end + 1]
        parent = _find_parent(units, marker)
        level = units[parent].level + 1 if parent is not None else 1
        units.append(
            Unit(
                id=len(units),
                number=marker.number,
                label=marker.label,
                title=marker.title,
                text=_join(chunk),
                parent=parent,
                level=level,
                line_start=marker.line,
                line_end=line_end,
            )
        )
    return Document(title=_title(lines), units=units)


def address(doc: Document, unit: Unit) -> str:
    """Адрес единицы: «ДОГОВОР ПОСТАВКИ № 14/26, п. 6.2»."""
    if unit.label == PREAMBLE:
        local = PREAMBLE
    else:
        local = f"{_ABBREV.get(unit.label, unit.label)} {unit.number}"
    return f"{doc.title}, {local}" if doc.title else local


def _title(lines: list[str]) -> str:
    for raw in lines:
        m = _TITLE.match(raw.strip())
        if m:
            return m.group("title")
    return ""


def _inline(marker: Marker) -> bool:
    """Пункт в тексте: после номера в той же строке идёт его текст."""
    return marker.kind == "clause" and marker.label == "пункт"


def _strip_number(raw: str, marker: Marker) -> str:
    s = raw.strip()
    return s[len(marker.number) :].lstrip(".").strip()


def _trim(lines: list[str], start: int, stop: int) -> tuple[int, int] | None:
    """Первая и последняя непустые строки в [start, stop) или None."""
    filled = [i for i in range(start, stop) if lines[i].strip()]
    return (filled[0], filled[-1]) if filled else None


def _join(chunk: list[str]) -> str:
    return "\n".join(line.rstrip() for line in chunk).strip("\n")


def _find_parent(units: list[Unit], marker: Marker) -> int | None:
    if marker.label in ("статья", "глава") and "." not in marker.number:
        rank = _KEYWORD_RANKS.index(marker.label)
        for unit in reversed(units):
            if unit.label not in _KEYWORD_RANKS:
                continue
            other = _KEYWORD_RANKS.index(unit.label)
            if other == rank - 1:
                return unit.id
            if other < rank - 1:
                return None
        return None

    # «2.3.1» — в «2.3», а если его нет — в «2»; ищем ближайший выше по тексту.
    parts = marker.number.split(".")
    for size in range(len(parts) - 1, 0, -1):
        prefix = ".".join(parts[:size])
        for unit in reversed(units):
            if unit.number == prefix and unit.label in ("пункт", "раздел"):
                return unit.id
    return None
