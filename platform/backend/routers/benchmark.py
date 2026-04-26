from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.benchmark_service import run_benchmark


router = APIRouter()


class BenchmarkRequest(BaseModel):
    experiment_family: str = "kem"
    classical_algo: str
    pqc_algo: str
    operation: str
    iterations: int = 100
    file_size_mb: int = 1


@router.post("/run")
def benchmark_run(payload: BenchmarkRequest) -> dict:
    try:
        return run_benchmark(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
