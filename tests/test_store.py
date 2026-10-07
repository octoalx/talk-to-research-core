"""M0: в базе работают FTS5 и sqlite-vec — основа гибридного индекса (decisions/020)."""

import sqlite_vec

from core.embed import FakeEmbedder
from core.store import connect


def test_fts5_finds_word() -> None:
    conn = connect()
    conn.execute("create virtual table units_fts using fts5(text_norm)")
    conn.executemany(
        "insert into units_fts(text_norm) values (?)",
        [("покупатель уплачивать пеня",), ("договор действовать до 31 декабрь",)],
    )
    rows = conn.execute("select text_norm from units_fts where units_fts match 'пеня'").fetchall()
    assert rows == [("покупатель уплачивать пеня",)]


def test_sqlite_vec_nearest_neighbour() -> None:
    conn = connect()
    emb = FakeEmbedder(dim=8)
    texts = ["п. 4.1 пеня 0,2%", "п. 6.1 срок действия", "п. 5.1 споры"]
    conn.execute("create virtual table unit_vectors using vec0(embedding float[8])")
    for rowid, vec in enumerate(emb.embed(texts), start=1):
        conn.execute(
            "insert into unit_vectors(rowid, embedding) values (?, ?)",
            (rowid, sqlite_vec.serialize_float32(vec)),
        )
    query = sqlite_vec.serialize_float32(emb.embed(["п. 6.1 срок действия"])[0])
    rows = conn.execute(
        "select rowid, distance from unit_vectors where embedding match ? and k = 1", (query,)
    ).fetchall()
    assert rows[0][0] == 2
    assert rows[0][1] < 1e-6


def test_file_database_uses_wal(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "ws.sqlite")
    (mode,) = conn.execute("pragma journal_mode").fetchone()
    assert mode == "wal"
