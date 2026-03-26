"""Initialize the SQLite database using db/schema.sql."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def main() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    schema_path = root_dir / "db" / "schema.sql"
    db_path = Path(os.getenv("DB_PATH", root_dir / "vault.db"))

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()

    print(f"Database initialized at: {db_path}")


if __name__ == "__main__":
    main()
