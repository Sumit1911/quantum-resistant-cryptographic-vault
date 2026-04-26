from __future__ import annotations

import os
import platform
import random
import statistics
import sys
import time
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, x25519

from core import crypto

EXPERIMENT_FAMILIES = {
    "kem": {
        "operation": "key_exchange",
        "classical_algos": ["X25519"],
        "pqc_algos": ["Kyber-512", "Kyber-768"],
        "default_payload_mb": None,
    },
    "signature": {
        "operation": "sign_verify",
        "classical_algos": ["ECDSA"],
        "pqc_algos": ["Dilithium3", "ML-DSA-65"],
        "default_payload_mb": None,
    },
    "encryption": {
        "operation": "hybrid_encrypt",
        "classical_algos": ["RSA-OAEP-AES"],
        "pqc_algos": ["Kyber-AES-Hybrid"],
        "default_payload_mb": 1,
    },
}

RISK_SCORES = {
    "X25519": 80,
    "ECDSA": 85,
    "RSA-OAEP-AES": 95,
    "Kyber-512": 20,
    "Kyber-768": 10,
    "Dilithium3": 10,
    "ML-DSA-65": 10,
    "Kyber-AES-Hybrid": 12,
}


@dataclass
class Sample:
    latency_ms: float
    ciphertext_overhead_bytes: int
    capsule_signature_overhead_bytes: int


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    idx = max(0, int(len(ordered) * 0.95) - 1)
    return ordered[idx]


def _measure(op, warmup_runs: int, iterations: int) -> list[Sample]:
    # Warm-up runs are intentionally excluded from measured output.
    for _ in range(warmup_runs):
        op()

    samples: list[Sample] = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = op()  # ONLY crypto operation block measured
        end = time.perf_counter()
        samples.append(
            Sample(
                latency_ms=(end - start) * 1000.0,
                ciphertext_overhead_bytes=result["ciphertext_overhead_bytes"],
                capsule_signature_overhead_bytes=result["capsule_signature_overhead_bytes"],
            )
        )
    return samples


def _validate_experiment_config(family: str, classical_algo: str, pqc_algo: str, operation: str) -> None:
    rules = EXPERIMENT_FAMILIES.get(family)
    if rules is None:
        raise ValueError(f"Unsupported experiment_family '{family}'")
    if operation != rules["operation"]:
        raise ValueError(
            f"Invalid operation '{operation}' for family '{family}'. Expected '{rules['operation']}'."
        )
    if classical_algo not in rules["classical_algos"]:
        raise ValueError(
            f"Invalid classical algorithm '{classical_algo}' for family '{family}'. "
            f"Allowed: {', '.join(rules['classical_algos'])}"
        )
    if pqc_algo not in rules["pqc_algos"]:
        raise ValueError(
            f"Invalid PQC algorithm '{pqc_algo}' for family '{family}'. "
            f"Allowed: {', '.join(rules['pqc_algos'])}"
        )


def _build_kem_ops(pqc_algo: str):
    def classical_op() -> dict:
        sk_a = x25519.X25519PrivateKey.generate()
        sk_b = x25519.X25519PrivateKey.generate()
        pk_b = sk_b.public_key()
        secret_a = sk_a.exchange(pk_b)
        if len(secret_a) != 32:
            raise RuntimeError("X25519 secret size mismatch")
        return {
            "ciphertext_overhead_bytes": 0,
            "capsule_signature_overhead_bytes": 0,
        }

    def pqc_op() -> dict:
        if pqc_algo == "Kyber-768":
            kem_alg = "Kyber768"
            with crypto.oqs.KeyEncapsulation(kem_alg) as kem:
                pk = kem.generate_keypair()
                sk = kem.export_secret_key()
            with crypto.oqs.KeyEncapsulation(kem_alg) as kem_enc:
                capsule, ss_enc = kem_enc.encap_secret(pk)
            with crypto.oqs.KeyEncapsulation(kem_alg, secret_key=sk) as kem_dec:
                ss_dec = kem_dec.decap_secret(capsule)
        else:
            pk, sk = crypto.generate_kyber_keypair()
            capsule, ss_enc = crypto.kyber_encapsulate(pk)
            ss_dec = crypto.kyber_decapsulate(capsule, sk)
        if ss_enc != ss_dec:
            raise RuntimeError("KEM decapsulation mismatch")
        return {
            "ciphertext_overhead_bytes": 0,
            "capsule_signature_overhead_bytes": len(capsule),
        }

    return classical_op, pqc_op


