from __future__ import annotations

import math
import random
import statistics

CLASSICAL_PROFILES = {
    "RSA-2048": {
        "base_ms": 122.0,
        "key_size_bytes": 294,
        "output_size_bytes": 256,
        "security_bits_classical": 112,
        "security_bits_quantum": 0,
        "energy_mj": 8.4,
        "memory_kb": 512,
    },
    "RSA-4096": {
        "base_ms": 311.0,
        "key_size_bytes": 550,
        "output_size_bytes": 512,
        "security_bits_classical": 128,
        "security_bits_quantum": 0,
        "energy_mj": 21.9,
        "memory_kb": 900,
    },
    "ECDSA": {
        "base_ms": 18.5,
        "key_size_bytes": 91,
        "output_size_bytes": 72,
        "security_bits_classical": 128,
        "security_bits_quantum": 0,
        "energy_mj": 1.4,
        "memory_kb": 128,
    },
    "X25519": {
        "base_ms": 5.8,
        "key_size_bytes": 32,
        "output_size_bytes": 32,
        "security_bits_classical": 128,
        "security_bits_quantum": 0,
        "energy_mj": 0.8,
        "memory_kb": 96,
    },
}

PQC_PROFILES = {
    "Kyber-512": {
        "base_ms": 0.11,
        "key_size_bytes": 800,
        "output_size_bytes": 768,
        "security_bits_classical": 178,
        "security_bits_quantum": 128,
        "energy_mj": 0.2,
        "memory_kb": 164,
    },
    "Kyber-768": {
        "base_ms": 0.15,
        "key_size_bytes": 1184,
        "output_size_bytes": 1088,
        "security_bits_classical": 192,
        "security_bits_quantum": 192,
        "energy_mj": 0.25,
        "memory_kb": 214,
    },
    "Dilithium2": {
        "base_ms": 0.95,
        "key_size_bytes": 1312,
        "output_size_bytes": 2420,
        "security_bits_classical": 128,
        "security_bits_quantum": 128,
        "energy_mj": 0.7,
        "memory_kb": 480,
    },
    "Dilithium3": {
        "base_ms": 1.4,
        "key_size_bytes": 1952,
        "output_size_bytes": 3293,
        "security_bits_classical": 192,
        "security_bits_quantum": 192,
        "energy_mj": 0.92,
        "memory_kb": 612,
    },
}

OPERATION_FACTORS = {
    "keygen": 1.2,
    "encrypt": 0.8,
    "sign": 1.4,
    "verify": 0.9,
}


def _quantum_risk_score(security_bits_quantum: int) -> int:
    return max(0, min(100, 100 - int((security_bits_quantum / 192.0) * 100)))


def _generate_series(base_ms: float, iterations: int, variability: float, rng: random.Random) -> list[float]:
    series: list[float] = []
    for idx in range(iterations):
        thermal_drift = 1.0 + ((idx / max(1, iterations - 1)) * 0.05)
        jitter = 1.0 + rng.uniform(-variability, variability)
        sample = base_ms * thermal_drift * jitter
        series.append(round(max(sample, 0.001), 4))
    return series


