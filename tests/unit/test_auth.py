"""Unit tests for core.auth (Phase 2)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag

from core import auth


def _init_in_memory_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    schema_path = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def test_hash_and_verify_password() -> None:
    password = "CorrectHorseBatteryStaple!"
    stored_hash = auth.hash_master_password(password)

    assert auth.verify_master_password(password, stored_hash) is True
    assert auth.verify_master_password("wrong-password", stored_hash) is False


def test_hash_same_password_twice_is_randomized() -> None:
    password = "same-password"
    hash_1 = auth.hash_master_password(password)
    hash_2 = auth.hash_master_password(password)

    assert hash_1 != hash_2


def test_derive_protection_key_is_deterministic_for_same_inputs() -> None:
    password = "master-password"
    salt = b"1234567890abcdef"

    key_1 = auth.derive_protection_key(password, salt)
    key_2 = auth.derive_protection_key(password, salt)

    assert key_1 == key_2
    assert len(key_1) == auth.PROTECTION_KEY_SIZE


def test_wrap_and_unwrap_private_key_roundtrip() -> None:
    key_material = b"private-key-bytes"
    protection_key = b"k" * auth.PROTECTION_KEY_SIZE

    iv, wrapped = auth.wrap_private_key(key_material, protection_key)
    recovered = auth.unwrap_private_key(wrapped, iv, protection_key)

    assert recovered == key_material


def test_unwrap_private_key_with_wrong_key_raises() -> None:
    key_material = b"private-key-bytes"
    correct_key = b"a" * auth.PROTECTION_KEY_SIZE
    wrong_key = b"b" * auth.PROTECTION_KEY_SIZE

    iv, wrapped = auth.wrap_private_key(key_material, correct_key)

    with pytest.raises(InvalidTag):
        auth.unwrap_private_key(wrapped, iv, wrong_key)


def test_register_then_login_returns_expected_session(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = _init_in_memory_db()

    expected_kyber_pk = b"K" * 800
    expected_kyber_sk = b"k" * 1632
    expected_dil_pk = b"D" * 32
    expected_dil_sk = b"d" * 64

    monkeypatch.setattr(
        auth.crypto,
        "generate_kyber_keypair",
        lambda: (expected_kyber_pk, expected_kyber_sk),
    )
    monkeypatch.setattr(
        auth.crypto,
        "generate_dilithium_keypair",
        lambda: (expected_dil_pk, expected_dil_sk),
    )

    assert auth.register_user("alice", "pass123", conn) is True

    session = auth.login_user("alice", "pass123", conn)
    assert session is not None
    assert session["kyber_pk"] == expected_kyber_pk
    assert session["kyber_sk"] == expected_kyber_sk
    assert session["dilithium_pk"] == expected_dil_pk
    assert session["dilithium_sk"] == expected_dil_sk


def test_login_with_wrong_password_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = _init_in_memory_db()

    monkeypatch.setattr(auth.crypto, "generate_kyber_keypair", lambda: (b"K" * 800, b"k" * 1632))
    monkeypatch.setattr(auth.crypto, "generate_dilithium_keypair", lambda: (b"D" * 32, b"d" * 64))

    auth.register_user("bob", "correct-password", conn)

    assert auth.login_user("bob", "wrong-password", conn) is None


def test_register_duplicate_username_raises_integrity_error(monkeypatch: pytest.MonkeyPatch) -> None:
    conn = _init_in_memory_db()

    monkeypatch.setattr(auth.crypto, "generate_kyber_keypair", lambda: (b"K" * 800, b"k" * 1632))
    monkeypatch.setattr(auth.crypto, "generate_dilithium_keypair", lambda: (b"D" * 32, b"d" * 64))

    auth.register_user("charlie", "password", conn)

    with pytest.raises(sqlite3.IntegrityError):
        auth.register_user("charlie", "another-password", conn)
