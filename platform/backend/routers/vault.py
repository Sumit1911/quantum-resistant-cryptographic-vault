from fastapi import APIRouter
from pydantic import BaseModel

from services.metrics_service import build_vault_metrics


router = APIRouter()


class VaultEncryptRequest(BaseModel):
    plaintext: str
    algorithm: str = "Kyber-512"
    signing: str = "Dilithium3"


@router.post("/encrypt")
def encrypt(payload: VaultEncryptRequest) -> dict:
    return build_vault_metrics(
        payload.plaintext.encode("utf-8"),
        algorithm=payload.algorithm,
        signing=payload.signing,
    )
