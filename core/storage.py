"""SQLite storage layer for users and vault items."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VaultItem:
    id: int
    user_id: int
    item_name: str
    item_type: str
    ciphertext: bytes | None
    aes_iv: bytes | None
    aes_tag: bytes | None
    kyber_capsule: bytes | None
    dilithium_signature: bytes | None
    original_size: int | None
    mime_type: str | None


def get_connection(db_path: str = "vault.db") -> sqlite3.Connection:
    """Return a configured SQLite connection with WAL and FK support."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path: str = "vault.db") -> None:
    """Initialize database schema from db/schema.sql."""
    schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with get_connection(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()


def create_user(
    conn: sqlite3.Connection,
    username: str,
    password_hash: str,
    kyber_pk: bytes,
    kyber_sk_enc: bytes,
    kyber_sk_iv: bytes,
    dil_pk: bytes,
    dil_sk_enc: bytes,
    dil_sk_iv: bytes,
    kdf_salt: bytes,
) -> int:
    """Insert a new user row and return the new user id."""
    cursor = conn.execute(
        """
        INSERT INTO users (
            username, password_hash,
            kyber_public_key, kyber_private_key,
            dilithium_public_key, dilithium_private_key,
            kdf_salt, kyber_private_key_iv, dilithium_private_key_iv
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            password_hash,
            kyber_pk,
            kyber_sk_enc,
            dil_pk,
            dil_sk_enc,
            kdf_salt,
            kyber_sk_iv,
            dil_sk_iv,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def get_user_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    """Fetch a user row by username."""
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        return None
    return dict(row)


def store_vault_item(
    conn: sqlite3.Connection,
    user_id: int,
    item_name: str,
    item_type: str,
    ciphertext: bytes,
    aes_iv: bytes,
    aes_tag: bytes,
    kyber_capsule: bytes,
    dilithium_signature: bytes,
    original_size: int | None,
    mime_type: str | None,
) -> int:
    """Insert an encrypted vault item and return new item id."""
    cursor = conn.execute(
        """
        INSERT INTO vault_items (
            user_id, item_name, item_type,
            ciphertext, aes_iv, aes_tag,
            kyber_capsule, dilithium_signature,
            original_size, mime_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            item_name,
            item_type,
            ciphertext,
            aes_iv,
            aes_tag,
            kyber_capsule,
            dilithium_signature,
            original_size,
            mime_type,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def list_vault_items(conn: sqlite3.Connection, user_id: int) -> list[VaultItem]:
    """List vault items metadata for a user (without ciphertext blobs)."""
    rows = conn.execute(
        """
        SELECT id, user_id, item_name, item_type,
               NULL as ciphertext, NULL as aes_iv, NULL as aes_tag,
               NULL as kyber_capsule, NULL as dilithium_signature,
               original_size, mime_type
        FROM vault_items
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,),
    ).fetchall()

    return [VaultItem(**dict(row)) for row in rows]


def get_vault_item(conn: sqlite3.Connection, item_id: int, user_id: int) -> VaultItem | None:
    """Fetch a vault item with ownership check."""
    row = conn.execute(
        """
        SELECT id, user_id, item_name, item_type,
               ciphertext, aes_iv, aes_tag,
               kyber_capsule, dilithium_signature,
               original_size, mime_type
        FROM vault_items
        WHERE id = ? AND user_id = ?
        """,
        (item_id, user_id),
    ).fetchone()

    if row is None:
        return None
    return VaultItem(**dict(row))


def delete_vault_item(conn: sqlite3.Connection, item_id: int, user_id: int) -> bool:
    """Delete a vault item with ownership check."""
    cursor = conn.execute(
        "DELETE FROM vault_items WHERE id = ? AND user_id = ?",
        (item_id, user_id),
    )
    conn.commit()
    return cursor.rowcount > 0
