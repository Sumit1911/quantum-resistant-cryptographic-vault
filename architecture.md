# Quantum Vault Architecture
## Current Codebase Reference (Updated: April 12, 2026)

---

## 1) Project Reality: Two Active Stacks

This repository currently contains **two runnable products**:

1. **Legacy Vault App (Stable + Fully Tested)**
- Stack: Streamlit + Python core + SQLite + liboqs
- Path roots: `app/`, `core/`, `db/`, `tests/`
- Purpose: secure file vault proof-of-concept with real crypto flow

2. **Research Platform (Modern UX + Simulation Layer)**
- Stack: FastAPI backend + React frontend
- Path roots: `platform/backend`, `platform/frontend`
- Purpose: comparative benchmarking, attack simulation, and vault telemetry visualization

Recommended user-facing path for demos/reports: **platform/**

---

## 2) Repository Structure (As Implemented)

```text
/Users/yasmodi/Documents/Project
├── app/                          # Streamlit legacy UI
├── core/                         # Real auth/crypto/storage/orchestration modules
├── db/
│   ├── schema.sql
│   └── migrations/
├── docs/                         # architecture/api/threat docs
├── platform/
│   ├── backend/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   ├── core/                 # mirrored core modules for platform backend context
│   │   └── db/schema.sql
│   └── frontend/
│       └── src/
│           ├── pages/
│           ├── components/
│           ├── hooks/
│           └── api/client.ts
├── scripts/                      # setup, benchmark, keygen, unified runner
├── tests/                        # unit/integration/security/benchmark
├── Makefile
├── README.md
└── architecture.md
```

---

## 3) Runtime Architecture

## 3.1 Legacy Vault Runtime (Production-Crypto Path)

```text
Streamlit UI (app/main.py + pages)
        │
        ▼
vault_manager.py (orchestrator)
        │
 ┌──────┼───────────────┐
 ▼      ▼               ▼
auth.py crypto.py     storage.py
        │               │
        └──────► SQLite (vault.db)
```

Core guarantees in this path:
- Kyber encapsulation/decapsulation for session key exchange
- Dilithium/ML-DSA signatures for tamper gate
- AES-256-GCM encryption for payload confidentiality + integrity
- Ownership-gated data retrieval and deletion
- Signature verification before decryption

## 3.2 Platform Runtime (Research + Visualization Path)

```text
React (Vite)
  pages: Dashboard, Arena, AttackLab, Vault
        │ axios
        ▼
FastAPI
  routers: /benchmark, /attack, /vault, /auth
        │
  services: benchmark_service, attack_service, metrics_service
```

Platform backend currently focuses on **analytical simulation telemetry**, not full DB-backed user vault CRUD.

---

## 4) Backend (platform/backend) Detailed Design

## 4.1 Entry Point

File: `platform/backend/main.py`

Responsibilities:
- FastAPI app creation
- CORS for `http://localhost:5173`
- Router mounting:
  - `/api/benchmark`
  - `/api/attack`
  - `/api/vault`
  - `/api/auth`
- Health endpoint: `GET /health`

## 4.2 Routers and Contracts

### Benchmark Router
File: `platform/backend/routers/benchmark.py`

Endpoint:
- `POST /api/benchmark/run`

Request body:
```json
{
  "classical_algo": "RSA-2048|RSA-4096|ECDSA|X25519",
  "pqc_algo": "Kyber-512|Kyber-768|Dilithium2|Dilithium3",
  "operation": "keygen|encrypt|sign|verify",
  "iterations": 80,
  "file_size_mb": 1
}
```

Response highlights:
- Per-branch: `avg_ms`, `p95_ms`, `stddev_ms`, `ops_per_sec`, `throughput_mbps`
- Security telemetry: `security_bits_quantum`, `quantum_risk_score`
- Resource telemetry: `energy_mj`, `memory_kb`
- Comparative section: latency and throughput deltas
- Generated `research_insights[]`

### Attack Router
File: `platform/backend/routers/attack.py`

Endpoints:
- `POST /api/attack/shors`
- `POST /api/attack/grovers`
- `POST /api/attack/lattice`
- `POST /api/attack/harvest-risk`

Modes:
1. **Shor**
- Fields: `break_ratio`, `classical_curve`, `quantum_curve`, `snapshot`, `verdict`
2. **Grover**
- Fields: `effective_reduction_percent`, `bars[]`, `recommendation`, `verdict`
3. **Lattice SVP**
- Fields: `security_level`, `bkz_block_size`, attack curves, lattice points
4. **Harvest-Now/Decrypt-Later (HNDL)**
- Fields: `risk_curve[]`, `risk_today_percent`, `risk_horizon_percent`, `compromise_year_estimate`, `recommendation`

### Vault Router
File: `platform/backend/routers/vault.py`

Endpoint:
- `POST /api/vault/encrypt`

Request:
```json
{
  "plaintext": "...",
  "algorithm": "Kyber-512|Kyber-768",
  "signing": "Dilithium2|Dilithium3|ML-DSA-65"
}
```

Response:
- Stage timings (`steps[]`) for cryptographic pipeline
- Output sizes per step
- Total timing
- Overhead and throughput metrics
- Quantum readiness score
- Research interpretation notes

### Auth Router
File: `platform/backend/routers/auth.py`

Endpoint:
- `POST /api/auth/login`

Current state:
- Scaffold/demo response (`token: demo-token`)
- Not yet integrated with full auth/session model

## 4.3 Services

### benchmark_service.py
Models benchmark race with deterministic seeded variability and emits:
- Time series + statistical spread
- Quantum risk quantization
- Energy/memory proxies
- Comparative analytics for report-ready interpretation

### attack_service.py
Implements four simulation families:
- Shor complexity growth
- Grover post-quantum key-space reduction
- Lattice SVP hardness trends
- HNDL long-horizon confidentiality risk

### metrics_service.py
Implements vault instrumentation model:
- session key gen
- KEM encapsulation
- AEAD encryption
- signature generation
- pre-release signature gate
- DB write phase

Outputs both pipeline and overhead economics.

---

## 5) Frontend (platform/frontend) Detailed Design

## 5.1 App Shell

File: `platform/frontend/src/App.tsx`

- Top navigation with active-route highlight
- Routes:
  - `/` -> Dashboard
  - `/arena` -> Algorithm Arena
  - `/attack` -> Attack Lab
  - `/vault` -> Vault Lens

## 5.2 Visual System

File: `platform/frontend/src/index.css`

- Design tokens via CSS variables
- Dual-font system:
  - `Space Grotesk` for narrative/UI
  - `IBM Plex Mono` for technical signals
- Layered gradients + atmospheric orbs
- Metric cards with semantic tones (`neutral`, `good`, `warn`)
- Responsive layout rules for mobile and desktop

## 5.3 Pages

### Dashboard (`pages/Dashboard.tsx`)
- Overview narrative
- Entry CTA to all three labs
- Research workflow guidance

### Arena (`pages/Arena.tsx`)
- Full control surface for algorithm/operation/iterations/file size
- Output panels for winner, speedup, energy reduction, risk, throughput
- Live line chart + normalized race bars
- auto-generated notes from backend insights

### Attack Lab (`pages/AttackLab.tsx`)
- Tabbed simulation modes: Shor, Grover, Lattice, HNDL
- Mode-specific parameter controls
- Dynamic cards and mode-specific visuals:
  - Attack complexity chart
  - Grover security bars
  - HNDL risk timeline

### Vault Lens (`pages/Vault.tsx`)
- Configurable KEM/signature profile
- Plaintext test payload input
- Pipeline cards, overhead cards, flow visualizer, execution log
- Research notes rendering

## 5.4 Shared Components

- `MetricCard.tsx` -> standardized numeric insight card
- `LiveChart.tsx` -> latency evolution chart
- `AttackCurve.tsx` -> complexity curve chart
- `RiskTimeline.tsx` -> HNDL risk-by-year chart
- `AlgoRaceBar.tsx` -> comparative bar tracks
- `FlowVisualizer.tsx` -> animated pipeline stage cards
- `TerminalLog.tsx` -> ordered event stream
- `CryptoLoader.tsx` -> animated cryptographic loading state

## 5.5 Data Access Layer

- `api/client.ts`: axios base client (`http://127.0.0.1:8000/api`)
- Hooks:
  - `useBenchmark.ts`
  - `useAttack.ts`
  - `useVault.ts`
- Hooks manage loading, error, and data state per lab

---

## 6) Security & Crypto Core (Legacy/Shared Core)

Core files:
- `core/crypto.py`
- `core/auth.py`
- `core/storage.py`
- `core/vault_manager.py`

Implemented capabilities:
- Argon2 password hashing
- PBKDF2-based key wrapping protection
- Kyber KEM encapsulation/decapsulation
- Dilithium/ML-DSA sign/verify
- AES-256-GCM encrypt/decrypt
- deterministic signing payload construction
- ownership-gated retrieval + tamper rejection

---

## 7) Testing & Validation Status

Current validated status:
- `pytest -q` -> 39 passing tests
- Test domains covered:
  - unit
  - integration
  - security
- Frontend build validated (`npm run build`)
- Backend syntax validated (`python -m compileall`)

Known warning:
- `liboqs` native version and `liboqs-python` wrapper minor mismatch warning

---

## 8) Run & Developer Experience

Unified execution helpers now available:

- `make run-platform` -> backend + frontend together
- `make run-streamlit` -> legacy vault app
- `make run-backend`, `make run-frontend`
- `python3 scripts/run_project.py <target>` alternative

Documentation entrypoint:
- `README.md` now reflects dual-stack reality and command-first onboarding

---

## 9) Current Gaps (Explicit)

1. Platform auth router is still scaffold-level and not session-hardened.
2. Platform backend currently emits simulation/analytical metrics rather than full persisted benchmark history.
3. Legacy core and platform core modules are duplicated; long-term cleanup should converge to one shared import surface.
4. Frontend chunk size is large; route-level code splitting is recommended.

---

## 10) Recommended Next Refactor (if we continue)

1. Create shared package (`shared_core/`) and remove duplicated core modules.
2. Wire platform auth/vault endpoints to real DB-backed workflows from `core/vault_manager.py`.
3. Add persistent experiment runs table (`benchmark_runs`, `attack_runs`) for exportable report evidence.
4. Add code-splitting per page in React routes.
5. Add CI workflow for `pytest` + frontend build on every push.

---

This document now reflects the **actual implemented architecture**, not a target-only design.
