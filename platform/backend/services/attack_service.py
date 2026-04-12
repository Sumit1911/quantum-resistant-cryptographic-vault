from __future__ import annotations

import math
import random


def compute_shors_complexity(key_bits: int) -> dict:
    points = [512, 1024, 2048, 4096]
    classical_curve = [[k, float(2 ** (k / 18))] for k in points]
    quantum_curve = [[k, float(2 ** (math.log2(k) * 2.5))] for k in points]

    selected_classical = float(2 ** (key_bits / 18))
    selected_quantum = float(2 ** (math.log2(key_bits) * 2.5))

    return {
        "key_size": key_bits,
        "classical_ops": selected_classical,
        "quantum_ops": selected_quantum,
        "classical_years": selected_classical / 1e12,
        "quantum_hours": selected_quantum / 1e6,
        "classical_curve": classical_curve,
        "quantum_curve": quantum_curve,
        "verdict": "BROKEN",
    }


def compute_grovers_impact(algo: str) -> dict:
    base_bits = {"AES-128": 128, "AES-256": 256, "SHA-256": 256}.get(algo, 128)
    post_grover = base_bits // 2
    return {
        "algorithm": algo,
        "classical_bits": base_bits,
        "post_grover_bits": post_grover,
        "verdict": "WEAKENED" if post_grover < 128 else "SECURE",
        "recommendation": "Use AES-256" if algo == "AES-128" else "Current choice acceptable",
    }


def compute_lattice_svp_hardness(dimension: int) -> dict:
    beta = max(200, int(dimension * 0.75))
    classical_ops = float(2 ** (0.292 * beta))
    quantum_ops = float(2 ** (0.265 * beta))
    points = [[random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(120)]

    return {
        "dimension": dimension,
        "classical_attack_ops": classical_ops,
        "quantum_attack_ops": quantum_ops,
        "bkz_block_size": beta,
        "security_level": 128 if dimension <= 512 else 192,
        "verdict": "SECURE",
        "lattice_points": points,
    }
