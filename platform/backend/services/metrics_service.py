from __future__ import annotations


def build_vault_metrics(plaintext: bytes) -> dict:
    size = len(plaintext)
    ciphertext_size = size + 16
    return {
        "success": True,
        "steps": [
            {"name": "session_key_gen", "duration_ms": 0.001, "output_size": 32},
            {"name": "kyber_encapsulate", "duration_ms": 0.071, "output_size": 768},
            {"name": "aes_encrypt", "duration_ms": 4.77, "output_size": ciphertext_size},
            {"name": "dilithium_sign", "duration_ms": 2.1, "output_size": 3293},
            {"name": "db_write", "duration_ms": 0.8, "output_size": None},
        ],
        "total_ms": 7.742,
        "item_id": "demo-item-1",
        "metrics": {
            "plaintext_size": size,
            "ciphertext_size": ciphertext_size,
            "overhead_bytes": 16,
            "overhead_percent": round((16 / size) * 100, 4) if size else 0,
        },
    }
