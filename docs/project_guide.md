# Quantum-Resistant Cryptographic Vault: Project Guide

## 1. Project Overview

This project is a single unified **post-quantum cryptographic research platform** built to analyze, visualize, and validate secure vault workflows under both classical and post-quantum assumptions.

The platform combines three tightly connected modules:

1. **Algorithm Arena**
   Benchmarks classical and PQC algorithms in valid comparison families.
2. **Attack Lab**
   Explains modeled quantum pressure through transparent formulas and visual simulations.
3. **Vault Lens**
   Executes a live end-to-end vault pipeline and exposes timing, size, integrity, and overhead metrics.

From a report or viva perspective, this should be presented as **one platform with three analytical views**, not as multiple separate products.

## 2. Core Idea of the Platform

The platform answers three research questions:

1. How do classical and post-quantum algorithms compare in controlled benchmarks?
2. How should quantum-era threat pressure be explained and visualized for different cryptographic families?
3. What happens inside a real post-quantum vault pipeline when data is encrypted, signed, stored, verified, and decrypted?

The frontend is the main user-facing product. The backend powers all calculations, cryptographic execution, and telemetry generation. The platform’s vault logic is backed by the repository’s shared cryptographic core, so the vault analysis page is not a fake mockup.

## 3. Current Platform Structure

### Frontend

Path:

- `platform/frontend`

Technology:

- React
- Vite
- TypeScript
- Axios
- Recharts

Current routes from `platform/frontend/src/App.tsx`:

- `/arena`
- `/attack`
- `/vault`

The root route redirects directly to `/arena`, which means the live product is centered around the three research modules rather than a separate landing/dashboard experience.

### Backend

Path:

- `platform/backend`

Technology:

- FastAPI
- Pydantic
- Python cryptography stack
- `liboqs-python`

Current API routes from `platform/backend/main.py`:

- `/api/benchmark/*`
- `/api/attack/*`
- `/api/vault/*`
- `/api/auth/*`
- `/health`

### Shared Security and Vault Engine

Paths:

- `core/auth.py`
- `core/crypto.py`
- `core/storage.py`
- `core/vault_manager.py`
- `db/schema.sql`

These modules contain the real password protection, cryptography, signing, storage, and vault orchestration logic that the platform reuses for live vault instrumentation.

## 4. Unified Platform Architecture

The current architecture is best described as:

`React UI -> hooks -> FastAPI API -> benchmark/attack/vault services -> shared cryptographic core -> SQLite/local metrics -> visual output`

### Request Flow

1. The user selects inputs in one of the three platform modules.
2. React hooks send requests to the FastAPI backend.
3. Backend services run one of the following:
   - live crypto benchmarks
   - modeled threat calculations
   - live vault pipeline instrumentation
4. The backend returns structured JSON.
5. The frontend renders cards, charts, formula tooltips, logs, and flow visualizations.

### Important Architectural Point

Although the repository still contains earlier prototype code and helper modules, the current product should be described as a **single platform** whose operational center is the `platform/` application and whose cryptographic engine lives in `core/`.

## 5. Platform Modules

## 5.1 Algorithm Arena

Frontend:

- `platform/frontend/src/pages/Arena.tsx`

Backend:

- `platform/backend/routers/benchmark.py`
- `platform/backend/services/benchmark_service.py`

Purpose:

- compare classical and PQC baselines only within valid experiment families
- produce defensible performance telemetry
- expose formulas for derived metrics directly in the UI

Supported experiment families:

1. **KEM / key exchange**
   - classical: `X25519`
   - PQC: `Kyber-512`, `Kyber-768`

2. **Signature**
   - classical: `ECDSA`
   - PQC: `Dilithium3`, `ML-DSA-65`

3. **Hybrid encryption**
   - classical: `RSA-OAEP-AES`
   - PQC: `Kyber-AES-Hybrid`

Current UI capabilities:

- choose family
- choose classical baseline
- choose PQC baseline
- choose iteration count
- choose payload size for encryption family
- inspect comparative metrics
- inspect per-branch metrics
- inspect overhead for both branches
- inspect formula tooltips for derived metrics
- export run JSON

Current displayed metric categories:

- winner
- speedup
- median latency gap
- p95 latency gap
- throughput ratio
- per-branch throughput
- per-branch median / p95 / stddev
- classical and PQC overhead
- iteration-wise latency chart
- machine and methodology metadata

## 5.2 Attack Lab

Frontend:

- `platform/frontend/src/pages/AttackLab.tsx`

Backend:

