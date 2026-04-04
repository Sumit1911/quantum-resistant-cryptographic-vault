"""Security test for cross-user access rejection."""

from __future__ import annotations

from core import storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "security_wrong_key.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_user_b_cannot_retrieve_user_a_item(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("user_a", "pass_a", conn)
    assert vault_manager.register("user_b", "pass_b", conn)

    session_a = vault_manager.login("user_a", "pass_a", conn)
    session_b = vault_manager.login("user_b", "pass_b", conn)
    assert session_a is not None
    assert session_b is not None

    item_id = vault_manager.store_file(session_a, "a.txt", b"owned by a", "text/plain")
    assert vault_manager.retrieve_file(session_b, item_id) is None
