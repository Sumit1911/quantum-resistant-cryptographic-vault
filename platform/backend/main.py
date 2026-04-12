from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import attack, auth, benchmark, vault


app = FastAPI(title="Quantum Vault Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(benchmark.router, prefix="/api/benchmark", tags=["benchmark"])
app.include_router(attack.router, prefix="/api/attack", tags=["attack"])
app.include_router(vault.router, prefix="/api/vault", tags=["vault"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
