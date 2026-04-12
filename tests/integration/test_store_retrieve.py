"""Focused integration tests for store/retrieve flows."""

from __future__ import annotations

from core import storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "store_retrieve.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_store_and_retrieve_text_file_roundtrip(tmp_path) -> None:
    conn = _setup_db(tmp_path)

    assert vault_manager.register("alice_sr", "pass123", conn) is True
    session = vault_manager.login("alice_sr", "pass123", conn)
    assert session is not None

    original = b"store-retrieve integration payload"
    item_id = vault_manager.store_file(session, "payload.txt", original, "text/plain")
    recovered = vault_manager.retrieve_file(session, item_id)

    assert recovered == original


def test_retrieve_missing_item_returns_none(tmp_path) -> None:
    conn = _setup_db(tmp_path)

    assert vault_manager.register("bob_sr", "pass123", conn) is True
    session = vault_manager.login("bob_sr", "pass123", conn)
    assert session is not None

    assert vault_manager.retrieve_file(session, 999999) is None
