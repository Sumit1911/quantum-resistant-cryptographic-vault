# Quantum-Resistant Cryptographic Vault

Post-quantum security project with two runnable stacks:

- `app/` legacy Streamlit vault (fully tested core flows)
- `platform/` modern FastAPI + React research platform (Arena, Attack Lab, Vault Lens)

## Quick Start

Run from project root:

```bash
make run-platform
```

This starts:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

## Other Common Commands

```bash
make run-streamlit   # legacy Streamlit app
make run-backend     # platform backend only
make run-frontend    # platform frontend only
make test            # quick tests
make test-all        # unit + integration + security
make setup-db        # initialize vault.db
make benchmark       # benchmark report
make keygen          # key generation utility
```

You can also use the unified runner directly:

```bash
python3 scripts/run_project.py platform
python3 scripts/run_project.py streamlit
```

## Clean Project Structure

```text
.
├── app/                # Streamlit UI
├── core/               # Auth, crypto, storage, vault orchestration
├── db/                 # Schema + migrations
├── docs/               # Architecture/API/threat model docs
├── platform/
│   ├── backend/        # FastAPI API services
│   └── frontend/       # React + Vite app
├── scripts/            # Setup, benchmark, keygen, unified runner
└── tests/              # Unit/integration/security/benchmarks
```

## Install Notes

- Python deps (legacy + tests): `pip install -r requirements.txt`
- Platform backend deps: `pip install -r platform/backend/requirements.txt`
- Platform frontend deps: `cd platform/frontend && npm install`

If `liboqs` is not available, install native `liboqs` first, then `liboqs-python`.
