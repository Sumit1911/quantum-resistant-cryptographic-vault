from __future__ import annotations

import math
import random


def _fmt_ops(value: float) -> str:
    if value <= 0:
        return "0"
    exponent = int(math.log10(value))
    mantissa = value / (10 ** exponent)
    return f"{mantissa:.2f}e{exponent}"


def _shor_verdict(break_ratio_model: float) -> str:
    if break_ratio_model >= 1e12:
        return "highly_exposed"
    if break_ratio_model >= 1e6:
        return "degraded"
    return "not_broken_in_model"


def compute_shors_complexity(key_bits: int) -> dict:
    points = [256, 512, 1024, 2048, 3072, 4096, 8192]
    classical_exponent_divisor = 18.0
    quantum_log_multiplier = 2.5

    classical_curve = []
    quantum_curve = []
    for bits in points:
        classical = float(2 ** (bits / classical_exponent_divisor))
        quantum = float(2 ** (math.log2(bits) * quantum_log_multiplier))
        classical_curve.append([bits, classical])
        quantum_curve.append([bits, quantum])

    selected_classical = float(2 ** (key_bits / classical_exponent_divisor))
    selected_quantum = float(2 ** (math.log2(key_bits) * quantum_log_multiplier))
    break_ratio_model = selected_classical / max(selected_quantum, 1.0)

    return {
        "mode": "shors",
        "model_type": "modeled asymptotic pressure on RSA/ECC-like schemes",
        "key_size": key_bits,
        "classical_ops_estimate": selected_classical,
        "quantum_ops_estimate": selected_quantum,
        "classical_curve": classical_curve,
        "quantum_curve": quantum_curve,
        "break_ratio_model": break_ratio_model,
        "verdict": _shor_verdict(break_ratio_model),
        "explanation": (
            "Shor-mode output is a model of relative asymptotic pressure; "
            "it is not a hardware-calibrated break-time forecast."
        ),
        "snapshot": {
            "classical_notation": _fmt_ops(selected_classical),
            "quantum_notation": _fmt_ops(selected_quantum),
        },
        "formula_panel": {
            "input": "key_size_bits",
            "classical_formula_family": "2^(n/18)",
            "quantum_formula_family": "2^((log2(n))*2.5)",
            "curve_source": "heuristic asymptotic model for comparative visualization",
            "assumptions": {
                "key_size_bits": key_bits,
                "classical_exponent_divisor": classical_exponent_divisor,
                "quantum_log_multiplier": quantum_log_multiplier,
            },
        },
    }


def _grover_verdict(post_grover_bits: int) -> str:
    if post_grover_bits < 128:
        return "weakened"
    return "resilient_in_model"


