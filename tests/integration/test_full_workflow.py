"""Integration tests for Phase 4 vault orchestration."""

from __future__ import annotations

import sqlite3

import pytest

from core import storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "integration_vault.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_register_login_store_retrieve_roundtrip(tmp_path) -> None:
    conn = _setup_db(tmp_path)

    assert vault_manager.register("alice", "pass123", conn) is True
    session = vault_manager.login("alice", "pass123", conn)
    assert session is not None

    original = b"hello quantum vault"
    item_id = vault_manager.store_file(session, "note.txt", original, "text/plain")

    recovered = vault_manager.retrieve_file(session, item_id)
    assert recovered == original


def test_store_and_retrieve_1mb_payload(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("perf_user", "pass123", conn) is True
    session = vault_manager.login("perf_user", "pass123", conn)
    assert session is not None

    payload = b"A" * (1024 * 1024)
    item_id = vault_manager.store_file(session, "large.bin", payload, "application/octet-stream")
    recovered = vault_manager.retrieve_file(session, item_id)

    assert recovered == payload


def test_signature_verification_gate_on_tamper(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("tamper_user", "pass123", conn) is True
    session = vault_manager.login("tamper_user", "pass123", conn)
    assert session is not None

    item_id = vault_manager.store_file(session, "secret.txt", b"very secret", "text/plain")

    row = conn.execute("SELECT ciphertext FROM vault_items WHERE id = ?", (item_id,)).fetchone()
    assert row is not None
    ciphertext = bytearray(row[0])
    ciphertext[0] ^= 0x01
    conn.execute("UPDATE vault_items SET ciphertext = ? WHERE id = ?", (bytes(ciphertext), item_id))
    conn.commit()

    with pytest.raises(vault_manager.IntegrityError):
        vault_manager.retrieve_file(session, item_id)


def test_wrong_user_cannot_retrieve_other_users_item(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("user_a", "pass123", conn) is True
    assert vault_manager.register("user_b", "pass456", conn) is True

    session_a = vault_manager.login("user_a", "pass123", conn)
    session_b = vault_manager.login("user_b", "pass456", conn)
    assert session_a is not None
    assert session_b is not None

    item_id = vault_manager.store_file(session_a, "a.txt", b"owned by a", "text/plain")

    assert vault_manager.retrieve_file(session_b, item_id) is None


def test_delete_item_flow(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("deleter", "pass123", conn) is True
    session = vault_manager.login("deleter", "pass123", conn)
    assert session is not None

    item_id = vault_manager.store_file(session, "to-delete.txt", b"bye", "text/plain")
    assert vault_manager.delete_file(session, item_id) is True
    assert vault_manager.retrieve_file(session, item_id) is None
