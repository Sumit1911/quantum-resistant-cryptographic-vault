"""Unit tests for core.crypto (Phase 1)."""

from __future__ import annotations

import secrets

import pytest
from cryptography.exceptions import InvalidTag

from core import crypto


HAS_OQS = crypto.oqs is not None


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_keypair_generation() -> None:
    """Kyber and Dilithium keypairs should be generated with expected structure."""
    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()

    assert isinstance(kyber_pk, bytes)
    assert isinstance(kyber_sk, bytes)
    assert isinstance(dil_pk, bytes)
    assert isinstance(dil_sk, bytes)

    # Kyber-512 lengths from liboqs spec.
    assert len(kyber_pk) == 800
    assert len(kyber_sk) == 1632


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_kyber_encap_decap_roundtrip() -> None:
    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()

    capsule, shared_secret_enc = crypto.kyber_encapsulate(kyber_pk)
    shared_secret_dec = crypto.kyber_decapsulate(capsule, kyber_sk)

    assert shared_secret_enc == shared_secret_dec
    assert isinstance(capsule, bytes)
    assert isinstance(shared_secret_enc, bytes)


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_kyber_decapsulate_wrong_private_key_mismatch() -> None:
    kyber_pk_1, _ = crypto.generate_kyber_keypair()
    _, kyber_sk_2 = crypto.generate_kyber_keypair()

    capsule, shared_secret_enc = crypto.kyber_encapsulate(kyber_pk_1)
    shared_secret_wrong = crypto.kyber_decapsulate(capsule, kyber_sk_2)

    assert shared_secret_wrong != shared_secret_enc


def test_aes_encrypt_decrypt_roundtrip() -> None:
    plaintext = b"quantum-resistant vault sample payload"
    key = secrets.token_bytes(crypto.AES_KEY_SIZE)

    iv, ciphertext, tag = crypto.aes_encrypt(plaintext, key)
    recovered = crypto.aes_decrypt(ciphertext, iv, tag, key)

    assert recovered == plaintext
    assert len(iv) == crypto.AES_IV_SIZE
    assert len(tag) == crypto.GCM_TAG_SIZE


def test_aes_decrypt_fails_on_ciphertext_tamper() -> None:
    plaintext = b"payload"
    key = secrets.token_bytes(crypto.AES_KEY_SIZE)

    iv, ciphertext, tag = crypto.aes_encrypt(plaintext, key)
    tampered = bytearray(ciphertext)
    tampered[0] ^= 0x01

    with pytest.raises(InvalidTag):
        crypto.aes_decrypt(bytes(tampered), iv, tag, key)


def test_aes_decrypt_fails_on_iv_tamper() -> None:
    plaintext = b"payload"
    key = secrets.token_bytes(crypto.AES_KEY_SIZE)

    iv, ciphertext, tag = crypto.aes_encrypt(plaintext, key)
    tampered_iv = bytearray(iv)
    tampered_iv[0] ^= 0x01

    with pytest.raises(InvalidTag):
        crypto.aes_decrypt(ciphertext, bytes(tampered_iv), tag, key)


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_dilithium_sign_verify_success() -> None:
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()
    payload = b"payload-to-sign"

    sig = crypto.dilithium_sign(payload, dil_sk)

    assert crypto.dilithium_verify(payload, sig, dil_pk) is True


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_dilithium_sign_verify_modified_payload_fails() -> None:
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()
    payload = b"payload-to-sign"

    sig = crypto.dilithium_sign(payload, dil_sk)
    tampered_payload = payload + b"!"

    assert crypto.dilithium_verify(tampered_payload, sig, dil_pk) is False


@pytest.mark.skipif(not HAS_OQS, reason="liboqs-python not installed")
def test_dilithium_verify_wrong_public_key_fails() -> None:
    _, dil_sk_1 = crypto.generate_dilithium_keypair()
    dil_pk_2, _ = crypto.generate_dilithium_keypair()
    payload = b"payload-to-sign"

    sig = crypto.dilithium_sign(payload, dil_sk_1)

    assert crypto.dilithium_verify(payload, sig, dil_pk_2) is False


def test_build_signing_payload_is_deterministic() -> None:
    ciphertext = b"ciphertext-bytes"
    capsule = b"capsule-bytes"
    item_name = "sample.txt"
    user_id = 42

    payload_1 = crypto.build_signing_payload(ciphertext, capsule, item_name, user_id)
    payload_2 = crypto.build_signing_payload(ciphertext, capsule, item_name, user_id)

    assert payload_1 == payload_2
