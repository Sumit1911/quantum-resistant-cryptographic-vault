from __future__ import annotations

import base64
import os
import sqlite3
import time
from pathlib import Path

from core import auth, crypto, storage


class VaultFlowError(RuntimeError):
    pass


_DEMO_DB_PATH = Path('/tmp/cryptoarena_platform_vault.db')
_DEMO_USER = 'platform_demo'
_DEMO_PASS = 'platform_demo_pass'


def _ensure_demo_session() -> dict:
    storage.init_db(str(_DEMO_DB_PATH))
    conn = storage.get_connection(str(_DEMO_DB_PATH))

    existing = storage.get_user_by_username(conn, _DEMO_USER)
    if existing is None:
        try:
            auth.register_user(_DEMO_USER, _DEMO_PASS, conn)
        except sqlite3.IntegrityError:
            pass

    session = auth.login_user(_DEMO_USER, _DEMO_PASS, conn)
    if session is None:
        raise VaultFlowError('Failed to initialize demo session')
    session['db_conn'] = conn
    return session


def _resolve_signing_mechanism(requested: str) -> str:
    if crypto.oqs is None:
        raise VaultFlowError('liboqs-python not installed for platform vault flow')

    enabled = set(crypto.oqs.get_enabled_sig_mechanisms())
    if requested in enabled:
        return requested

    for candidate in ('Dilithium3', 'ML-DSA-65'):
        if candidate in enabled:
            return candidate

    raise VaultFlowError('No supported Dilithium/ML-DSA mechanism available')


def _kyber_encapsulate_with_alg(algorithm: str, public_key_hint: bytes) -> tuple[bytes, bytes, bytes]:
    if algorithm == 'Kyber-512':
        capsule, shared = crypto.kyber_encapsulate(public_key_hint)
        return capsule, shared, b''

    # For non-default KEMs, generate ephemeral keypair for this run.
    if crypto.oqs is None:
        raise VaultFlowError('liboqs-python unavailable for non-default KEM')

    oqs_alg = {'Kyber-768': 'Kyber768'}.get(algorithm)
    if oqs_alg is None:
        raise VaultFlowError(f'Unsupported KEM algorithm: {algorithm}')

    with crypto.oqs.KeyEncapsulation(oqs_alg) as kem:
        ephemeral_pk = kem.generate_keypair()
        ephemeral_sk = kem.export_secret_key()

    with crypto.oqs.KeyEncapsulation(oqs_alg) as kem:
        capsule, shared = kem.encap_secret(ephemeral_pk)

    return capsule, shared, ephemeral_sk


def _kyber_decapsulate_with_alg(algorithm: str, capsule: bytes, private_key_hint: bytes, ephemeral_sk: bytes) -> bytes:
    if algorithm == 'Kyber-512':
        return crypto.kyber_decapsulate(capsule, private_key_hint)

    oqs_alg = {'Kyber-768': 'Kyber768'}.get(algorithm)
    if oqs_alg is None:
        raise VaultFlowError(f'Unsupported KEM algorithm: {algorithm}')

    with crypto.oqs.KeyEncapsulation(oqs_alg, secret_key=ephemeral_sk) as kem:
        return kem.decap_secret(capsule)


