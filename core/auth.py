"""Authentication and password-based key protection logic."""

from __future__ import annotations

import os
import sqlite3

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core import crypto


ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 2
KEY_DERIVATION_SALT_SIZE = 16
PROTECTION_KEY_SIZE = 32
PBKDF2_ITERATIONS = 390_000
AES_GCM_IV_SIZE = 12


def _password_hasher() -> PasswordHasher:
    return PasswordHasher(
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
    )


def hash_master_password(password: str) -> str:
    """Hash master password using Argon2id."""
    return _password_hasher().hash(password)


def verify_master_password(password: str, stored_hash: str) -> bool:
    """Verify master password against an Argon2id hash."""
    try:
        return _password_hasher().verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def derive_protection_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from password and salt using PBKDF2-HMAC-SHA256."""
    if len(salt) != KEY_DERIVATION_SALT_SIZE:
        raise ValueError(f"salt must be {KEY_DERIVATION_SALT_SIZE} bytes")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=PROTECTION_KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def wrap_private_key(private_key_bytes: bytes, protection_key: bytes) -> tuple[bytes, bytes]:
    """Encrypt private key bytes using AES-256-GCM.

    Returns:
        (iv, ciphertext_with_tag)
    """
    if len(protection_key) != PROTECTION_KEY_SIZE:
        raise ValueError(f"protection_key must be {PROTECTION_KEY_SIZE} bytes")

    iv = os.urandom(AES_GCM_IV_SIZE)
    aesgcm = AESGCM(protection_key)
    ciphertext = aesgcm.encrypt(iv, private_key_bytes, associated_data=None)
    return iv, ciphertext


def unwrap_private_key(ciphertext: bytes, iv: bytes, protection_key: bytes) -> bytes:
    """Decrypt wrapped private key bytes using AES-256-GCM."""
    if len(protection_key) != PROTECTION_KEY_SIZE:
        raise ValueError(f"protection_key must be {PROTECTION_KEY_SIZE} bytes")
    if len(iv) != AES_GCM_IV_SIZE:
        raise ValueError(f"iv must be {AES_GCM_IV_SIZE} bytes")

    aesgcm = AESGCM(protection_key)
    return aesgcm.decrypt(iv, ciphertext, associated_data=None)


def register_user(username: str, password: str, db_conn: sqlite3.Connection) -> bool:
    """Register a user and store wrapped PQC private keys."""
    password_hash = hash_master_password(password)
    kdf_salt = os.urandom(KEY_DERIVATION_SALT_SIZE)
    protection_key = derive_protection_key(password, kdf_salt)

    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()

    kyber_iv, kyber_sk_enc = wrap_private_key(kyber_sk, protection_key)
    dil_iv, dil_sk_enc = wrap_private_key(dil_sk, protection_key)

    db_conn.execute(
        """
        INSERT INTO users (
            username, password_hash,
            kyber_public_key, kyber_private_key,
            dilithium_public_key, dilithium_private_key,
            kdf_salt, kyber_private_key_iv, dilithium_private_key_iv
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            password_hash,
            kyber_pk,
            kyber_sk_enc,
            dil_pk,
            dil_sk_enc,
            kdf_salt,
            kyber_iv,
            dil_iv,
        ),
    )
    db_conn.commit()
    return True


def login_user(username: str, password: str, db_conn: sqlite3.Connection) -> dict | None:
    """Authenticate user and return decrypted key material in memory."""
    row = db_conn.execute(
        """
        SELECT id, password_hash,
               kyber_public_key, kyber_private_key,
               dilithium_public_key, dilithium_private_key,
               kdf_salt, kyber_private_key_iv, dilithium_private_key_iv
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()

    if row is None:
        return None

    (
        user_id,
        password_hash,
        kyber_pk,
        kyber_sk_wrapped,
        dil_pk,
        dil_sk_wrapped,
        kdf_salt,
        kyber_iv,
        dil_iv,
    ) = row

    if not verify_master_password(password, password_hash):
        return None

    protection_key = derive_protection_key(password, kdf_salt)
    try:
        kyber_sk = unwrap_private_key(kyber_sk_wrapped, kyber_iv, protection_key)
        dil_sk = unwrap_private_key(dil_sk_wrapped, dil_iv, protection_key)
    except Exception:
        # Fail closed on unwrap/authentication errors (wrong password/corrupted blob).
        return None

    return {
        "user_id": user_id,
        "kyber_pk": kyber_pk,
        "kyber_sk": kyber_sk,
        "dil_pk": dil_pk,
        "dil_sk": dil_sk,
        "dilithium_pk": dil_pk,
        "dilithium_sk": dil_sk,
    }
