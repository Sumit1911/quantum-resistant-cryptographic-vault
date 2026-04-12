from __future__ import annotations

import math
import random


def _fmt_ops(value: float) -> str:
    if value <= 0:
        return "0"
    exponent = int(math.log10(value))
    mantissa = value / (10 ** exponent)
    return f"{mantissa:.2f}e{exponent}"


def compute_shors_complexity(key_bits: int) -> dict:
    points = [256, 512, 1024, 2048, 3072, 4096, 8192]

    classical_curve = []
    quantum_curve = []
    for bits in points:
        classical = float(2 ** (bits / 18.0))
        quantum = float(2 ** (math.log2(bits) * 2.5))
        classical_curve.append([bits, classical])
        quantum_curve.append([bits, quantum])

    selected_classical = float(2 ** (key_bits / 18.0))
    selected_quantum = float(2 ** (math.log2(key_bits) * 2.5))
    break_ratio = selected_classical / max(selected_quantum, 1.0)

    return {
        "mode": "shors",
        "key_size": key_bits,
        "classical_ops": selected_classical,
        "quantum_ops": selected_quantum,
        "classical_years": selected_classical / 1e12,
        "quantum_hours": selected_quantum / 1e6,
        "break_ratio": break_ratio,
        "classical_curve": classical_curve,
        "quantum_curve": quantum_curve,
        "verdict": "BROKEN" if key_bits >= 1024 else "DEGRADED",
        "explanation": (
            "Shor reduces integer factorization from sub-exponential classical hardness "
            "to polynomial-time quantum circuits."
        ),
        "snapshot": {
            "classical_notation": _fmt_ops(selected_classical),
            "quantum_notation": _fmt_ops(selected_quantum),
        },
    }


def compute_grovers_impact(algo: str) -> dict:
    base_bits = {"AES-128": 128, "AES-192": 192, "AES-256": 256, "SHA-256": 256}.get(algo, 128)
    post_grover = max(1, base_bits // 2)

    recommendations = {
        "AES-128": "Migrate to AES-256 for 128-bit post-quantum margin.",
        "AES-192": "Borderline option; AES-256 preferred for long-lived data.",
        "AES-256": "Maintains strong post-quantum brute-force resistance.",
        "SHA-256": "Still useful, but pair with strong PQC authentication design.",
    }

    bars = [
        {"label": "Classical Security", "bits": base_bits},
        {"label": "Post-Grover Security", "bits": post_grover},
        {"label": "Safety Threshold", "bits": 128},
    ]

    return {
        "mode": "grovers",
        "algorithm": algo,
        "classical_bits": base_bits,
        "post_grover_bits": post_grover,
        "effective_reduction_percent": round(100.0 * (1 - (post_grover / base_bits)), 2),
        "verdict": "SECURE" if post_grover >= 128 else "WEAKENED",
        "recommendation": recommendations.get(algo, "Evaluate for 128-bit post-quantum margin."),
        "bars": bars,
    }


def compute_lattice_svp_hardness(dimension: int) -> dict:
    beta = max(180, int(dimension * 0.76))
    classical_ops = float(2 ** (0.292 * beta))
    quantum_ops = float(2 ** (0.265 * beta))

    rng = random.Random(dimension)
    points = [[rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(140)]

    dims = [384, 512, 640, 768, 896, 1024]
    classical_curve = [[d, float(2 ** (0.292 * max(180, int(d * 0.76))))] for d in dims]
    quantum_curve = [[d, float(2 ** (0.265 * max(180, int(d * 0.76))))] for d in dims]

    security_level = 128 if dimension <= 512 else 192 if dimension <= 768 else 256

    return {
        "mode": "lattice",
        "dimension": dimension,
        "classical_attack_ops": classical_ops,
        "quantum_attack_ops": quantum_ops,
        "bkz_block_size": beta,
        "security_level": security_level,
        "verdict": "SECURE" if security_level >= 128 else "REVIEW",
        "lattice_points": points,
        "classical_curve": classical_curve,
        "quantum_curve": quantum_curve,
        "summary": (
            "Approximate SVP remains expensive in high dimensions, preserving PQC hardness "
            "under known attack models."
        ),
    }


def compute_harvest_now_risk(years_to_protect: int, data_value: str) -> dict:
    years_to_protect = max(1, min(50, years_to_protect))
    value_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.25, "critical": 1.5}.get(
        data_value.lower(), 1.0
    )

    # Logistic-style risk growth curve (demo model for research discussion).
    risk_curve = []
    compromise_year = None
    for year in range(1, years_to_protect + 1):
        baseline = 100 / (1 + math.exp(-0.35 * (year - 9)))
        adjusted = min(100.0, baseline * value_multiplier)
        risk_curve.append({"year": year, "risk": round(adjusted, 2)})
        if compromise_year is None and adjusted >= 70:
            compromise_year = year

    present_risk = risk_curve[0]["risk"]
    future_risk = risk_curve[-1]["risk"]

    return {
        "mode": "harvest",
        "years_to_protect": years_to_protect,
        "data_value": data_value.lower(),
        "risk_today_percent": present_risk,
        "risk_horizon_percent": future_risk,
        "compromise_year_estimate": compromise_year,
        "risk_curve": risk_curve,
        "verdict": "URGENT" if future_risk >= 70 else "MONITOR",
        "recommendation": (
            "Adopt PQC + crypto-agility now for long-lived sensitive data."
            if future_risk >= 70
            else "Maintain migration plan and re-evaluate yearly."
        ),
    }
