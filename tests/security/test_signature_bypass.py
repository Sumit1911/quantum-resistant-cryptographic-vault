"""Security tests against signature substitution/bypass attempts."""

from __future__ import annotations

from core import crypto, storage, vault_manager


def _setup_db(tmp_path):
    db_path = tmp_path / "security_signature.db"
    storage.init_db(str(db_path))
    return storage.get_connection(str(db_path))


def test_replace_signature_with_another_items_signature_detected(tmp_path) -> None:
    conn = _setup_db(tmp_path)
    assert vault_manager.register("alice", "pass123", conn)
    session = vault_manager.login("alice", "pass123", conn)
    assert session is not None

    item_1 = vault_manager.store_file(session, "one.txt", b"first", "text/plain")
    item_2 = vault_manager.store_file(session, "two.txt", b"second", "text/plain")

    sig_row = conn.execute(
        "SELECT dilithium_signature FROM vault_items WHERE id = ?",
        (item_2,),
    ).fetchone()
    assert sig_row is not None
    conn.execute(
        "UPDATE vault_items SET dilithium_signature = ? WHERE id = ?",
        (sig_row[0], item_1),
    )
    conn.commit()

    try:
        vault_manager.retrieve_file(session, item_1)
        assert False, "Expected IntegrityError"
    except vault_manager.IntegrityError:
        assert True


def test_verify_with_wrong_dilithium_public_key_returns_false() -> None:
    payload = b"payload-for-signature"
    pub_a, priv_a = crypto.generate_dilithium_keypair()
    pub_b, _ = crypto.generate_dilithium_keypair()

    signature = crypto.dilithium_sign(payload, priv_a)
    assert crypto.dilithium_verify(payload, signature, pub_a) is True
    assert crypto.dilithium_verify(payload, signature, pub_b) is False