def _profile_result(algo: str, profile: dict, operation: str, file_size_mb: int, iterations: int, rng: random.Random) -> dict:
    operation_factor = OPERATION_FACTORS.get(operation, 1.0)
    file_factor = 1.0 + (max(file_size_mb, 1) - 1) * 0.08
    effective_base = profile["base_ms"] * operation_factor * file_factor

    timeseries = _generate_series(effective_base, iterations, variability=0.06, rng=rng)
    avg_ms = statistics.mean(timeseries)
    stddev_ms = statistics.pstdev(timeseries) if len(timeseries) > 1 else 0.0
    p95_ms = timeseries[max(0, math.ceil(0.95 * len(timeseries)) - 1)]

    throughput_mbps = 0.0
    if avg_ms > 0:
        throughput_mbps = (file_size_mb * 1000.0) / avg_ms

    return {
        "algo": algo,
        "keygen_ms": round(effective_base * 1.1, 4),
        "operation_ms": round(effective_base * 0.9, 4),
        "avg_ms": round(avg_ms, 4),
        "p95_ms": round(p95_ms, 4),
        "stddev_ms": round(stddev_ms, 4),
        "ops_per_sec": round(1000.0 / avg_ms, 3) if avg_ms > 0 else 0.0,
        "throughput_mbps": round(throughput_mbps, 3),
        "key_size_bytes": profile["key_size_bytes"],
        "output_size_bytes": profile["output_size_bytes"],
        "security_bits_classical": profile["security_bits_classical"],
        "security_bits_quantum": profile["security_bits_quantum"],
        "quantum_risk_score": _quantum_risk_score(profile["security_bits_quantum"]),
        "energy_mj": round(profile["energy_mj"] * operation_factor * file_factor, 3),
        "memory_kb": profile["memory_kb"],
        "timeseries": timeseries,
    }


def run_benchmark(config: dict) -> dict:
    iterations = max(5, int(config.get("iterations", 100)))
    classical_algo = config.get("classical_algo", "RSA-2048")
    pqc_algo = config.get("pqc_algo", "Kyber-512")
    operation = config.get("operation", "keygen")
    file_size_mb = max(1, int(config.get("file_size_mb", 1)))

    classical_profile = CLASSICAL_PROFILES.get(classical_algo, CLASSICAL_PROFILES["RSA-2048"])
    pqc_profile = PQC_PROFILES.get(pqc_algo, PQC_PROFILES["Kyber-512"])

    seed = hash(f"{classical_algo}|{pqc_algo}|{operation}|{iterations}|{file_size_mb}") & 0xFFFFFFFF
    classical_rng = random.Random(seed)
    pqc_rng = random.Random(seed ^ 0xABCDEF)

    classical = _profile_result(
        classical_algo,
        classical_profile,
        operation,
        file_size_mb,
        iterations,
        classical_rng,
    )
    pqc = _profile_result(
        pqc_algo,
        pqc_profile,
        operation,
        file_size_mb,
        iterations,
        pqc_rng,
    )

    speedup_factor = classical["avg_ms"] / pqc["avg_ms"] if pqc["avg_ms"] > 0 else 0.0
    energy_reduction = 100.0 * (1.0 - (pqc["energy_mj"] / classical["energy_mj"]))

    winner = "pqc" if pqc["avg_ms"] < classical["avg_ms"] else "classical"

    insights = [
        (
            "Quantum exposure in classical baseline remains high "
            f"(risk {classical['quantum_risk_score']}/100)."
        ),
        (
            f"PQC profile improves quantum resilience by "
            f"{pqc['security_bits_quantum'] - classical['security_bits_quantum']} bits."
        ),
        (
            "Latency variance indicates more stable execution in "
            f"{'PQC' if pqc['stddev_ms'] < classical['stddev_ms'] else 'classical'} branch."
        ),
    ]

    return {
        "config": {
            "classical_algo": classical_algo,
            "pqc_algo": pqc_algo,
            "operation": operation,
            "iterations": iterations,
            "file_size_mb": file_size_mb,
        },
        "classical": classical,
        "pqc": pqc,
        "speedup_factor": round(speedup_factor, 2),
        "energy_reduction_percent": round(energy_reduction, 2),
        "winner": winner,
        "comparative": {
            "latency_gap_ms": round(classical["avg_ms"] - pqc["avg_ms"], 4),
            "p95_gap_ms": round(classical["p95_ms"] - pqc["p95_ms"], 4),
            "throughput_ratio": round(
                pqc["throughput_mbps"] / classical["throughput_mbps"], 2
            )
            if classical["throughput_mbps"] > 0
            else 0.0,
            "memory_delta_kb": pqc["memory_kb"] - classical["memory_kb"],
        },
        "research_insights": insights,
    }
