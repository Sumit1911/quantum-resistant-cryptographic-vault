"""Unit tests for core.storage (Phase 3)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from core import storage


def _new_in_memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    schema_path = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
    conn.executescript(schema_path.read_text(encoding="utf-8"))


def _create_user(conn: sqlite3.Connection, username: str = "alice") -> int:
    return storage.create_user(
        conn,
        username=username,
        password_hash="argon2-hash",
        kyber_pk=b"kpk",
        kyber_sk_enc=b"ksk",
        kyber_sk_iv=b"kiv123456789",
        dil_pk=b"dpk",
        dil_sk_enc=b"dsk",
        dil_sk_iv=b"div123456789",
        kdf_salt=b"1234567890abcdef",
    )


def test_init_db_is_idempotent(tmp_path) -> None:
    db_path = tmp_path / "vault_test.db"

    storage.init_db(str(db_path))
    storage.init_db(str(db_path))

    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "users" in tables
    assert "vault_items" in tables


def test_create_and_get_user() -> None:
    conn = _new_in_memory_conn()
    _apply_schema(conn)

    user_id = _create_user(conn, username="bob")
    user = storage.get_user_by_username(conn, "bob")

    assert user is not None
    assert user["id"] == user_id
    assert user["username"] == "bob"
    assert user["kyber_public_key"] == b"kpk"


def test_get_user_by_username_missing_returns_none() -> None:
    conn = _new_in_memory_conn()
    _apply_schema(conn)

    assert storage.get_user_by_username(conn, "missing") is None


def test_store_list_get_delete_vault_item_flow() -> None:
    conn = _new_in_memory_conn()
    _apply_schema(conn)
    user_id = _create_user(conn)

    item_id = storage.store_vault_item(
        conn,
        user_id=user_id,
        item_name="secret.txt",
        item_type="file",
        metadata_nonce=b"0123456789abcdef",
        ciphertext=b"cipher",
        aes_iv=b"iv-123456789",
        aes_tag=b"1234567890abcdef",
        kyber_capsule=b"capsule",
        dilithium_signature=b"signature",
        original_size=6,
        mime_type="text/plain",
    )

    items = storage.list_vault_items(conn, user_id)
    assert len(items) == 1
    assert items[0].id == item_id
    assert items[0].item_name == "secret.txt"
    assert items[0].ciphertext is None

    item = storage.get_vault_item(conn, item_id, user_id)
    assert item is not None
    assert item.metadata_nonce == b"0123456789abcdef"
    assert item.ciphertext == b"cipher"
    assert item.aes_iv == b"iv-123456789"
    assert item.dilithium_signature == b"signature"

    deleted = storage.delete_vault_item(conn, item_id, user_id)
    assert deleted is True
    assert storage.get_vault_item(conn, item_id, user_id) is None


def test_get_vault_item_wrong_user_returns_none() -> None:
    conn = _new_in_memory_conn()
    _apply_schema(conn)
    user_a = _create_user(conn, "user_a")
    user_b = _create_user(conn, "user_b")

    item_id = storage.store_vault_item(
        conn,
        user_id=user_a,
        item_name="secret.txt",
        item_type="file",
        metadata_nonce=b"0123456789abcdef",
        ciphertext=b"cipher",
        aes_iv=b"iv-123456789",
        aes_tag=b"1234567890abcdef",
        kyber_capsule=b"capsule",
        dilithium_signature=b"signature",
        original_size=6,
        mime_type="text/plain",
    )

    assert storage.get_vault_item(conn, item_id, user_b) is None
