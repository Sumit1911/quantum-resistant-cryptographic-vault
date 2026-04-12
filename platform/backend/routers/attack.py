from fastapi import APIRouter
from pydantic import BaseModel

from services.attack_service import (
    compute_grovers_impact,
    compute_lattice_svp_hardness,
    compute_shors_complexity,
)


router = APIRouter()


class ShorsRequest(BaseModel):
    key_size_bits: int


class GroversRequest(BaseModel):
    algorithm: str


class LatticeRequest(BaseModel):
    dimension: int


@router.post("/shors")
def shors(payload: ShorsRequest) -> dict:
    return compute_shors_complexity(payload.key_size_bits)


@router.post("/grovers")
def grovers(payload: GroversRequest) -> dict:
    return compute_grovers_impact(payload.algorithm)


@router.post("/lattice")
def lattice(payload: LatticeRequest) -> dict:
    return compute_lattice_svp_hardness(payload.dimension)