def compute_grovers_impact(algo: str) -> dict:
    base_bits = {"AES-128": 128, "AES-192": 192, "AES-256": 256, "SHA-256": 256}.get(algo, 128)
    post_grover = max(1, base_bits // 2)

    target_type = "hash_preimage" if algo.startswith("SHA") else "symmetric_encryption"

    recommendations = {
        "AES-128": "migration_advised: move to AES-256 for stronger post-quantum margin.",
        "AES-192": "migration_advised: AES-256 preferred for long-term confidentiality.",
        "AES-256": "resilient_in_model: strong remaining margin under this reduction model.",
        "SHA-256": "resilient_in_model for many contexts; interpret as reduced margin, not direct break.",
    }

    interpretation = {
        "symmetric_encryption": "Effective key-search-space reduction model; not direct practical break timing.",
        "hash_preimage": "Preimage search-space reduction model; not collision analysis and not direct break timing.",
    }

    bars = [
        {"label": "Classical Security", "bits": base_bits},
        {"label": "Post-Grover Security", "bits": post_grover},
        {"label": "Reference Margin", "bits": 128},
    ]

    return {
        "mode": "grovers",
        "model_type": "effective search-space reduction model",
        "algorithm": algo,
        "target_type": target_type,
        "classical_bits": base_bits,
        "post_grover_bits": post_grover,
        "effective_reduction_percent": round(100.0 * (1 - (post_grover / base_bits)), 2),
        "verdict": _grover_verdict(post_grover),
        "recommendation": recommendations.get(algo, "migration_advised: evaluate stronger post-quantum margin."),
        "interpretation": interpretation[target_type],
        "bars": bars,
        "formula_panel": {
            "input": "classical_security_bits",
            "formula_family": "effective_bits = classical_bits / 2",
            "output_meaning": "remaining modeled security margin under quadratic search speedup",
            "estimated_vs_measured": "modeled",
        },
    }


def _lattice_verdict(security_band_model: int) -> str:
    if security_band_model >= 192:
        return "resilient_in_model"
    if security_band_model >= 128:
        return "degraded"
    return "highly_exposed"


def compute_lattice_svp_hardness(dimension: int) -> dict:
    bkz_block_size_proxy = max(180, int(dimension * 0.76))
    classical_attack_ops_estimate = float(2 ** (0.292 * bkz_block_size_proxy))
    quantum_attack_ops_estimate = float(2 ** (0.265 * bkz_block_size_proxy))

    rng = random.Random(dimension)
    points = [[rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(140)]

    dims = [384, 512, 640, 768, 896, 1024]
    classical_curve = [[d, float(2 ** (0.292 * max(180, int(d * 0.76))))] for d in dims]
    quantum_curve = [[d, float(2 ** (0.265 * max(180, int(d * 0.76))))] for d in dims]

    security_band_model = 128 if dimension <= 512 else 192 if dimension <= 768 else 256

    return {
        "mode": "lattice",
        "model_type": "coarse hardness trend model for lattice attacks",
        "dimension": dimension,
        "attack_ops_estimate_classical": classical_attack_ops_estimate,
        "attack_ops_estimate_quantum": quantum_attack_ops_estimate,
        "bkz_block_size_proxy": bkz_block_size_proxy,
        "security_band_model": security_band_model,
        "verdict": _lattice_verdict(security_band_model),
        "lattice_points": points,
        "classical_curve": classical_curve,
        "quantum_curve": quantum_curve,
        "summary": (
            "Modeled hardness trend only. Values are heuristic estimates, not full cryptanalytic cost bounds."
        ),
        "formula_panel": {
            "input": "dimension",
            "formula_family": "bkz_proxy = 0.76*n; ops ~ 2^(c*beta)",
            "output_meaning": "relative hardness trend across dimensions",
            "estimated_vs_measured": "estimated/model",
        },
    }


def _harvest_verdict(risk_horizon_percent: float) -> str:
    if risk_horizon_percent >= 70:
        return "migration_advised"
    if risk_horizon_percent >= 45:
        return "weakened"
    return "resilient_in_model"


def compute_harvest_now_risk(years_to_protect: int, data_value: str) -> dict:
    years_to_protect = max(1, min(50, years_to_protect))
    normalized_value = data_value.lower()
    value_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.25, "critical": 1.5}.get(
        normalized_value, 1.0
    )

    risk_curve = []
    threshold_crossing_year_model = None
    for year in range(1, years_to_protect + 1):
        baseline = 100 / (1 + math.exp(-0.35 * (year - 9)))
        adjusted = min(100.0, baseline * value_multiplier)
        risk_curve.append({"year": year, "risk": round(adjusted, 2)})
        if threshold_crossing_year_model is None and adjusted >= 70:
            threshold_crossing_year_model = year

    risk_today = risk_curve[0]["risk"]
    risk_horizon = risk_curve[-1]["risk"]

    return {
        "mode": "harvest",
        "model_type": "relative exposure planning model (not a forecast)",
        "years_to_protect": years_to_protect,
        "data_value": normalized_value,
        "risk_today_percent": risk_today,
        "risk_horizon_percent": risk_horizon,
        "threshold_crossing_year_model": threshold_crossing_year_model,
        "risk_curve": risk_curve,
        "verdict": _harvest_verdict(risk_horizon),
        "recommendation": (
            "migration_advised: adopt PQC and crypto-agility now for long-lived sensitive data."
            if risk_horizon >= 70
            else "monitor_in_model: maintain migration plan and re-evaluate regularly."
        ),
        "formula_panel": {
            "input": "years_to_protect, data_value_multiplier",
            "formula_family": "logistic risk growth scaled by value multiplier",
            "output_meaning": "relative long-horizon exposure curve",
            "estimated_vs_measured": "modeled",
        },
        "assumptions": {
            "threat_model": "adversary can harvest ciphertext now and attempt decryption later",
            "planning_scope": "long-term confidentiality planning",
        },
    }