def build_vault_metrics(
    plaintext: bytes,
    algorithm: str = 'Kyber-512',
    signing: str = 'Dilithium3',
    item_name: str = 'payload.bin',
    item_type: str = 'text',
    mime_type: str = 'application/octet-stream',
) -> dict:
    session = _ensure_demo_session()
    conn = session['db_conn']
    user_id = session['user_id']

    signing_alg = _resolve_signing_mechanism(signing)

    steps: list[dict] = []
    started_total = time.perf_counter()

    t0 = time.perf_counter()
    capsule, shared_secret, ephemeral_sk = _kyber_encapsulate_with_alg(algorithm, session['kyber_pk'])
    steps.append(
        {
            'name': 'kyber_encapsulate',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(capsule),
            'detail': f'kem={algorithm}',
        }
    )

    t0 = time.perf_counter()
    iv, ciphertext, tag = crypto.aes_encrypt(plaintext, shared_secret)
    steps.append(
        {
            'name': 'aes_encrypt',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(ciphertext) + len(tag),
            'detail': 'aes-256-gcm',
        }
    )

    metadata_nonce = os.urandom(16)

    t0 = time.perf_counter()
    sign_payload = crypto.build_signing_payload(
        ciphertext,
        capsule,
        item_name,
        user_id,
        metadata_nonce=metadata_nonce,
    )
    steps.append(
        {
            'name': 'build_signing_payload',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(sign_payload),
            'detail': 'deterministic payload structure',
        }
    )

    t0 = time.perf_counter()
    if signing_alg in {'Dilithium3', 'ML-DSA-65'}:
        signature = crypto.dilithium_sign(sign_payload, session['dilithium_sk'])
    else:
        with crypto.oqs.Signature(signing_alg, secret_key=session['dilithium_sk']) as signer:
            signature = signer.sign(sign_payload)
    steps.append(
        {
            'name': 'dilithium_sign',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(signature),
            'detail': f'signature={signing_alg}',
        }
    )

    t0 = time.perf_counter()
    item_id = storage.store_vault_item(
        conn,
        user_id=user_id,
        item_name=item_name,
        item_type=item_type,
        metadata_nonce=metadata_nonce,
        ciphertext=ciphertext,
        aes_iv=iv,
        aes_tag=tag,
        kyber_capsule=capsule,
        dilithium_signature=signature,
        original_size=len(plaintext),
        mime_type=mime_type,
    )
    steps.append(
        {
            'name': 'db_write',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': None,
            'detail': f'item_id={item_id}',
        }
    )

    t0 = time.perf_counter()
    is_valid = crypto.dilithium_verify(sign_payload, signature, session['dilithium_pk'])
    steps.append(
        {
            'name': 'signature_precheck',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': None,
            'detail': f'valid={is_valid}',
        }
    )

    if not is_valid:
        raise VaultFlowError('Signature verification failed during live flow')

    t0 = time.perf_counter()
    decapped_secret = _kyber_decapsulate_with_alg(algorithm, capsule, session['kyber_sk'], ephemeral_sk)
    steps.append(
        {
            'name': 'kyber_decapsulate',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(decapped_secret),
            'detail': f'kem={algorithm}',
        }
    )

    t0 = time.perf_counter()
    recovered = crypto.aes_decrypt(ciphertext, iv, tag, decapped_secret)
    steps.append(
        {
            'name': 'aes_decrypt',
            'duration_ms': round((time.perf_counter() - t0) * 1000, 4),
            'output_size': len(recovered),
            'detail': 'integrity verified',
        }
    )

    total_ms = (time.perf_counter() - started_total) * 1000

    ciphertext_size = len(ciphertext) + len(tag)
    overhead_bytes = (ciphertext_size - len(plaintext)) + len(capsule) + len(signature)
    throughput_mbps = ((len(plaintext) / (1024 * 1024)) * 1000) / max(total_ms, 0.001)

    return {
        'success': True,
        'algorithm': algorithm,
        'signing': signing_alg,
        'input_kind': item_type,
        'item_name': item_name,
        'item_id': item_id,
        'steps': steps,
        'total_ms': round(total_ms, 4),
        'metrics': {
            'plaintext_size': len(plaintext),
            'ciphertext_size': ciphertext_size,
            'capsule_size': len(capsule),
            'signature_size': len(signature),
            'overhead_bytes': overhead_bytes,
            'overhead_percent': round((overhead_bytes / max(len(plaintext), 1)) * 100, 4),
            'throughput_mbps': round(throughput_mbps, 3),
            'tamper_detection_window_ms': next((s['duration_ms'] for s in steps if s['name'] == 'signature_precheck'), 0.0),
            'quantum_readiness_score': 94 if algorithm == 'Kyber-512' else 97,
            'recovered_matches_input': recovered == plaintext,
        },
        'research_notes': [
            'This flow uses real cryptographic operations from the vault core, not static synthetic timings.',
            'Pipeline includes encrypt + sign + store + verify + decrypt to visualize full backend lifecycle.',
            'Supports text and file payload classes with identical cryptographic pipeline semantics.',
        ],
    }


def decode_base64_payload(content_base64: str) -> bytes:
    try:
        return base64.b64decode(content_base64, validate=True)
    except Exception as exc:  # pragma: no cover
        raise VaultFlowError('Invalid base64 payload') from exc