def _build_signature_ops(pqc_algo: str):
    payload = b"S" * 1024

    ecdsa_private = ec.generate_private_key(ec.SECP256R1())
    ecdsa_public = ecdsa_private.public_key()

    if pqc_algo in {"Dilithium3", "ML-DSA-65"}:
        pqc_public, pqc_private = crypto.generate_dilithium_keypair()
        pqc_alg = None
    else:
        raise ValueError(f"Unsupported PQC signature algorithm '{pqc_algo}' on this backend")

    def classical_op() -> dict:
        sig = ecdsa_private.sign(payload, ec.ECDSA(hashes.SHA256()))
        ecdsa_public.verify(sig, payload, ec.ECDSA(hashes.SHA256()))
        return {
            "ciphertext_overhead_bytes": 0,
            "capsule_signature_overhead_bytes": len(sig),
        }

    def pqc_op() -> dict:
        if pqc_alg is None:
            sig = crypto.dilithium_sign(payload, pqc_private)
            ok = crypto.dilithium_verify(payload, sig, pqc_public)
        else:
            with crypto.oqs.Signature(pqc_alg, secret_key=pqc_private) as signer:
                sig = signer.sign(payload)
            with crypto.oqs.Signature(pqc_alg) as verifier:
                ok = verifier.verify(payload, sig, pqc_public)
        if not ok:
            raise RuntimeError("PQC signature verify failed")
        return {
            "ciphertext_overhead_bytes": 0,
            "capsule_signature_overhead_bytes": len(sig),
        }

    return classical_op, pqc_op


def _build_encryption_ops(payload_size_mb: int):
    rng = random.Random(1337 + payload_size_mb)
    payload = rng.randbytes(payload_size_mb * 1024 * 1024)

    rsa_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_public = rsa_private.public_key()

    kyber_public, _ = crypto.generate_kyber_keypair()

    def classical_op() -> dict:
        # Classical hybrid pipeline (same structure as PQC pipeline):
        # 1) generate AES key 2) AES-encrypt payload 3) wrap AES key
        aes_key = os.urandom(crypto.AES_KEY_SIZE)
        _, ciphertext, tag = crypto.aes_encrypt(payload, aes_key)
        wrapped_key = rsa_public.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return {
            "ciphertext_overhead_bytes": (len(ciphertext) - len(payload)) + len(tag),
            "capsule_signature_overhead_bytes": len(wrapped_key),
        }

    def pqc_op() -> dict:
        # PQC hybrid pipeline (structurally identical):
        # 1) generate AES key 2) AES-encrypt payload 3) wrap AES key
        aes_key = os.urandom(crypto.AES_KEY_SIZE)
        _, ciphertext, tag = crypto.aes_encrypt(payload, aes_key)

        # KEM shared secret wraps AES key via AEAD; capsule carries unwrap context.
        capsule, wrap_key = crypto.kyber_encapsulate(kyber_public)
        wrap_iv, wrapped_aes_key, wrapped_tag = crypto.aes_encrypt(aes_key, wrap_key)

        return {
            "ciphertext_overhead_bytes": (len(ciphertext) - len(payload)) + len(tag),
            "capsule_signature_overhead_bytes": len(capsule)
            + len(wrap_iv)
            + len(wrapped_aes_key)
            + len(wrapped_tag),
        }

    return classical_op, pqc_op, payload


def _summarize_branch(
    algo: str,
    samples: list[Sample],
    family: str,
    payload_size_mb: int | None,
) -> dict:
    latencies = [s.latency_ms for s in samples]
    med_ms = statistics.median(latencies)
    avg_ms = statistics.mean(latencies)

    ops_per_sec = (1000.0 / med_ms) if med_ms > 0 else 0.0
    if family == "encryption":
        throughput_value = ((payload_size_mb or 1) / (med_ms / 1000.0)) if med_ms > 0 else 0.0
        throughput_unit = "MB/s"
    else:
        throughput_value = ops_per_sec
        throughput_unit = "ops/s"

    return {
        "algo": algo,
        "median_ms": round(med_ms, 6),
        "avg_ms": round(avg_ms, 6),
        "p95_ms": round(_p95(latencies), 6),
        "stddev_ms": round(statistics.pstdev(latencies) if len(latencies) > 1 else 0.0, 6),
        "ops_per_sec": round(ops_per_sec, 6),
        "throughput_value": round(throughput_value, 6),
        "throughput_unit": throughput_unit,
        "ciphertext_overhead_bytes": int(
            statistics.median([s.ciphertext_overhead_bytes for s in samples])
        ),
        "capsule_signature_overhead_bytes": int(
            statistics.median([s.capsule_signature_overhead_bytes for s in samples])
        ),
        "quantum_risk_score": RISK_SCORES.get(algo, 50),
        "timeseries": [round(value, 6) for value in latencies],
    }