- `platform/backend/routers/attack.py`
- `platform/backend/services/attack_service.py`

Purpose:

- visualize quantum-era cryptographic pressure
- explain formulas and thresholds in a way that is easy to defend academically
- show the difference between measured performance data and modeled threat analysis

Current modes:

1. **Shor**
   Models asymptotic exposure pressure for RSA/ECC-like public-key systems.

2. **Grover**
   Models effective search-space reduction for symmetric and hash primitives.

3. **Lattice SVP**
   Models relative hardness trends for lattice-based cryptographic assumptions.

4. **HNDL**
   Models harvest-now-decrypt-later risk across a protection horizon.

Current UI capabilities:

- switch between four attack-analysis modes
- enter mode-specific inputs
- inspect verdict and primary model metric
- inspect charts and risk curves
- inspect formula tooltips directly on cards
- inspect the backend-provided formula panel for transparency

Current displayed metric categories:

- verdict
- break ratio
- bit reduction
- security band
- risk horizon
- threshold crossing year
- recommendation
- classical vs quantum trend curves
- formula panel and assumptions

## 5.3 Vault Lens

Frontend:

- `platform/frontend/src/pages/Vault.tsx`

Backend:

- `platform/backend/routers/vault.py`
- `platform/backend/services/metrics_service.py`

Purpose:

- run a live post-quantum vault flow in the backend
- show how secure vault operations behave in practice
- expose step-by-step timings and overhead for report-ready explanation

Current user inputs:

- text or file payload
- KEM algorithm
- signature scheme

Current KEM options:

- `Kyber-512`
- `Kyber-768`

Current signature options:

- `Dilithium3`
- `ML-DSA-65`

Current displayed outputs:

- total time
- quantum readiness score
- roundtrip success check
- plaintext size
- ciphertext size
- overhead percent
- throughput
- step-by-step flow visualization
- terminal-style operation log
- backend research notes

This module is the strongest proof in the platform that the vault pipeline is live rather than static, because the backend actually performs encryption, signing, storage, verification, decapsulation, and decryption in sequence.

## 6. Cryptographic Design

## 6.1 Password Protection

Implemented in:

- `core/auth.py`

Algorithms and methods:

- **Argon2id** for password hashing
- **PBKDF2-HMAC-SHA256** for deriving a 256-bit protection key
- **AES-GCM** for wrapping private keys before storage

What this provides:

- no plaintext passwords in storage
- no raw private keys stored directly in the database
- deterministic login restoration of protected key material

## 6.2 Post-Quantum Primitives

Implemented in:

- `core/crypto.py`

Current PQC building blocks:

- **Kyber / ML-KEM family** for key encapsulation
- **Dilithium / ML-DSA family** for signatures
- **AES-256-GCM** for payload encryption

Core cryptographic helper functions include:

- key generation
- encapsulation and decapsulation
- signing and verification
- deterministic signing payload construction
- authenticated encryption and decryption

## 6.3 Classical Comparison Primitives

Used mainly in Arena and benchmark services:

- `X25519`
- `ECDSA` on `SECP256R1`
- `RSA-2048 OAEP`
- `AES-GCM`

These are not random comparisons. The backend validates that comparisons stay within the same operation family.

## 7. Real Vault Pipeline Used by the Platform

The current platform’s vault instrumentation is built on the repository’s real vault core.

### Live flow in Vault Lens

Implemented in:

- `platform/backend/services/metrics_service.py`

Runtime sequence:

1. Initialize or reuse a demo vault session
2. Encapsulate a shared secret with the selected KEM
3. Encrypt the payload using AES-GCM
4. Build a deterministic signing payload
5. Sign that payload using the selected signature scheme
6. Write the encrypted artifact to SQLite
7. Verify the signature before release
8. Decapsulate the shared secret
9. Decrypt and compare recovered plaintext

This is why Vault Lens can legitimately be described as a **live instrumentation view of the platform’s secure vault engine**.

## 8. Data Model

Schema:

- `db/schema.sql`

### `users`

Stores:

- username
- password hash
- public keys
- wrapped private keys
- KDF salt
- private-key IVs

### `vault_items`

Stores:

- user ownership
- item name and type
- metadata nonce
- ciphertext
- AES IV and tag
- Kyber capsule
- Dilithium signature
- original size
- mime type

Even though the user-facing experience is now framed as one platform, the secure storage model underneath remains a real vault model with ownership checks and tamper-protected records.

## 9. Metric Types Across the Platform

The platform shows three different classes of metrics.

## 9.1 Measured Metrics

