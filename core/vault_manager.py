"""High-level orchestration for auth + crypto + storage flows."""

from __future__ import annotations

from core import auth, crypto, storage


class IntegrityError(Exception):
    """Raised when signature verification fails for stored vault data."""


def _zero_bytes(secret: bytearray) -> None:
    for i in range(len(secret)):
        secret[i] = 0


def register(username: str, password: str, db_conn) -> bool:
    """Register a new user."""
    return auth.register_user(username, password, db_conn)


def login(username: str, password: str, db_conn) -> dict | None:
    """Login user and return in-memory session."""
    session = auth.login_user(username, password, db_conn)
    if session is None:
        return None
    session["db_conn"] = db_conn
    return session


def store_file(session: dict, file_name: str, file_bytes: bytes, mime_type: str) -> int:
    """Encrypt + sign + store a file for the authenticated user."""
    user_id = session["user_id"]
    conn = session["db_conn"]

    capsule, shared_secret = crypto.kyber_encapsulate(session["kyber_pk"])
    shared_secret_buf = bytearray(shared_secret)
    try:
        iv, ciphertext, tag = crypto.aes_encrypt(file_bytes, bytes(shared_secret_buf))
    finally:
        _zero_bytes(shared_secret_buf)

    payload = crypto.build_signing_payload(ciphertext, capsule, file_name, user_id)
    signature = crypto.dilithium_sign(payload, session["dilithium_sk"])

    return storage.store_vault_item(
        conn,
        user_id=user_id,
        item_name=file_name,
        item_type="file",
        ciphertext=ciphertext,
        aes_iv=iv,
        aes_tag=tag,
        kyber_capsule=capsule,
        dilithium_signature=signature,
        original_size=len(file_bytes),
        mime_type=mime_type,
    )


def retrieve_file(session: dict, item_id: int) -> bytes | None:
    """Verify signature first, then decapsulate and decrypt file bytes."""
    user_id = session["user_id"]
    conn = session["db_conn"]

    item = storage.get_vault_item(conn, item_id, user_id)
    if item is None:
        return None

    payload = crypto.build_signing_payload(
        item.ciphertext or b"",
        item.kyber_capsule or b"",
        item.item_name,
        user_id,
    )
    is_valid = crypto.dilithium_verify(payload, item.dilithium_signature or b"", session["dilithium_pk"])
    if not is_valid:
        raise IntegrityError("Vault item integrity check failed")

    shared_secret = crypto.kyber_decapsulate(item.kyber_capsule or b"", session["kyber_sk"])
    shared_secret_buf = bytearray(shared_secret)
    try:
        return crypto.aes_decrypt(
            item.ciphertext or b"",
            item.aes_iv or b"",
            item.aes_tag or b"",
            bytes(shared_secret_buf),
        )
    finally:
        _zero_bytes(shared_secret_buf)


def delete_file(session: dict, item_id: int) -> bool:
    """Delete a user's file by id."""
    return storage.delete_vault_item(session["db_conn"], item_id, session["user_id"])


def list_files(session: dict) -> list:
    """List metadata-only file entries for authenticated user."""
    return storage.list_vault_items(session["db_conn"], session["user_id"])
