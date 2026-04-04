"""Unit tests to improve vault_manager and edge-path coverage."""

from __future__ import annotations

import pytest

from core import auth, crypto, storage, vault_manager


def _conn(tmp_path):
    db_path = tmp_path / "vault_manager_unit.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_vault_manager_login_none_and_list_files(tmp_path) -> None:
    conn = _conn(tmp_path)
    assert vault_manager.login("missing", "bad", conn) is None

    assert vault_manager.register("alice", "pass123", conn)
    session = vault_manager.login("alice", "pass123", conn)
    assert session is not None
    assert vault_manager.list_files(session) == []


def test_change_master_password_success_and_failures(tmp_path) -> None:
    conn = _conn(tmp_path)
    assert vault_manager.register("bob", "oldpass", conn)
    session = vault_manager.login("bob", "oldpass", conn)
    assert session is not None

    # Wrong old password path
    assert vault_manager.change_master_password(session, "wrong", "newpass") is False

    # Success path
    assert vault_manager.change_master_password(session, "oldpass", "newpass") is True

    # old password should no longer work
    assert vault_manager.login("bob", "oldpass", conn) is None
    # new password should work
    assert vault_manager.login("bob", "newpass", conn) is not None


def test_change_master_password_missing_user_returns_false(tmp_path) -> None:
    conn = _conn(tmp_path)
    fake_session = {"user_id": 9999, "db_conn": conn}
    assert vault_manager.change_master_password(fake_session, "a", "b") is False


def test_auth_and_crypto_and_storage_error_paths(tmp_path) -> None:
    # auth guards
    with pytest.raises(ValueError):
        auth.derive_protection_key("pw", b"short")
    with pytest.raises(ValueError):
        auth.wrap_private_key(b"k", b"short")
    with pytest.raises(ValueError):
        auth.unwrap_private_key(b"ct", b"123456789012", b"short")
    with pytest.raises(ValueError):
        auth.unwrap_private_key(b"ct", b"short", b"x" * auth.PROTECTION_KEY_SIZE)

    # crypto guards
    with pytest.raises(ValueError):
        crypto.aes_encrypt(b"pt", b"short")
    with pytest.raises(ValueError):
        crypto.aes_decrypt(b"ct", b"123456789012", b"1234567890abcdef", b"short")
    with pytest.raises(ValueError):
        crypto.aes_decrypt(b"ct", b"short", b"1234567890abcdef", b"x" * crypto.AES_KEY_SIZE)
    with pytest.raises(ValueError):
        crypto.aes_decrypt(b"ct", b"123456789012", b"short", b"x" * crypto.AES_KEY_SIZE)

    # storage path error path
    with pytest.raises(Exception):
        storage.init_db("/Users/yasmodi/Documents/Project/db/does/not/exist/vault.db")
