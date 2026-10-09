"""Поиск нумерации разделов и пунктов в тексте документа (M3, цель 1).

Распознаются:
- заголовки Markdown с номером: «## 1. Предмет», «### 2.3 Порядок»;
- пункты в начале строки: «1.1. Текст», «2.3 Текст», «1. Текст»
  (с одним числом — только с точкой после него; «1) Текст» — не пункт);
- «Статья 15.», «Статья 15. Название», «Глава 2», «Раздел III»
  (римские цифры переводятся в арабские).

Числа внутри текста, даты («12 января 2026 г.», «12.01.2026»), проценты,
номера документов и адреса пунктами не считаются: номер должен стоять в
начале строки, части номера — не длиннее трёх цифр, после номера — пробел.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Kind = Literal["heading", "clause"]

_NUM = r"\d{1,3}(?:\.\d{1,3})*"
_ROMAN = r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})"

_HEADING = re.compile(r"^#{1,6}\s+(?P<rest>.*?)\s*#*\s*$")
# «Статья 15», «Глава 2», «Раздел III»: после номера — конец строки или точка и название.
_KEYWORD = re.compile(
    rf"^(?P<label>статья|глава|раздел)\s+(?P<num>{_NUM}|{_ROMAN})(?!\w|\.\d)"
    r"(?:\s*\.?\s*$|\.\s+(?P<title>\S.*?)\s*$)",
    re.IGNORECASE,
)
# Номер в заголовке Markdown: «1. Предмет», «2.3 Порядок», «4».
_HEADING_NUM = re.compile(rf"^(?P<num>{_NUM})\.?(?:\s+(?P<title>\S.*?))?\s*$")
# Пункт в тексте: «1.1. Текст», «2.3 Текст», «1. Текст».
_CLAUSE = re.compile(r"^(?P<num>\d{1,3}(?:\.\d{1,3})+\.?|\d{1,3}\.)\s+\S")

_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


@dataclass(frozen=True)
class Marker:
    """Номер раздела или пункта, найденный в строке документа.

    line — номер строки с 0; kind — «heading» для заголовков Markdown,
    «clause» для строк внутри текста; number — как в тексте, без точки в
    конце (римские цифры — арабскими); label — «пункт», «статья», «глава»
    или «раздел»; title — текст заголовка без номера или пустая строка;
    level — глубина номера («1» — 1, «2.3» — 2, «Статья 15» — 1).
    """

    line: int
    kind: Kind
    number: str
    label: str
    title: str
    level: int


def find_numbering(text: str) -> list[Marker]:
    """Вернуть маркеры нумерации в порядке строк документа."""
    markers: list[Marker] = []
    for i, raw in enumerate(text.splitlines()):
        marker = _parse_line(i, raw.strip())
        if marker is not None:
            markers.append(marker)
    return markers


def _parse_line(line: int, s: str) -> Marker | None:
    heading = _HEADING.match(s)
    if heading:
        rest = heading.group("rest")
        kw = _keyword(line, "heading", rest)
        if kw is not None:
            return kw
        m = _HEADING_NUM.match(rest)
        if m is None:
            return None
        number = m.group("num")
        return Marker(line, "heading", number, "раздел", m.group("title") or "", _level(number))

    kw = _keyword(line, "clause", s)
    if kw is not None:
        return kw
    m = _CLAUSE.match(s)
    if m is None:
        return None
    number = m.group("num").rstrip(".")
    return Marker(line, "clause", number, "пункт", "", _level(number))


def _keyword(line: int, kind: Kind, s: str) -> Marker | None:
    m = _KEYWORD.match(s)
    if m is None:
        return None
    num = m.group("num")
    if not num:  # пустая строка тоже подходит под шаблон римского числа
        return None
    if not num[0].isdigit():
        num = str(_roman_to_int(num))
    return Marker(line, kind, num, m.group("label").lower(), m.group("title") or "", _level(num))


def _level(number: str) -> int:
    return number.count(".") + 1


def _roman_to_int(roman: str) -> int:
    total = 0
    for ch, nxt in zip(roman, roman[1:] + " ", strict=True):
        value = _ROMAN_VALUES[ch]
        total += -value if _ROMAN_VALUES.get(nxt, 0) > value else value
    return total
