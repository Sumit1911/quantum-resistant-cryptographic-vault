"""Generate PQC keypairs and print their sizes/fingerprints."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core import crypto


def _fp(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def main() -> None:
    kyber_pk, kyber_sk = crypto.generate_kyber_keypair()
    dil_pk, dil_sk = crypto.generate_dilithium_keypair()

    print("Kyber-512")
    print("  public bytes:", len(kyber_pk))
    print("  private bytes:", len(kyber_sk))
    print("  public fingerprint:", _fp(kyber_pk))

    print("Dilithium")
    print("  public bytes:", len(dil_pk))
    print("  private bytes:", len(dil_sk))
    print("  public fingerprint:", _fp(dil_pk))


if __name__ == "__main__":
    main()