These come from actual code execution:

- Arena latency samples
- Arena median / p95 / stddev
- Arena output-size overhead
- Vault Lens step timings
- Vault Lens total latency
- Vault Lens ciphertext / capsule / signature sizes
- Vault Lens roundtrip validation

## 9.2 Derived Metrics

These are calculated from measured outputs:

- speedup factor
- throughput ratio
- ops per second
- MB/s throughput
- latency gap
- overhead percent

## 9.3 Modeled Metrics

These are explanatory rather than experimentally measured:

- quantum risk score in Arena
- Attack Lab verdicts
- Shor break ratio model
- Grover bit-reduction model
- lattice security band model
- harvest-now-decrypt-later risk horizon
- quantum readiness score in Vault Lens

This distinction is important in a final report. The platform is strongest when it clearly separates **measured**, **derived**, and **modeled** outputs.

## 10. Current Backend Services

## 10.1 Benchmark Service

Path:

- `platform/backend/services/benchmark_service.py`

Responsibilities:

- validate experiment families and algorithm pairs
- run warm-up loops
- time only the benchmarked crypto operation block
- summarize median, average, p95, stddev, throughput, and overhead
- return methodology metadata for defensible reporting

## 10.2 Attack Service

Path:

- `platform/backend/services/attack_service.py`

Responsibilities:

- compute Shor, Grover, lattice, and HNDL model outputs
- return formula metadata
- return curves and verdicts used by the frontend

## 10.3 Vault Metrics Service

Path:

- `platform/backend/services/metrics_service.py`

Responsibilities:

- execute a live vault flow
- record step timings
- calculate size and overhead metrics
- validate recovered plaintext
- generate researcher-friendly interpretation notes

## 10.4 Auth Router

Path:

- `platform/backend/routers/auth.py`

Current status:

- present in the API surface
- currently scaffolded
- returns a demo token rather than full production authentication/session handling

For documentation purposes, this should be described as **platform API scaffolding for future access control integration**, not as a finished authentication subsystem.

## 11. Frontend Experience

The frontend is designed as a research workstation rather than a general consumer app.

### Navigation

Current top navigation:

- Arena
- Attack Lab
- Vault Lens

### Interaction style

The current UI emphasizes:

- parameterized experiments
- card-based result summaries
- chart-driven comparison
- formula-on-hover explanations
- visual flow trace for vault execution

### Formula transparency

The current codebase now exposes formulas directly on metric cards in Arena and Attack Lab through the `MetricCard` component. This is especially useful for report demonstrations because it allows you to explain not just the result, but also the method.

## 12. Testing and Validation

Main test areas:

- `tests/unit`
- `tests/integration`
- `tests/security`
- `tests/benchmarks`

Coverage focus:

1. unit validation of auth, crypto, storage, and vault orchestration
2. integration validation of register/login/store/retrieve/delete flows
3. security validation of tamper detection, wrong-user access denial, replay resistance, and signature substitution rejection
4. benchmark validation through repeatable timing scripts and harnesses

From a project-report standpoint, these tests support the claim that the platform is not only visual, but also backed by validated cryptographic behavior.

## 13. How to Present This Project Cleanly in a Report

Recommended project framing:

> The project is a unified post-quantum cryptographic vault platform with three integrated analysis modules: Algorithm Arena for benchmark-driven comparison, Attack Lab for transparent quantum-threat modeling, and Vault Lens for live instrumentation of the secure vault pipeline. The platform uses a shared cryptographic engine for password protection, PQC key exchange, digital signatures, authenticated encryption, and tamper-resistant storage, while exposing both measured and modeled outputs through a modern React and FastAPI interface.

That framing matches the current codebase much better than describing it as multiple separate products.

## 14. Current Scope and Honest Limitations

1. The platform is unified at the product level, but some earlier prototype code still exists in the repository.
2. The Auth API is still scaffolded and not yet a full production auth layer.
3. Attack Lab metrics are models, not empirical attack benchmarks.
4. Vault Lens uses a managed backend demo session for live instrumentation rather than a complete end-user account flow inside the React platform.
5. Some presentational scores, such as quantum readiness or quantum risk, are heuristic overlays rather than formally derived security proofs.

These limitations should be acknowledged briefly in technical documentation, but they do not change the fact that the current deliverable is best understood and presented as a **single coherent platform**.

## 15. One-Line Summary

This codebase now presents a single post-quantum cryptographic vault platform where benchmarking, threat modeling, and live vault execution all operate as connected modules on top of the same underlying cryptographic engine.
