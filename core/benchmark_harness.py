"""Reproducible benchmark harness for storage-flow baselines.

Runs multi-trial measurements for:
1) RSA-2048 + AES-GCM + ECDSA
2) AES-only flow
3) PQC flow (ML-KEM + ML-DSA + AES-GCM)
"""

from __future__ import annotations

import json
import math
import os
import random
import statistics
import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

from core import crypto


BASELINE_RSA = "rsa2048_aesgcm_ecdsa"
BASELINE_AES = "aes_only"
BASELINE_PQC = "mlkem_mldsa_aesgcm"
ALL_BASELINES = (BASELINE_RSA, BASELINE_AES, BASELINE_PQC)


@dataclass
class TrialMetrics:
    latency_ms: float
    throughput_mbps: float
    ciphertext_overhead_bytes: int
    capsule_signature_overhead_bytes: int
    peak_memory_bytes: int
    cpu_usage_percent: float
    tamper_blocked: bool
    wrong_key_blocked: bool


def _p95(samples: list[float]) -> float:
    ordered = sorted(samples)
    idx = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[idx]


def _payload(seed_rng: random.Random, size_bytes: int) -> bytes:
    return seed_rng.randbytes(size_bytes)


def _aes_encrypt_decrypt(payload: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    iv, ciphertext, tag = crypto.aes_encrypt(payload, key)
    recovered = crypto.aes_decrypt(ciphertext, iv, tag, key)
    if recovered != payload:
        raise RuntimeError("AES roundtrip mismatch")
    return iv, ciphertext, tag


def _run_trial_aes_only(payload: bytes, wrong_key: bytes) -> TrialMetrics:
    key = os.urandom(crypto.AES_KEY_SIZE)

    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    tracemalloc.start()
    try:
        iv, ciphertext, tag = _aes_encrypt_decrypt(payload, key)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    wall_s = time.perf_counter() - wall_start
    cpu_s = time.process_time() - cpu_start

    tamper_blocked = True
    tampered = bytearray(ciphertext)
    tampered[0] ^= 0x01
    try:
        crypto.aes_decrypt(bytes(tampered), iv, tag, key)
        tamper_blocked = False
    except InvalidTag:
        tamper_blocked = True

    wrong_key_blocked = True
    try:
        crypto.aes_decrypt(ciphertext, iv, tag, wrong_key)
        wrong_key_blocked = False
    except InvalidTag:
        wrong_key_blocked = True

    latency_ms = wall_s * 1000.0
    throughput_mbps = (len(payload) / (1024 * 1024)) / max(wall_s, 1e-9)
    cpu_usage_percent = (cpu_s / max(wall_s, 1e-9)) * 100.0

    return TrialMetrics(
        latency_ms=latency_ms,
        throughput_mbps=throughput_mbps,
        ciphertext_overhead_bytes=(len(ciphertext) - len(payload)) + len(tag),
        capsule_signature_overhead_bytes=0,
        peak_memory_bytes=peak,
        cpu_usage_percent=cpu_usage_percent,
        tamper_blocked=tamper_blocked,
        wrong_key_blocked=wrong_key_blocked,
    )


def _run_trial_rsa_classical(
    payload: bytes,
    rsa_public_key,
    rsa_private_key,
    rsa_private_key_wrong,
    ecdsa_private_key,
    ecdsa_public_key,
) -> TrialMetrics:
    session_key = os.urandom(32)
    metadata_nonce = os.urandom(16)

    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    tracemalloc.start()
    try:
        encrypted_session_key = rsa_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        iv, ciphertext, tag = crypto.aes_encrypt(payload, session_key)
        sign_payload = b"|".join((metadata_nonce, encrypted_session_key, ciphertext, tag))
        signature = ecdsa_private_key.sign(sign_payload, ec.ECDSA(hashes.SHA256()))
        ecdsa_public_key.verify(signature, sign_payload, ec.ECDSA(hashes.SHA256()))
        recovered_key = rsa_private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        recovered = crypto.aes_decrypt(ciphertext, iv, tag, recovered_key)
        if recovered != payload:
            raise RuntimeError("RSA baseline roundtrip mismatch")
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    wall_s = time.perf_counter() - wall_start
    cpu_s = time.process_time() - cpu_start

    tamper_blocked = True
    tampered_cipher = bytearray(ciphertext)
    tampered_cipher[0] ^= 0x01
    tampered_payload = b"|".join((metadata_nonce, encrypted_session_key, bytes(tampered_cipher), tag))
    try:
        ecdsa_public_key.verify(signature, tampered_payload, ec.ECDSA(hashes.SHA256()))
        # If signature verification somehow passes, decryption still must fail.
        crypto.aes_decrypt(bytes(tampered_cipher), iv, tag, session_key)
        tamper_blocked = False
    except (InvalidSignature, InvalidTag):
        tamper_blocked = True

    wrong_key_blocked = True
    try:
        wrong_key = rsa_private_key_wrong.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        crypto.aes_decrypt(ciphertext, iv, tag, wrong_key)
        wrong_key_blocked = False
    except Exception:
        wrong_key_blocked = True

    latency_ms = wall_s * 1000.0
    throughput_mbps = (len(payload) / (1024 * 1024)) / max(wall_s, 1e-9)
    cpu_usage_percent = (cpu_s / max(wall_s, 1e-9)) * 100.0

    return TrialMetrics(
        latency_ms=latency_ms,
        throughput_mbps=throughput_mbps,
        ciphertext_overhead_bytes=(len(ciphertext) - len(payload)) + len(tag),
        capsule_signature_overhead_bytes=len(encrypted_session_key) + len(signature),
        peak_memory_bytes=peak,
        cpu_usage_percent=cpu_usage_percent,
        tamper_blocked=tamper_blocked,
        wrong_key_blocked=wrong_key_blocked,
    )


def _run_trial_pqc(
    payload: bytes,
    kyber_public_key: bytes,
    kyber_private_key: bytes,
    kyber_private_key_wrong: bytes,
    dilithium_private_key: bytes,
    dilithium_public_key: bytes,
) -> TrialMetrics:
    item_name = "bench.bin"
    user_id = 1
    metadata_nonce = os.urandom(16)

    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    tracemalloc.start()
    try:
        capsule, shared_secret = crypto.kyber_encapsulate(kyber_public_key)
        iv, ciphertext, tag = crypto.aes_encrypt(payload, shared_secret)
        sign_payload = crypto.build_signing_payload(
            ciphertext,
            capsule,
            item_name,
            user_id,
            metadata_nonce=metadata_nonce,
        )
        signature = crypto.dilithium_sign(sign_payload, dilithium_private_key)
        if not crypto.dilithium_verify(sign_payload, signature, dilithium_public_key):
            raise RuntimeError("PQC signature verify failed")
        recovered_secret = crypto.kyber_decapsulate(capsule, kyber_private_key)
        recovered = crypto.aes_decrypt(ciphertext, iv, tag, recovered_secret)
        if recovered != payload:
            raise RuntimeError("PQC baseline roundtrip mismatch")
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    wall_s = time.perf_counter() - wall_start
    cpu_s = time.process_time() - cpu_start

    tamper_payload = crypto.build_signing_payload(
        bytes(bytearray(ciphertext[:-1]) + bytes([ciphertext[-1] ^ 0x01])),
        capsule,
        item_name,
        user_id,
        metadata_nonce=metadata_nonce,
    )
    tamper_blocked = not crypto.dilithium_verify(tamper_payload, signature, dilithium_public_key)

    wrong_key_blocked = True
    try:
        wrong_secret = crypto.kyber_decapsulate(capsule, kyber_private_key_wrong)
        crypto.aes_decrypt(ciphertext, iv, tag, wrong_secret)
        wrong_key_blocked = False
    except InvalidTag:
        wrong_key_blocked = True

    latency_ms = wall_s * 1000.0
    throughput_mbps = (len(payload) / (1024 * 1024)) / max(wall_s, 1e-9)
    cpu_usage_percent = (cpu_s / max(wall_s, 1e-9)) * 100.0

    return TrialMetrics(
        latency_ms=latency_ms,
        throughput_mbps=throughput_mbps,
        ciphertext_overhead_bytes=(len(ciphertext) - len(payload)) + len(tag),
        capsule_signature_overhead_bytes=len(capsule) + len(signature),
        peak_memory_bytes=peak,
        cpu_usage_percent=cpu_usage_percent,
        tamper_blocked=tamper_blocked,
        wrong_key_blocked=wrong_key_blocked,
    )


def _summarize_trials(baseline: str, file_size_bytes: int, trials: list[TrialMetrics]) -> dict:
    latencies = [trial.latency_ms for trial in trials]
    throughputs = [trial.throughput_mbps for trial in trials]
    ciphertext_overheads = [trial.ciphertext_overhead_bytes for trial in trials]
    capsule_signature_overheads = [trial.capsule_signature_overhead_bytes for trial in trials]
    peak_memories = [trial.peak_memory_bytes for trial in trials]
    cpu_percents = [trial.cpu_usage_percent for trial in trials]

    tamper_bypass = sum(1 for trial in trials if not trial.tamper_blocked)
    wrong_key_bypass = sum(1 for trial in trials if not trial.wrong_key_blocked)

    return {
        "baseline": baseline,
        "file_size_bytes": file_size_bytes,
        "trials": len(trials),
        "median_latency_ms": round(statistics.median(latencies), 6),
        "p95_latency_ms": round(_p95(latencies), 6),
        "throughput_mbps": round(statistics.median(throughputs), 6),
        "ciphertext_overhead_bytes": int(statistics.median(ciphertext_overheads)),
        "capsule_signature_overhead_bytes": int(statistics.median(capsule_signature_overheads)),
        "peak_memory_bytes": max(peak_memories),
        "cpu_usage_percent": round(statistics.median(cpu_percents), 4),
        "tamper_failure_rate": round(tamper_bypass / len(trials), 6),
        "wrong_key_failure_rate": round(wrong_key_bypass / len(trials), 6),
    }


def run_benchmark_suite(
    file_sizes_bytes: list[int],
    trials_per_size: int = 20,
    seed: int = 1337,
) -> dict:
    if trials_per_size < 1:
        raise ValueError("trials_per_size must be >= 1")

    seed_rng = random.Random(seed)
    results: list[dict] = []

    # Baseline key setup done once to keep comparisons consistent.
    rsa_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_public = rsa_private.public_key()
    rsa_private_wrong = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ecdsa_private = ec.generate_private_key(ec.SECP256R1())
    ecdsa_public = ecdsa_private.public_key()

    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()
    _, kyber_sk_wrong = crypto.generate_kyber_keypair()
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()
    wrong_aes_key = os.urandom(crypto.AES_KEY_SIZE)

    for file_size in file_sizes_bytes:
        for baseline in ALL_BASELINES:
            trial_metrics: list[TrialMetrics] = []
            for _ in range(trials_per_size):
                payload = _payload(seed_rng, file_size)
                if baseline == BASELINE_AES:
                    trial_metrics.append(_run_trial_aes_only(payload, wrong_aes_key))
                elif baseline == BASELINE_RSA:
                    trial_metrics.append(
                        _run_trial_rsa_classical(
                            payload,
                            rsa_public,
                            rsa_private,
                            rsa_private_wrong,
                            ecdsa_private,
                            ecdsa_public,
                        )
                    )
                elif baseline == BASELINE_PQC:
                    trial_metrics.append(
                        _run_trial_pqc(
                            payload,
                            kyber_pk,
                            kyber_sk,
                            kyber_sk_wrong,
                            dil_sk,
                            dil_pk,
                        )
                    )
                else:
                    raise ValueError(f"Unsupported baseline: {baseline}")

            results.append(_summarize_trials(baseline, file_size, trial_metrics))

    return {
        "seed": seed,
        "trials_per_size": trials_per_size,
        "file_sizes_bytes": file_sizes_bytes,
        "results": results,
    }


def save_suite_report(report: dict, output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out