def run_benchmark(config: dict) -> dict:
    family = config.get("experiment_family", "kem")
    rules = EXPERIMENT_FAMILIES.get(family, EXPERIMENT_FAMILIES["kem"])

    iterations = max(5, int(config.get("iterations", 100)))
    warmup_runs = max(0, int(config.get("warmup_runs", 5)))
    operation = config.get("operation", rules["operation"])
    classical_algo = config.get("classical_algo", rules["classical_algos"][0])
    pqc_algo = config.get("pqc_algo", rules["pqc_algos"][0])
    _validate_experiment_config(family, classical_algo, pqc_algo, operation)

    # Mandatory fix: payload is ignored entirely for KEM/signature families.
    payload_size_mb = None if family in {"kem", "signature"} else max(1, int(config.get("file_size_mb", 1)))

    if family == "kem":
        classical_op, pqc_op = _build_kem_ops(pqc_algo)
    elif family == "signature":
        classical_op, pqc_op = _build_signature_ops(pqc_algo)
    elif family == "encryption":
        classical_op, pqc_op, _ = _build_encryption_ops(payload_size_mb or 1)
    else:
        raise ValueError(f"Unsupported experiment_family '{family}'")

    classical_samples = _measure(classical_op, warmup_runs=warmup_runs, iterations=iterations)
    pqc_samples = _measure(pqc_op, warmup_runs=warmup_runs, iterations=iterations)

    classical = _summarize_branch(classical_algo, classical_samples, family, payload_size_mb)
    pqc = _summarize_branch(pqc_algo, pqc_samples, family, payload_size_mb)

    winner = "pqc" if pqc["median_ms"] < classical["median_ms"] else "classical"
    speedup_factor = (
        classical["median_ms"] / pqc["median_ms"] if pqc["median_ms"] > 0 else 0.0
    )

    throughput_ratio = (
        pqc["throughput_value"] / classical["throughput_value"]
        if classical["throughput_value"] > 0
        else 0.0
    )

    return {
        "config": {
            "experiment_family": family,
            "classical_algo": classical_algo,
            "pqc_algo": pqc_algo,
            "operation": operation,
            "iterations": iterations,
            "warmup_runs": warmup_runs,
            "file_size_mb": payload_size_mb,
        },
        "classical": classical,
        "pqc": pqc,
        "winner": winner,
        "speedup_factor": round(speedup_factor, 6),
        "comparative": {
            "latency_gap_ms": round(classical["median_ms"] - pqc["median_ms"], 6),
            "p95_gap_ms": round(classical["p95_ms"] - pqc["p95_ms"], 6),
            "throughput_ratio": round(throughput_ratio, 6),
            "throughput_unit": classical["throughput_unit"],
        },
        "telemetry_basis": {
            "quantum_risk_score": "modeled (NIST PQC status + theoretical quantum attack model mapping)",
            "throughput": (
                "ops/s for KEM/signature families, MB/s for encryption family"
            ),
            "latency": "median/p95/stddev from measured crypto-only operation block",
        },
        "methodology": {
            "machine_specs": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor() or "unknown",
                "cpu_count": os.cpu_count(),
            },
            "python_version": sys.version.split()[0],
            "backend_version": "cryptoarena-backend-2026.04",
            "iterations": iterations,
            "warmup_runs": warmup_runs,
            "payload_size_mb": payload_size_mb,
            "measurement_basis": {
                "primary_metric": "median_ms",
                "p95_metric": "p95_ms",
                "timing_boundary": "start/end perf_counter wraps only crypto_op block; excludes API/logging/serialization/DB",
            },
        },
        "valid_comparison_badges": [
            "same operation class",
            "same payload class",
            "same number of trials",
        ],
        "research_insights": [
            f"Family '{family}' enforces operation-valid comparisons only.",
            "Median latency is used as the primary performance metric for robustness.",
            f"Throughput is reported in {classical['throughput_unit']} for this family.",
        ],
    }
