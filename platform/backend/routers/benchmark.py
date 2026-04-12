from fastapi import APIRouter
from pydantic import BaseModel

from services.benchmark_service import run_benchmark


router = APIRouter()


class BenchmarkRequest(BaseModel):
    classical_algo: str
    pqc_algo: str
    operation: str
    iterations: int = 100
    file_size_mb: int = 1


@router.post("/run")
def benchmark_run(payload: BenchmarkRequest) -> dict:
    return run_benchmark(payload.model_dump())

