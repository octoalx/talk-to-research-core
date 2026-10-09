from pathlib import Path

import pytest

from core.structure.numbering import Marker, find_numbering

CONTRACTS = Path(__file__).resolve().parent.parent / "eval" / "testset-by" / "contracts"


def one(text: str) -> Marker:
    markers = find_numbering(text)
    assert len(markers) == 1, markers
    return markers[0]


def test_markdown_heading_with_number() -> None:
    assert one("## 1. Предмет") == Marker(
        line=0, kind="heading", number="1", label="раздел", title="Предмет", level=1
    )


def test_markdown_heading_with_nested_number() -> None:
    m = one("### 2.3. Порядок приёмки")
    assert (m.kind, m.number, m.title, m.level) == ("heading", "2.3", "Порядок приёмки", 2)


def test_clause_with_trailing_dot() -> None:
    assert one("1.1. Текст пункта") == Marker(
        line=0, kind="clause", number="1.1", label="пункт", title="", level=2
    )


def test_clause_without_trailing_dot() -> None:
    m = one("2.3 Текст пункта")
    assert (m.kind, m.number, m.label, m.level) == ("clause", "2.3", "пункт", 2)


def test_single_level_clause() -> None:
    m = one("1. С 1 ноября 2026 г. арендная плата составляет 2 300 BYN в месяц.")
    assert (m.kind, m.number, m.level) == ("clause", "1", 1)


def test_parenthesis_list_is_not_clause() -> None:
    assert find_numbering("1) Текст") == []
    assert find_numbering("2) уплатить пеню 0,3% за каждый день просрочки.") == []


def test_article_with_dot() -> None:
    assert one("Статья 15.") == Marker(
        line=0, kind="clause", number="15", label="статья", title="", level=1
    )


def test_article_with_title() -> None:
    m = one("Статья 15. Название")
    assert (m.number, m.label, m.title, m.level) == ("15", "статья", "Название", 1)


def test_chapter() -> None:
    m = one("Глава 2")
    assert (m.number, m.label, m.title, m.level) == ("2", "глава", "", 1)


def test_section_roman_number() -> None:
    m = one("Раздел III")
    assert (m.number, m.label, m.level) == ("3", "раздел", 1)


@pytest.mark.parametrize(
    ("roman", "arabic"),
    [("I", "1"), ("IV", "4"), ("IX", "9"), ("XIV", "14"), ("XL", "40"), ("XCIX", "99")],
)
def test_roman_numbers(roman: str, arabic: str) -> None:
    assert one(f"Раздел {roman}").number == arabic


def test_article_in_markdown_heading() -> None:
    m = one("## Статья 7. Ответственность сторон")
    assert (m.kind, m.number, m.label, m.title) == ("heading", "7", "статья", "Ответственность сторон")


def test_document_title_is_not_marker() -> None:
    assert find_numbering("# ДОГОВОР ПОСТАВКИ № 14/26") == []


@pytest.mark.parametrize(
    "text",
    [
        "12 января 2026 г.",
        "г. Минск, 12 января 2026 г.",
        "0,2% от неоплаченной суммы",
        "Договор № 14/26 от 12.01.2026",
        "ул. Вымышленная, 7.",
        "12.01.2026 г. стороны подписали акт.",
        "1 900 BYN в месяц",
        "2026. Год подписания",
        "Статья 15 Закона применяется к сторонам.",
        "Раздел ИЛИ глава",
        "Как сказано в п. 2.3. договора",
        "> 1.1. цитата",
    ],
)
def test_no_false_positives(text: str) -> None:
    assert find_numbering(text) == []


def test_line_numbers_count_from_zero() -> None:
    text = "# ДОГОВОР\n\n## 1. Предмет\n1.1. Текст\n"
    assert [(m.line, m.number) for m in find_numbering(text)] == [(2, "1"), (3, "1.1")]


def test_contract_01_order() -> None:
    text = (CONTRACTS / "01-postavka-agromash.md").read_text(encoding="utf-8")
    got = [(m.kind, m.number) for m in find_numbering(text)]
    expected = [
        ("heading", "1"), ("clause", "1.1"),
        ("heading", "2"), ("clause", "2.1"), ("clause", "2.2"),
        ("heading", "3"), ("clause", "3.1"), ("clause", "3.2"),
        ("heading", "4"), ("clause", "4.1"), ("clause", "4.2"),
        ("heading", "5"), ("clause", "5.1"),
        ("heading", "6"), ("clause", "6.1"), ("clause", "6.2"),
    ]  # fmt: skip
    assert got == expected
    assert [m.title for m in find_numbering(text) if m.kind == "heading"] == [
        "Предмет",
        "Цена и порядок расчётов",
        "Поставка",
        "Ответственность",
        "Разрешение споров",
        "Срок действия",
    ]


def test_all_contracts_clause_matches_last_heading() -> None:
    files = sorted(CONTRACTS.glob("*.md"))
    assert len(files) == 12
    checked = 0
    for path in files:
        heading: str | None = None
        for m in find_numbering(path.read_text(encoding="utf-8")):
            if m.kind == "heading":
                heading = m.number
            elif m.level == 2:
                assert heading is not None, (path.name, m)
                assert m.number.split(".")[0] == heading, (path.name, m)
                checked += 1
    assert checked > 0
