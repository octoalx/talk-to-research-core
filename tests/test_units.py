from pathlib import Path

import pytest

from cli.main import main
from core.structure.units import Document, Unit, address, split_units

CONTRACTS = Path(__file__).resolve().parent.parent / "eval" / "testset-by" / "contracts"
AGROMASH = CONTRACTS / "01-postavka-agromash.md"
ALL_CONTRACTS = sorted(CONTRACTS.glob("*.md"))


def by_number(doc: Document, number: str) -> Unit:
    found = [u for u in doc.units if u.number == number]
    assert len(found) == 1, found
    return found[0]


# --- договор 01 ---


def test_agromash_title() -> None:
    assert split_units(AGROMASH.read_text(encoding="utf-8")).title == "ДОГОВОР ПОСТАВКИ № 14/26"


def test_agromash_units_in_order() -> None:
    doc = split_units(AGROMASH.read_text(encoding="utf-8"))
    got = [(u.label, u.number) for u in doc.units]
    sections = [("раздел", str(n)) for n in range(1, 7)]
    clauses = ["1.1", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "6.1", "6.2"]
    expected = [("преамбула", "")]
    for label, number in sections:
        expected.append((label, number))
        expected.extend(("пункт", c) for c in clauses if c.split(".")[0] == number)
    assert got == expected
    assert sorted(got[1:]) == sorted(sections + [("пункт", c) for c in clauses])
    assert [u.id for u in doc.units] == list(range(len(doc.units)))


def test_agromash_clause_6_2() -> None:
    doc = split_units(AGROMASH.read_text(encoding="utf-8"))
    unit = by_number(doc, "6.2")
    parent = doc.units[unit.parent] if unit.parent is not None else None
    assert parent is not None
    assert (parent.label, parent.number, parent.title) == ("раздел", "6", "Срок действия")
    assert address(doc, unit) == "ДОГОВОР ПОСТАВКИ № 14/26, п. 6.2"
    assert unit.text.startswith("Если ни одна из сторон")
    # «Подписи сторон.» после последнего пункта входит в его текст
    assert unit.text.endswith("Подписи сторон.")


def test_agromash_addresses_of_other_labels() -> None:
    doc = split_units(AGROMASH.read_text(encoding="utf-8"))
    assert address(doc, by_number(doc, "6")) == "ДОГОВОР ПОСТАВКИ № 14/26, разд. 6"
    assert address(doc, doc.units[0]) == "ДОГОВОР ПОСТАВКИ № 14/26, преамбула"


def test_agromash_preamble_and_lines() -> None:
    doc = split_units(AGROMASH.read_text(encoding="utf-8"))
    pre = doc.units[0]
    assert (pre.label, pre.parent, pre.line_start) == ("преамбула", None, 0)
    assert "заключили настоящий договор" in pre.text
    sec1 = by_number(doc, "1")
    assert (sec1.line_start, sec1.line_end, sec1.text, sec1.parent) == (8, 8, "", None)
    c11 = by_number(doc, "1.1")
    assert (c11.line_start, c11.line_end, c11.level, sec1.level) == (9, 9, 2, 1)


# --- все 12 договоров ---


def test_all_contracts_present() -> None:
    assert len(ALL_CONTRACTS) == 12


@pytest.mark.parametrize("path", ALL_CONTRACTS, ids=lambda p: p.name)
def test_dotted_clause_has_parent_section(path: Path) -> None:
    doc = split_units(path.read_text(encoding="utf-8"))
    for unit in doc.units:
        parts = unit.number.split(".")
        if len(parts) == 2:
            assert unit.parent is not None, unit
            assert doc.units[unit.parent].number == parts[0]


@pytest.mark.parametrize("path", ALL_CONTRACTS, ids=lambda p: p.name)
def test_no_line_lost(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    doc = split_units(text)
    starts = {u.line_start: u for u in doc.units if u.label != "преамбула"}
    for i, raw in enumerate(text.splitlines()):
        line = raw.strip()
        if not line:
            continue
        owners = [u for u in doc.units if u.line_start <= i <= u.line_end]
        assert len(owners) == 1, (i, line, owners)
        unit = owners[0]
        if i in starts and starts[i] is unit:
            # строка маркера: заголовок или пункт, текст которого начинается после номера
            if unit.label == "пункт":
                assert line.endswith(unit.text.splitlines()[0]), (i, line)
            continue
        assert line in unit.text, (i, line, unit)


# --- маленькие строки ---


def test_articles_inside_chapters() -> None:
    doc = split_units(
        "Раздел I. Общие положения\nГлава 1. Основы\nСтатья 1. Цели\nТекст 1.\n"
        "Статья 2.\nТекст 2.\nГлава 2\nСтатья 3. Сроки\nТекст 3.\n"
    )
    labels = [(u.label, u.number, u.parent) for u in doc.units]
    assert labels == [
        ("раздел", "1", None),
        ("глава", "1", 0),
        ("статья", "1", 1),
        ("статья", "2", 1),
        ("глава", "2", 0),
        ("статья", "3", 4),
    ]
    art3 = doc.units[5]
    assert (art3.title, art3.text, art3.level) == ("Сроки", "Текст 3.", 3)
    assert address(doc, art3) == "ст. 3"
    assert address(doc, doc.units[4]) == "гл. 2"


def test_nested_clause_inside_clause() -> None:
    doc = split_units("# Акт\n2. Общее\n2.3. Порядок\n2.3.1. Подпункт\n2.4. Другое\n")
    assert doc.title == "Акт"
    u = {x.number: x for x in doc.units}
    assert u["2.3"].parent == u["2"].id
    assert u["2.3.1"].parent == u["2.3"].id
    assert u["2.4"].parent == u["2"].id
    assert u["2.3.1"].level == 3
    assert address(doc, u["2.3.1"]) == "Акт, п. 2.3.1"


def test_clause_without_section() -> None:
    doc = split_units("5.1. Пункт без раздела.\n")
    assert len(doc.units) == 1
    unit = doc.units[0]
    assert (unit.number, unit.parent, unit.text, unit.level) == ("5.1", None, "Пункт без раздела.", 1)
    assert doc.title == ""


def test_document_without_numbering() -> None:
    doc = split_units("\n# Письмо\n\nПросим сообщить о сроках.\n\nДиректор\n\n")
    assert len(doc.units) == 1
    unit = doc.units[0]
    assert (unit.label, unit.number, unit.parent) == ("преамбула", "", None)
    assert (unit.line_start, unit.line_end) == (1, 5)
    assert unit.text == "# Письмо\n\nПросим сообщить о сроках.\n\nДиректор"
    assert address(doc, unit) == "Письмо, преамбула"


def test_empty_document() -> None:
    assert split_units("\n  \n") == Document(title="", units=[])


# --- командная строка ---


def test_cli_units(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["units", str(AGROMASH)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 17
    assert any(line.startswith("  6.2 Если ни одна из сторон") for line in lines)
    assert any(line.startswith("6 Срок действия") for line in lines)


def test_nested_markdown_heading_inside_section() -> None:
    doc = split_units("## 2. Общее\n### 2.3. Порядок\n2.3.1. Подпункт\n")
    u = {x.number: x for x in doc.units}
    assert (u["2.3"].label, u["2.3"].parent, u["2.3.1"].parent) == ("раздел", u["2"].id, u["2.3"].id)
