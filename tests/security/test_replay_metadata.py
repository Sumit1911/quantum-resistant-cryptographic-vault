"""Security tests for replay-resistant metadata nonce handling."""

from __future__ import annotations

import pytest

from core import storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "security_replay.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_replayed_metadata_nonce_is_rejected(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("alice", "pass123", conn)
    session = vault_manager.login("alice", "pass123", conn)
    assert session is not None

    item_1 = vault_manager.store_file(session, "one.txt", b"first", "text/plain")
    item_2 = vault_manager.store_file(session, "two.txt", b"second", "text/plain")

    nonce_row = conn.execute(
        "SELECT metadata_nonce FROM vault_items WHERE id = ?",
        (item_2,),
    ).fetchone()
    assert nonce_row is not None
    conn.execute(
        "UPDATE vault_items SET metadata_nonce = ? WHERE id = ?",
        (nonce_row[0], item_1),
    )
    conn.commit()

    with pytest.raises(vault_manager.IntegrityError):
        vault_manager.retrieve_file(session, item_1)
