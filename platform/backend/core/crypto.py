"""Cryptographic primitives for the quantum-resistant vault.

This module centralizes all direct interactions with:
- liboqs-python (Kyber + Dilithium)
- cryptography (AES-256-GCM)
"""

from __future__ import annotations

import os
import struct

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    import oqs
except ModuleNotFoundError:  # pragma: no cover - covered by runtime guard tests/environments
    oqs = None  # type: ignore[assignment]


KYBER_ALG = "Kyber512"
# liboqs naming varies by version (legacy "Dilithium3" vs NIST "ML-DSA-65").
DILITHIUM_CANDIDATES = ("Dilithium3", "ML-DSA-65")
AES_KEY_SIZE = 32
AES_IV_SIZE = 12
GCM_TAG_SIZE = 16


def _require_oqs() -> None:
    """Ensure liboqs-python is available before PQC operations."""
    if oqs is None:
        raise RuntimeError(
            "liboqs-python is not installed. Install Phase 0 dependencies first."
        )


def _resolve_dilithium_alg() -> str:
    """Return the first supported Dilithium/ML-DSA mechanism name."""
    _require_oqs()
    enabled = set(oqs.get_enabled_sig_mechanisms())
    for candidate in DILITHIUM_CANDIDATES:
        if candidate in enabled:
            return candidate
    raise RuntimeError(
        "No supported Dilithium/ML-DSA mechanism found in liboqs build. "
        f"Checked: {', '.join(DILITHIUM_CANDIDATES)}"
    )


def generate_kyber_keypair() -> tuple[bytes, bytes]:
    """Generate and return a Kyber-512 keypair as (public_key, private_key)."""
    _require_oqs()

    with oqs.KeyEncapsulation(KYBER_ALG) as kem:
        public_key = kem.generate_keypair()
        private_key = kem.export_secret_key()
    return public_key, private_key


def generate_dilithium_keypair() -> tuple[bytes, bytes]:
    """Generate and return a Dilithium keypair as (public_key, private_key)."""
    dilithium_alg = _resolve_dilithium_alg()

    with oqs.Signature(dilithium_alg) as signer:
        public_key = signer.generate_keypair()
        private_key = signer.export_secret_key()
    return public_key, private_key


def kyber_encapsulate(kyber_public_key: bytes) -> tuple[bytes, bytes]:
    """Encapsulate a fresh shared secret for the provided Kyber public key."""
    _require_oqs()

    with oqs.KeyEncapsulation(KYBER_ALG) as kem:
        capsule, shared_secret = kem.encap_secret(kyber_public_key)
    return capsule, shared_secret


def kyber_decapsulate(capsule: bytes, kyber_private_key: bytes) -> bytes:
    """Decapsulate and return the shared secret from capsule + private key."""
    _require_oqs()

    with oqs.KeyEncapsulation(KYBER_ALG, secret_key=kyber_private_key) as kem:
        return kem.decap_secret(capsule)


def aes_encrypt(plaintext: bytes, session_key: bytes) -> tuple[bytes, bytes, bytes]:
    """Encrypt plaintext with AES-256-GCM.

    Returns:
        (iv, ciphertext, tag)
    """
    if len(session_key) != AES_KEY_SIZE:
        raise ValueError(f"session_key must be {AES_KEY_SIZE} bytes")

    iv = os.urandom(AES_IV_SIZE)
    aesgcm = AESGCM(session_key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, associated_data=None)
    ciphertext, tag = (
        ciphertext_with_tag[:-GCM_TAG_SIZE],
        ciphertext_with_tag[-GCM_TAG_SIZE:],
    )
    return iv, ciphertext, tag


def aes_decrypt(ciphertext: bytes, iv: bytes, tag: bytes, session_key: bytes) -> bytes:
    """Decrypt AES-256-GCM ciphertext.

    Raises:
        cryptography.exceptions.InvalidTag: if integrity/authentication fails.
    """
    if len(session_key) != AES_KEY_SIZE:
        raise ValueError(f"session_key must be {AES_KEY_SIZE} bytes")
    if len(iv) != AES_IV_SIZE:
        raise ValueError(f"iv must be {AES_IV_SIZE} bytes")
    if len(tag) != GCM_TAG_SIZE:
        raise ValueError(f"tag must be {GCM_TAG_SIZE} bytes")

    aesgcm = AESGCM(session_key)
    return aesgcm.decrypt(iv, ciphertext + tag, associated_data=None)


def dilithium_sign(payload: bytes, dilithium_private_key: bytes) -> bytes:
    """Sign payload with Dilithium private key and return signature bytes."""
    dilithium_alg = _resolve_dilithium_alg()

    with oqs.Signature(dilithium_alg, secret_key=dilithium_private_key) as signer:
        return signer.sign(payload)


def dilithium_verify(
    payload: bytes, signature: bytes, dilithium_public_key: bytes
) -> bool:
    """Verify Dilithium signature for payload and public key."""
    dilithium_alg = _resolve_dilithium_alg()

    with oqs.Signature(dilithium_alg) as verifier:
        return verifier.verify(payload, signature, dilithium_public_key)


def build_signing_payload(
    ciphertext: bytes,
    capsule: bytes,
    item_name: str,
    user_id: int,
    metadata_nonce: bytes = b"",
) -> bytes:
    """Build a deterministic signed payload with explicit length prefixes."""
    name_bytes = item_name.encode("utf-8")

    # Layout:
    # [user_id:u64][name_len:u32][name][nonce_len:u32][nonce]
    # [cipher_len:u32][cipher][capsule_len:u32][capsule]
    return b"".join(
        (
            struct.pack(">Q", user_id),
            struct.pack(">I", len(name_bytes)),
            name_bytes,
            struct.pack(">I", len(metadata_nonce)),
            metadata_nonce,
            struct.pack(">I", len(ciphertext)),
            ciphertext,
            struct.pack(">I", len(capsule)),
            capsule,
        )
    )
