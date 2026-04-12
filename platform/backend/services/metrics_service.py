from __future__ import annotations


def build_vault_metrics(plaintext: bytes, algorithm: str = "Kyber-512", signing: str = "Dilithium3") -> dict:
    size = len(plaintext)

    # Lightweight analytical model so the frontend can visualize realistic tradeoffs.
    capsule_size = 768 if "512" in algorithm else 1088
    signature_size = 3293 if signing in {"Dilithium3", "ML-DSA-65"} else 2420
    ciphertext_size = size + 16

    session_key_ms = 0.004
    encapsulate_ms = 0.072 if algorithm == "Kyber-512" else 0.101
    encrypt_ms = max(0.15, (size / (1024 * 1024)) * 3.2)
    sign_ms = 1.9 if signing in {"Dilithium3", "ML-DSA-65"} else 1.2
    db_write_ms = 0.7 + (size / (1024 * 1024)) * 0.35
    verify_gate_ms = 0.43

    steps = [
        {"name": "session_key_gen", "duration_ms": round(session_key_ms, 4), "output_size": 32},
        {"name": "kyber_encapsulate", "duration_ms": round(encapsulate_ms, 4), "output_size": capsule_size},
        {"name": "aes_encrypt", "duration_ms": round(encrypt_ms, 4), "output_size": ciphertext_size},
        {"name": "dilithium_sign", "duration_ms": round(sign_ms, 4), "output_size": signature_size},
        {"name": "signature_precheck", "duration_ms": round(verify_gate_ms, 4), "output_size": None},
        {"name": "db_write", "duration_ms": round(db_write_ms, 4), "output_size": None},
    ]

    total_ms = sum(step["duration_ms"] for step in steps)
    overhead_bytes = (ciphertext_size - size) + capsule_size + signature_size

    return {
        "success": True,
        "algorithm": algorithm,
        "signing": signing,
        "steps": steps,
        "total_ms": round(total_ms, 4),
        "item_id": "demo-item-1",
        "metrics": {
            "plaintext_size": size,
            "ciphertext_size": ciphertext_size,
            "capsule_size": capsule_size,
            "signature_size": signature_size,
            "overhead_bytes": overhead_bytes,
            "overhead_percent": round((overhead_bytes / max(size, 1)) * 100, 4),
            "throughput_mbps": round(((size / (1024 * 1024)) * 1000) / max(total_ms, 0.001), 3),
            "tamper_detection_window_ms": round(verify_gate_ms, 4),
            "quantum_readiness_score": 94 if algorithm == "Kyber-512" else 97,
        },
        "research_notes": [
            "Verification gate runs before payload release, preventing decryption-on-tamper.",
            "Metadata inflation is dominated by signature and capsule overhead for tiny payloads.",
            "For larger files, symmetric encryption cost dominates while PQC setup remains near-constant.",
        ],
    }
