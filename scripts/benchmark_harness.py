"""Run reproducible multi-trial baseline benchmarks and save report JSON."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.benchmark_harness import run_benchmark_suite, save_suite_report


def _parse_sizes(raw: str) -> list[int]:
    sizes: list[int] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        if token.endswith("kb"):
            sizes.append(int(token[:-2]) * 1024)
        elif token.endswith("mb"):
            sizes.append(int(token[:-2]) * 1024 * 1024)
        else:
            sizes.append(int(token))
    if not sizes:
        raise ValueError("At least one file size is required")
    return sizes


def main() -> None:
    parser = argparse.ArgumentParser(description="Run baseline benchmark harness")
    parser.add_argument(
        "--sizes",
        default="1kb,64kb,1mb",
        help="Comma-separated sizes: e.g. 1kb,64kb,1mb or raw bytes",
    )
    parser.add_argument("--trials", type=int, default=20, help="Trials per baseline per size")
    parser.add_argument("--seed", type=int, default=1337, help="Deterministic payload seed")
    parser.add_argument(
        "--out",
        default="reports/benchmark_harness_latest.json",
        help="Output JSON report path",
    )
    args = parser.parse_args()

    sizes = _parse_sizes(args.sizes)
    report = run_benchmark_suite(file_sizes_bytes=sizes, trials_per_size=args.trials, seed=args.seed)
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    out_path = save_suite_report(report, args.out)

    print(f"Saved benchmark report: {out_path}")
    print("baseline | file_size | median_ms | p95_ms | throughput_MBps | ct_overhead | cap_sig_overhead | peak_mem_KB | cpu_% | tamper_fail | wrong_key_fail")
    for row in report["results"]:
        throughput = row["throughput_mbps"]
        peak_mem_kb = row["peak_memory_bytes"] / 1024
        print(
            f"{row['baseline']} | {row['file_size_bytes']} | "
            f"{row['median_latency_ms']:.4f} | {row['p95_latency_ms']:.4f} | "
            f"{throughput:.4f} | {row['ciphertext_overhead_bytes']} | "
            f"{row['capsule_signature_overhead_bytes']} | {peak_mem_kb:.2f} | "
            f"{row['cpu_usage_percent']:.2f} | {row['tamper_failure_rate']:.4f} | {row['wrong_key_failure_rate']:.4f}"
        )


if __name__ == "__main__":
    main()
