from __future__ import annotations

import sqlite3
from pathlib import Path

import sqlite_vec


def connect(path: Path | str = ":memory:") -> sqlite3.Connection:
    """Открыть базу с загруженным sqlite-vec и режимом WAL для файлов на диске."""
    conn = sqlite3.connect(str(path))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode=WAL")
    return conn
