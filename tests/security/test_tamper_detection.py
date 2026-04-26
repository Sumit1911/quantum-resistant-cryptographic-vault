"""Security tests for tamper detection guarantees."""

from __future__ import annotations

import sqlite3

import pytest

from core import storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "security_tamper.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_ciphertext_tamper_raises_integrity_error_before_decrypt(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("alice", "pass123", conn)
    session = vault_manager.login("alice", "pass123", conn)
    assert session is not None

    item_id = vault_manager.store_file(session, "secret.txt", b"top secret", "text/plain")

    row = conn.execute("SELECT ciphertext FROM vault_items WHERE id = ?", (item_id,)).fetchone()
    assert row is not None
    tampered = bytearray(row[0])
    tampered[0] ^= 0x01
    conn.execute("UPDATE vault_items SET ciphertext = ? WHERE id = ?", (bytes(tampered), item_id))
    conn.commit()

    with pytest.raises(vault_manager.IntegrityError):
        vault_manager.retrieve_file(session, item_id)


def test_item_name_tamper_raises_integrity_error(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("bob", "pass123", conn)
    session = vault_manager.login("bob", "pass123", conn)
    assert session is not None

    item_id = vault_manager.store_file(session, "original.txt", b"data", "text/plain")

    conn.execute("UPDATE vault_items SET item_name = ? WHERE id = ?", ("changed.txt", item_id))
    conn.commit()

    with pytest.raises(vault_manager.IntegrityError):
        vault_manager.retrieve_file(session, item_id)


def test_corrupted_aes_tag_fails_closed(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("eve", "pass123", conn)
    session = vault_manager.login("eve", "pass123", conn)
    assert session is not None

    item_id = vault_manager.store_file(session, "tag.txt", b"payload", "text/plain")

    row = conn.execute("SELECT aes_tag FROM vault_items WHERE id = ?", (item_id,)).fetchone()
    assert row is not None
    tampered_tag = bytearray(row[0])
    tampered_tag[0] ^= 0x01
    conn.execute("UPDATE vault_items SET aes_tag = ? WHERE id = ?", (bytes(tampered_tag), item_id))
    conn.commit()

    with pytest.raises(vault_manager.IntegrityError):
        vault_manager.retrieve_file(session, item_id)
