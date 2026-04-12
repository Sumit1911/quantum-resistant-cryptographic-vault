"""Simple crypto benchmarks for Phase 7.4 validation."""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core import auth, crypto, storage, vault_manager


def _timeit(fn, rounds: int = 200):
    samples = []
    for _ in range(rounds):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000)  # ms
    return statistics.mean(samples)


def main() -> None:
    run_id = int(time.time() * 1_000_000)

    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()
    payload_1k = b"a" * 1024
    blob_1mb = b"b" * (1024 * 1024)

    capsule, ss = crypto.kyber_encapsulate(kyber_pk)
    kyber_enc_ms = _timeit(lambda: crypto.kyber_encapsulate(kyber_pk), rounds=200)
    kyber_dec_ms = _timeit(lambda: crypto.kyber_decapsulate(capsule, kyber_sk), rounds=200)

    dil_sign_ms = _timeit(lambda: crypto.dilithium_sign(payload_1k, dil_sk), rounds=200)
    sig = crypto.dilithium_sign(payload_1k, dil_sk)
    dil_verify_ms = _timeit(lambda: crypto.dilithium_verify(payload_1k, sig, dil_pk), rounds=200)

    def _aes_enc_1mb():
        crypto.aes_encrypt(blob_1mb, ss)

    aes_1mb_ms = _timeit(_aes_enc_1mb, rounds=50)
    aes_mbps = (1.0 / (aes_1mb_ms / 1000.0))

    db_path = f"/tmp/bench_vault_{run_id}.db"
    storage.init_db(db_path)
    conn = storage.get_connection(db_path)
    username = f"bench_{run_id}"
    vault_manager.register(username, "pass123", conn)
    session = vault_manager.login(username, "pass123", conn)
    assert session is not None

    store_ms = _timeit(
        lambda: vault_manager.store_file(session, "bench.bin", blob_1mb, "application/octet-stream"),
        rounds=20,
    )
    item_id = vault_manager.store_file(session, "bench-last.bin", blob_1mb, "application/octet-stream")
    retrieve_ms = _timeit(lambda: vault_manager.retrieve_file(session, item_id), rounds=20)

    print("Kyber-512 encapsulation (ms):", round(kyber_enc_ms, 3))
    print("Kyber-512 decapsulation (ms):", round(kyber_dec_ms, 3))
    print("Dilithium sign 1KB (ms):", round(dil_sign_ms, 3))
    print("Dilithium verify 1KB (ms):", round(dil_verify_ms, 3))
    print("AES-256-GCM encrypt 1MB (ms):", round(aes_1mb_ms, 3), "~ MB/s:", round(aes_mbps, 2))
    print("Full store_file 1MB (ms):", round(store_ms, 3))
    print("Full retrieve_file 1MB (ms):", round(retrieve_ms, 3))


if __name__ == "__main__":
    main()
