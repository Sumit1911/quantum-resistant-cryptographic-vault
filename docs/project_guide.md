# Quantum-Resistant Cryptographic Vault: Complete Project Guide

## 1) What This Project Is Doing

This project demonstrates how to design and evaluate a **post-quantum secure vault system**.

It has two active products:

1. **Legacy secure vault app (`app/` + `core/` + `db/`)**
- A real file vault with encryption/signing/storage workflows.
- Built with Streamlit + Python core + SQLite.
- This is where real end-to-end secure file handling is implemented.

2. **Research platform (`platform/backend` + `platform/frontend`)**
- A modern FastAPI + React interface for research demos and analysis.
- Focuses on benchmark comparisons, attack simulations, and vault telemetry visualization.
- Uses analytical models for fast, explainable experimentation.

Together, the repo supports both:
- **Practical implementation** (secure vault behavior), and
- **Academic/research presentation** (comparative metrics and risk analysis).

## 2) High-Level Architecture

### Legacy Vault Path (real secure workflow)

`Streamlit UI -> vault_manager -> auth + crypto + storage -> SQLite`

- `app/` handles user interactions (login, upload, retrieve, settings).
- `core/vault_manager.py` orchestrates complete flows.
- `core/auth.py` handles identity and private-key wrapping.
- `core/crypto.py` handles PQC + AES cryptography.
- `core/storage.py` handles persistence with ownership checks.
- `db/schema.sql` defines `users` and `vault_items`.

### Research Platform Path (simulation + visualization)

`React UI -> hooks -> FastAPI routers -> services (benchmark/attack/metrics)`

- `platform/frontend/src/pages` gives 3 labs: Arena, Attack Lab, Vault Lens.
- `platform/backend/routers` expose `/benchmark`, `/attack`, `/vault`, `/auth`.
- `platform/backend/services` produce telemetry and simulation outputs.

## 3) Core Security Features and How They Work

## 3.1 User Registration and Login

Files:
- `core/auth.py`
- `core/vault_manager.py`

Flow:
1. User registers with username + master password.
2. Password is hashed with **Argon2id** (`hash_master_password`).
3. A PBKDF2 key (`derive_protection_key`) is derived from password + random salt.
4. Kyber and Dilithium keypairs are generated.
5. Private keys are encrypted (wrapped) with AES-GCM using the derived protection key.
6. User record is stored in SQLite.

On login:
1. Username row is fetched.
2. Argon2 hash is verified.
3. PBKDF2 key is derived again from entered password + stored salt.
4. Wrapped private keys are decrypted into memory.
5. Session object returns user ID + PQC key material for runtime operations.

Why this matters:
- Passwords are never stored in plaintext.
- PQC private keys are not stored raw in DB.

## 3.2 File Encryption and Secure Storage

Files:
- `core/vault_manager.py` (`store_file`)
- `core/crypto.py`
- `core/storage.py`

Flow when storing a file:
1. Kyber encapsulation generates `(capsule, shared_secret)`.
2. File bytes are encrypted using **AES-256-GCM** with `shared_secret`.
3. A deterministic signing payload is built from:
- `user_id`
- `item_name`
- `ciphertext`
- `kyber_capsule`
4. Payload is signed using Dilithium private key.
5. DB row is inserted with ciphertext, IV, tag, capsule, signature, metadata.
6. In-memory shared secret buffer is zeroed after use.

What is stored:
- Encrypted bytes (`ciphertext`)
- AES metadata (`aes_iv`, `aes_tag`)
- Kyber capsule (`kyber_capsule`)
- Dilithium signature (`dilithium_signature`)
- Metadata (name, mime, size, user ownership)

## 3.3 Retrieval, Tamper Detection, and Access Control

Files:
- `core/vault_manager.py` (`retrieve_file`)
- `core/storage.py`

Retrieve flow:
1. Item is fetched only if `(item_id, user_id)` match (ownership gate).
2. Signing payload is rebuilt from stored fields.
3. Dilithium signature verification runs **before decryption**.
4. If verification fails, `IntegrityError` is raised and download is blocked.
5. If valid, Kyber decapsulation recovers the shared secret.
6. AES-GCM decrypts and returns plaintext.

Security properties:
- Tampered ciphertext/name/capsule/signature is detected before release.
- One user cannot access another user’s vault item through API/storage calls.

## 3.4 Master Password Rotation

File:
- `core/vault_manager.py` (`change_master_password`)

Flow:
1. Verify old password hash.
2. Derive old protection key and unwrap stored private keys.
3. Create new Argon2 hash and new PBKDF2 salt/key.
4. Re-wrap private keys using new key.
5. Update DB with new hash, new salt, and new wrapped keys.

Effect:
- Cryptographic identity stays the same.
- Protection at rest moves to new master-password-derived key.

## 4) Legacy Streamlit App Features (User-Facing)

Files:
- `app/main.py`
- `app/pages/login.py`
- `app/pages/vault.py`
- `app/pages/settings.py`

Features:
1. **Login/Register page**
- Creates account, validates passwords, starts session after login.

2. **Vault page**
- Upload file -> encrypt/sign/store.
- List stored vault items (metadata only).
- Download item -> verify + decrypt -> Streamlit download button.
- Delete item with confirmation.

