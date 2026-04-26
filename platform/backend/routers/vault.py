from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.metrics_service import VaultFlowError, build_vault_metrics, decode_base64_payload


router = APIRouter()


class VaultEncryptRequest(BaseModel):
    plaintext: str | None = None
    content_base64: str | None = None
    input_kind: str = "text"
    item_name: str | None = None
    mime_type: str | None = None
    algorithm: str = "Kyber-512"
    signing: str = "Dilithium3"


@router.post("/encrypt")
def encrypt(payload: VaultEncryptRequest) -> dict:
    if payload.input_kind == "file":
        if not payload.content_base64:
            raise HTTPException(status_code=400, detail="content_base64 is required for file input_kind")
        raw = decode_base64_payload(payload.content_base64)
        item_name = payload.item_name or "upload.bin"
        mime_type = payload.mime_type or "application/octet-stream"
    else:
        text = payload.plaintext or ""
        raw = text.encode("utf-8")
        item_name = payload.item_name or "text_payload.txt"
        mime_type = payload.mime_type or "text/plain"

    try:
        return build_vault_metrics(
            raw,
            algorithm=payload.algorithm,
            signing=payload.signing,
            item_name=item_name,
            item_type=payload.input_kind,
            mime_type=mime_type,
        )
    except VaultFlowError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