3. **Settings page**
- Shows SHA-256 fingerprints of Kyber/Dilithium public keys.
- Allows secure master-password change.

## 5) Research Platform Features (FastAPI + React)

## 5.1 API Backend

Entry file:
- `platform/backend/main.py`

Registered routes:
- `/api/benchmark/*`
- `/api/attack/*`
- `/api/vault/*`
- `/api/auth/*`
- `/health`

### Benchmark API

Files:
- `platform/backend/routers/benchmark.py`
- `platform/backend/services/benchmark_service.py`

Feature:
- Compare classical vs PQC algorithms for operations (`keygen/encrypt/sign/verify`) with configurable iterations and file size.

Output includes:
- `avg_ms`, `p95_ms`, `stddev_ms`
- `ops_per_sec`, `throughput_mbps`
- energy/memory estimates
- quantum risk score
- winner, speedup, and comparative deltas
- generated research insight statements

### Attack Lab API

Files:
- `platform/backend/routers/attack.py`
- `platform/backend/services/attack_service.py`

Modes:
1. **Shor simulation** (`/shors`)
- Models classical vs quantum effort trends for factoring.

2. **Grover impact** (`/grovers`)
- Shows effective security bit reduction for symmetric/hash choices.

3. **Lattice SVP hardness** (`/lattice`)
- Estimates attack effort vs lattice dimension and security level.

4. **Harvest-now, decrypt-later risk** (`/harvest-risk`)
- Generates year-by-year risk growth curve and urgency recommendation.

### Vault Lens API

Files:
- `platform/backend/routers/vault.py`
- `platform/backend/services/metrics_service.py`

Feature:
- Models vault pipeline stages and overhead for given plaintext + PQC choices.

Returns:
- step timings (session key, KEM, AES, signature, precheck, DB write)
- size metrics (ciphertext/capsule/signature)
- overhead and throughput
- quantum readiness score
- interpretation notes

### Auth API (Current State)

File:
- `platform/backend/routers/auth.py`

Status:
- Currently scaffolded (`/login` returns demo token).
- Not yet integrated with full DB-backed auth/session hardening.

## 5.2 React Frontend

Core files:
- `platform/frontend/src/App.tsx`
- `platform/frontend/src/pages/*.tsx`
- `platform/frontend/src/hooks/*.ts`
- `platform/frontend/src/api/client.ts`

Pages:
1. **Overview (`/`)**
- Explains research workflow and links to labs.

2. **Arena (`/arena`)**
- Controls for algorithm pair + operation + iterations + file size.
- Displays race metrics, charts, risk cards, research notes.

3. **Attack Lab (`/attack`)**
- Tabbed Shor/Grover/Lattice/HNDL modes.
- Parameter controls and dynamic visualization cards/charts.

4. **Vault Lens (`/vault`)**
- Select KEM + signature profile, enter plaintext, inspect stage-by-stage metrics.

How data moves:
1. User interacts with page controls.
2. Hook (`useBenchmark`, `useAttack`, `useVault`) calls backend via Axios (`api/client.ts`).
3. Response data populates metric cards, charts, and notes.

## 6) Data Model

File:
- `db/schema.sql`

Tables:
1. `users`
- username
- Argon2 password hash
- PQC public keys
- wrapped PQC private keys
- key-wrapping salt and IVs

2. `vault_items`
- owner (`user_id`)
- encrypted payload data
- AES IV/tag
- Kyber capsule
- Dilithium signature
- size/mime metadata + timestamps

## 7) Testing and Validation

Test folders:
- `tests/unit`
- `tests/integration`
- `tests/security`
- `tests/benchmarks`

Coverage highlights:
1. Unit tests validate auth, crypto, storage, vault manager edge paths.
2. Integration tests verify register/login/store/retrieve/delete end-to-end.
3. Security tests verify:
- tamper detection on ciphertext and metadata
- signature substitution rejection
- wrong-user retrieval denial
4. Benchmark script times Kyber/Dilithium/AES and full store/retrieve flows.

## 8) Developer Utilities

Files:
- `Makefile`
- `scripts/run_project.py`
- `scripts/setup_db.py`
- `scripts/benchmark.py`
- `scripts/keygen.py`

Useful commands:
- `make run-platform` (FastAPI + React)
- `make run-streamlit` (legacy secure vault app)
- `make test` / `make test-all`
- `make setup-db`
- `make benchmark`
- `make keygen`

## 9) Current Project Status (What Is Complete vs In Progress)

Implemented:
1. Real secure vault path in legacy stack with PQC + AES + signature gate.
2. DB-backed user and vault item flows.
3. Comprehensive tests for functional and security behavior.
4. Modern research UI with benchmark/attack/vault instrumentation labs.

In progress / future refinement:
1. Platform auth is still demo-scaffolded.
2. Platform vault endpoint is analytical/telemetry-oriented rather than full persistence workflow.
3. There is duplicated core logic between root `core/` and `platform/backend/core/` that can be unified later.

## 10) One-Line Summary

This project is a dual-stack post-quantum vault system: one side proves real secure storage workflows, and the other side provides a research-grade platform to analyze performance, risk, and cryptographic tradeoffs for final-year project reporting.
