# PQC Platform Full Technical Documentation

## 1. Executive Summary

This repository is not a single application. It is a dual-track post-quantum cryptography project with:

1. A real secure vault implementation in `app/`, `core/`, `db/`, and `tests/`
2. A research and visualization platform in `platform/backend` and `platform/frontend`

The secure vault path performs real cryptographic work on the local machine:

- password hashing with Argon2id
- password-derived key generation with PBKDF2-HMAC-SHA256
- Kyber KEM encapsulation/decapsulation through `liboqs-python`
- Dilithium or ML-DSA signatures through `liboqs-python`
- AES-256-GCM encryption/decryption through `cryptography`
- SQLite persistence with ownership checks and signature-first retrieval

The research platform is mixed:

- `Vault Lens` executes a real local crypto pipeline and records timing per step
- `Algorithm Arena` measures real crypto operations for benchmark races
- `Attack Lab` is not a cryptanalytic engine; it is a transparent heuristic modeling layer for research storytelling

That distinction matters for authenticity. Some numbers in this project are measured from actual code execution, and some are intentionally estimated for analysis and visualization.

## 2. What the Project Shows

The platform groups into three feature categories.

### 2.1 Secure Vault Features

These features come from the legacy but fully implemented vault stack:

- user registration and login
- password hashing and password-derived wrapping keys
- PQC public/private key generation
- private key wrapping before database storage
- file encryption and authenticated storage
- tamper detection before decryption
- ownership-based access control
- secure file retrieval and deletion
- master password rotation without changing cryptographic identity

Main files:

- `core/auth.py`
- `core/crypto.py`
- `core/storage.py`
- `core/vault_manager.py`
- `db/schema.sql`
- `app/pages/login.py`
- `app/pages/vault.py`
- `app/pages/settings.py`

### 2.2 Research Platform Features

The FastAPI + React platform exposes three labs.

#### Algorithm Arena

Purpose:

- compare classical and PQC schemes only inside valid operation families
- report latency, p95, standard deviation, throughput, and overhead
- export run JSON for research reporting

Supported comparison families:

- KEM / key exchange: `X25519` vs `Kyber-512` or `Kyber-768`
- signatures: `ECDSA` vs `Dilithium3` or `ML-DSA-65`
- hybrid encryption: `RSA-OAEP-AES` vs `Kyber-AES-Hybrid`

#### Attack Lab

Purpose:

- visualize quantum threat pressure and long-horizon exposure
- explain security impact using simple formulas that are visible in the UI

Modes:

- Shor mode
- Grover mode
- lattice SVP hardness mode
- harvest-now-decrypt-later mode

#### Vault Lens

Purpose:

- run the vault pipeline locally and show step-by-step timings
- report payload size, overhead, throughput, and a recovery check
- help explain what happens during encapsulate -> encrypt -> sign -> store -> verify -> decapsulate -> decrypt

Main files:

- `platform/backend/services/benchmark_service.py`
- `platform/backend/services/attack_service.py`
- `platform/backend/services/metrics_service.py`
- `platform/frontend/src/pages/Arena.tsx`
- `platform/frontend/src/pages/AttackLab.tsx`
- `platform/frontend/src/pages/Vault.tsx`

### 2.3 Validation and Benchmark Features

The repo also includes:

- unit tests for auth, crypto, storage, and vault orchestration
- integration tests for full register/login/store/retrieve/delete flows
- security tests for tamper, replay, wrong-user access, and signature substitution
- a simple benchmark runner
- a reproducible multi-trial benchmark harness with baselines

Main files:

- `tests/unit/*`
- `tests/integration/*`
- `tests/security/*`
- `tests/benchmarks/bench_crypto.py`
- `core/benchmark_harness.py`
- `scripts/benchmark_harness.py`

## 3. System Architecture

### 3.1 Real Vault Path

Execution path:

`Streamlit UI -> vault_manager -> auth/crypto/storage -> SQLite`

Detailed flow:

1. User registers or logs in from the Streamlit UI.
2. `core/auth.py` verifies password material and unwraps PQC private keys into memory.
3. `core/vault_manager.py` coordinates storage and retrieval.
4. `core/crypto.py` performs KEM, signature, and AES operations.
5. `core/storage.py` persists ciphertext and metadata in SQLite.
6. Retrieval verifies signature before any decryption attempt.

### 3.2 Research Platform Path

Execution path:

`React page -> hook -> Axios client -> FastAPI router -> backend service -> response -> charts/cards`

Important detail:

- the frontend adds a random artificial wait of 2 to 5 seconds through `platform/frontend/src/utils/simulationDelay.ts`
- this delay affects perceived UI responsiveness
- it does not affect backend-reported crypto timings or benchmark statistics

## 4. Algorithms and Cryptographic Building Blocks

## 4.1 Password and Key Protection

### Argon2id

Used for:

- hashing the master password during registration
- verifying the entered password during login

Implementation:

- `hash_master_password`
- `verify_master_password`
- file: `core/auth.py`

Configured parameters:

- time cost: `3`
- memory cost: `65536`
- parallelism: `2`

### PBKDF2-HMAC-SHA256

Used for:

- deriving a 256-bit protection key from the master password and random salt
- encrypting wrapped private keys at rest

Implementation:

- `derive_protection_key`
- `PBKDF2_ITERATIONS = 390_000`
- `KEY_DERIVATION_SALT_SIZE = 16`
- file: `core/auth.py`

### AES-256-GCM

Used for:

- file payload encryption
- wrapped private key encryption
- authenticated decryption and tamper rejection

Implementation:

- `aes_encrypt`
- `aes_decrypt`
- files: `core/crypto.py`, `core/auth.py`

Properties:

- 32-byte key
- 12-byte IV
- 16-byte GCM tag
- confidentiality and integrity are both provided by AEAD

## 4.2 Post-Quantum Algorithms

### Kyber / ML-KEM Family

Used for:

- session key establishment in the vault flow
- PQC baseline in Arena and benchmark harness

Implementation:

- default core path uses `Kyber512`
- helper functions: `generate_kyber_keypair`, `kyber_encapsulate`, `kyber_decapsulate`
- file: `core/crypto.py`

Additional platform behavior:

- `Vault Lens` supports `Kyber-768` through a service-level branch in `platform/backend/services/metrics_service.py`
- for `Kyber-768`, the service creates an ephemeral KEM keypair for the run rather than using the demo user keypair

Meaning:

- `Kyber-512` in the core vault is a true user-key-based flow
- `Kyber-768` in `Vault Lens` is still a real KEM execution, but it is a run-local experimental path rather than the exact same persistent-key path used by the legacy vault

### Dilithium / ML-DSA Family

Used for:

- signing a deterministic payload built from vault metadata and ciphertext
- verifying integrity before decryption
- PQC signature comparisons in Arena

Implementation:

- `generate_dilithium_keypair`
- `dilithium_sign`
- `dilithium_verify`
- file: `core/crypto.py`

Mechanism selection behavior:

- the code checks `liboqs` for enabled mechanisms
- it prefers the first supported candidate from `("Dilithium3", "ML-DSA-65")`

Important authenticity caveat:

- some UI controls label the run as `Dilithium3` or `ML-DSA-65`
- but the low-level helper in `core/crypto.py` resolves to the first available supported mechanism
- that means signature labeling can be more specific than the actual execution path when both names are available

This does not make the flow fake, but it does mean the signature family selection is not perfectly isolated in every platform view.

## 4.3 Classical Comparison Algorithms

Used in the research platform and harness:

- `X25519` for classical key exchange comparison
- `ECDSA` over `SECP256R1` for classical signature comparison
- `RSA-2048 OAEP` for classical key wrapping in hybrid encryption comparison
- `AES-GCM` for symmetric payload encryption in both classical and PQC hybrid paths

Main file:

- `platform/backend/services/benchmark_service.py`
- `core/benchmark_harness.py`

## 5. Data Storage Model

## 5.1 Users Table

Stored fields include:

- username
- Argon2 password hash
- Kyber public key
- wrapped Kyber private key
- Dilithium public key
- wrapped Dilithium private key
- PBKDF2 salt
- IVs for wrapped private keys

Schema file:

- `db/schema.sql`

## 5.2 Vault Items Table

Stored fields include:

- `user_id`
- `item_name`
- `item_type`
- `metadata_nonce`
- `ciphertext`
- `aes_iv`
- `aes_tag`
- `kyber_capsule`
- `dilithium_signature`
- `original_size`
- `mime_type`

Security meaning:

- plaintext is never stored in the database
- metadata nonce becomes part of the signing payload to make replay/substitution harder
- retrieval is ownership-gated and integrity-gated

## 6. How the Real Vault Pipeline Works

## 6.1 Registration

Code path:

- `core/auth.py::register_user`

Steps:

1. Hash password with Argon2id.
2. Create random PBKDF2 salt.
3. Derive a 32-byte protection key from password + salt.
4. Generate Kyber and Dilithium keypairs.
5. Wrap both private keys with AES-GCM using the derived protection key.
6. Store wrapped keys and public keys in SQLite.

## 6.2 Login

Code path:

- `core/auth.py::login_user`

Steps:

1. Load the user row by username.
2. Verify Argon2id hash.
3. Re-derive protection key from entered password and stored salt.
4. Unwrap Kyber and Dilithium private keys.
5. Return a session dictionary containing live key material for runtime use.

## 6.3 Store File

Code path:

- `core/vault_manager.py::store_file`

Steps:

1. Encapsulate a shared secret using the user’s Kyber public key.
2. Convert the shared secret to a mutable buffer.
3. Encrypt the file bytes with AES-256-GCM.
4. Zero the mutable shared-secret buffer after use.
5. Generate a random `metadata_nonce`.
6. Build a deterministic signing payload from:
   - `user_id`
   - file name
   - metadata nonce
   - ciphertext
   - Kyber capsule
7. Sign that payload with the user’s Dilithium private key.
8. Persist ciphertext, IV, tag, capsule, signature, and metadata to SQLite.

## 6.4 Retrieve File

Code path:

- `core/vault_manager.py::retrieve_file`

Steps:

1. Fetch the vault item only if both `item_id` and `user_id` match.
2. Rebuild the exact signing payload from stored values.
3. Verify the Dilithium signature first.
4. Stop immediately with `IntegrityError` if signature verification fails.
5. Decapsulate the Kyber shared secret.
6. Decrypt using AES-256-GCM.
7. Raise `IntegrityError` if GCM tag validation fails.
8. Zero the mutable shared-secret buffer.

Why this is important:

- ciphertext tampering is blocked
- metadata tampering is blocked
- signature substitution is blocked
- unauthorized cross-user reads are blocked

## 6.5 Master Password Rotation

Code path:

- `core/vault_manager.py::change_master_password`

Steps:

1. Verify the old password.
2. Unwrap existing private keys using the old derived protection key.
3. Create a new Argon2 hash and new PBKDF2 salt.
4. Derive a new protection key.
5. Re-wrap the same PQC private keys with the new key.
6. Update the user record.

Effect:

- user identity and PQC keypairs remain the same
- at-rest protection changes to the new password-derived key

## 7. What Each Platform Page Shows

## 7.1 Algorithm Arena

Files:

- `platform/frontend/src/pages/Arena.tsx`
- `platform/backend/services/benchmark_service.py`

Displayed metric categories:

- winner
- speedup factor
- median latency gap
- p95 latency gap
- throughput ratio
- per-branch median, p95, and standard deviation
- ciphertext overhead
- capsule or signature overhead
- machine metadata
- methodology metadata
- raw per-iteration timeseries for the chart

Interpretation:

- this is the platform’s experimental comparison page
- it deliberately restricts the user to "same-family" comparisons so invalid comparisons like RSA signing vs Kyber KEM are not allowed

## 7.2 Attack Lab

Files:

- `platform/frontend/src/pages/AttackLab.tsx`
- `platform/backend/services/attack_service.py`

Displayed categories:

- verdict
- break ratio or effective bit reduction
- security band model
- risk horizon
- threshold crossing year
- classical vs quantum trend curves
- formula panels showing how the values were derived

Interpretation:

- this page is a modeling page, not a measured benchmark page
- its value is transparency and explainability, not lab-grade cryptanalytic precision

## 7.3 Vault Lens

Files:

- `platform/frontend/src/pages/Vault.tsx`
- `platform/backend/services/metrics_service.py`

Displayed categories:

- total execution time
- quantum readiness score
- roundtrip success check
- plaintext size
- ciphertext size
- capsule size
- signature size
- total overhead bytes
- overhead percent
- throughput in MB/s
- tamper detection window
- stage-by-stage timings
- terminal-style step log

Interpretation:

- this is the closest page to a true local execution trace
- it performs real cryptographic operations and a real SQLite write
- it is suitable for explaining the runtime pipeline in a project defense

## 8. How the Metrics Are Calculated

This section is the most important one for authenticity.

## 8.1 Arena Metrics

File:

- `platform/backend/services/benchmark_service.py`

### What is actually measured

Each benchmark branch runs an operation function multiple times. Timing uses:

- `time.perf_counter()` before the operation block
- `time.perf_counter()` after the operation block

Only the crypto operation block is measured.

Explicit boundary from the code:

- API overhead is excluded
- JSON serialization is excluded
- database work is excluded
- logging is excluded
- frontend rendering is excluded

### Warm-up and iteration logic

- warm-up runs happen first and are excluded from reported output
- measured runs are stored as per-iteration samples
- default backend minimum is 5 iterations
- UI default is 80 iterations for Arena

### Reported latency metrics

- `median_ms`: median of measured latencies
- `avg_ms`: arithmetic mean
- `p95_ms`: custom 95th percentile from sorted samples
- `stddev_ms`: population standard deviation

Why median is used:

- it is more stable than average when individual samples spike
- this is appropriate for performance demos on a local machine

### Throughput calculations

For KEM and signature families:

- throughput is reported as operations per second
- internally derived from median latency

Formula:

- `ops_per_sec = 1000 / median_ms`

For encryption family:

- throughput is reported as MB/s

Formula:

- `throughput_MBps = payload_size_mb / (median_ms / 1000)`

### Overhead calculations

For encryption payload overhead:

- `ciphertext_overhead_bytes = (len(ciphertext) - len(payload)) + len(tag)`

For PQC or classical wrapper/signature overhead:

- KEM/signature families mostly use `capsule_signature_overhead_bytes`
- encryption family adds wrapped-key or capsule/wrapped-AES metadata sizes

### Quantum risk score

This value is not measured.

It is assigned from a fixed lookup table:

- classical algorithms receive higher risk scores
- PQC algorithms receive lower risk scores

Meaning:

- this is a presentation-layer research indicator
- it is not produced by live cryptanalysis

### Authenticity rating for Arena

- latency: high authenticity for the measured crypto block
- throughput: derived from measured latency, so reasonably authentic
- overhead bytes: highly authentic because they come from actual output lengths
- risk score: heuristic
- energy estimate: not actually implemented in current backend despite frontend/high-level copy mentioning energy
- "winner": authentic only relative to the measured median timing of the chosen block

## 8.2 Attack Lab Metrics

File:

- `platform/backend/services/attack_service.py`

All Attack Lab outputs are modeled.

### Shor Mode

Uses:

- classical formula family: `2^(n/18)`
- quantum formula family: `2^((log2(n))*2.5)`
- `break_ratio_model = classical / quantum`

Meaning:

- this is a heuristic asymptotic pressure model
- it is not a hardware-calibrated runtime estimator
- it is useful for relative visualization only

### Grover Mode

Uses:

- `post_grover_bits = classical_bits / 2`

Meaning:

- this is the textbook-style search-space reduction intuition
- it is not a direct break-time forecast

### Lattice Mode

Uses:

- `bkz_block_size_proxy = max(180, int(dimension * 0.76))`
- classical estimate: `2^(0.292 * beta)`
- quantum estimate: `2^(0.265 * beta)`

Meaning:

- this is a coarse hardness trend model
- not a full security reduction
- not a rigorous attack cost bound

### Harvest-Now-Decrypt-Later Mode

Uses:

- logistic growth curve scaled by value multiplier
- years-to-protect and data-value class drive the curve

Meaning:

- useful for migration planning narrative
- not a real forecast of when quantum computers will break deployed systems

### Authenticity rating for Attack Lab

- threat education value: good
- mathematical transparency: good
- empirical validity as a benchmark: low
- direct real-world forecasting accuracy: intentionally limited

Attack Lab should be presented in reports as a transparent modeling layer, not as experimental proof.

## 8.3 Vault Lens Metrics

File:

- `platform/backend/services/metrics_service.py`

### What is actually executed

The service runs these real steps locally:

1. initialize or reuse a demo user in `/tmp/cryptoarena_platform_vault.db`
2. Kyber encapsulation
3. AES-GCM encryption
4. signing payload construction
5. Dilithium signature
6. SQLite insert
7. signature verification precheck
8. Kyber decapsulation
9. AES-GCM decryption

That means Vault Lens is not showing static mock numbers. It is executing real cryptographic and database operations on the host machine.

### Step timing calculation

Every stage is individually wrapped with `time.perf_counter()`.

Reported as:

- `duration_ms` per step
- `total_ms` for end-to-end flow

### Size and overhead calculation

- `ciphertext_size = len(ciphertext) + len(tag)`
- `overhead_bytes = (ciphertext_size - len(plaintext)) + len(capsule) + len(signature)`
- `overhead_percent = overhead_bytes / plaintext_size * 100`

### Throughput calculation

- `throughput_mbps = ((plaintext_size / (1024 * 1024)) * 1000) / total_ms`

This is really MB/s, not megabits per second, even though the field name says `throughput_mbps`.

### Tamper detection window

The code uses:

- the duration of `signature_precheck`

Meaning:

- it is really "signature verification time in this run"
- it is a reasonable proxy for the time to reject manipulated signed content in the platform flow

### Quantum readiness score

This value is not measured from a formula.

Current logic:

- `94` for `Kyber-512`
- `97` for other branch values such as `Kyber-768`

Meaning:

- this is a presentational confidence score
- it is not derived from NIST levels or a formal evaluation function in the code

### Authenticity rating for Vault Lens

- step timing: high
- size metrics: high
- roundtrip check: high
- throughput: derived from real timings, high enough for local demo use
- quantum readiness score: heuristic
- signing choice label: partly authentic, with caveat described earlier

## 9. Benchmarks in the Repo

## 9.1 Simple Benchmark Script

File:

- `tests/benchmarks/bench_crypto.py`

What it measures:

- Kyber encapsulation
- Kyber decapsulation
- Dilithium sign on 1 KB payload
- Dilithium verify on 1 KB payload
- AES-256-GCM encryption on 1 MB payload
- full `store_file` flow on 1 MB payload
- full `retrieve_file` flow on 1 MB payload

Method:

- average of repeated timings using `time.perf_counter()`

Usefulness:

- quick local sanity benchmark
- not as rigorous as the multi-trial harness

## 9.2 Reproducible Benchmark Harness

Files:

- `core/benchmark_harness.py`
- `scripts/benchmark_harness.py`

Baselines:

- `rsa2048_aesgcm_ecdsa`
- `aes_only`
- `mlkem_mldsa_aesgcm`

Metrics captured per trial family:

- median latency
- p95 latency
- median throughput
- ciphertext overhead bytes
- capsule/signature overhead bytes
- peak memory bytes from `tracemalloc`
- CPU usage percent from `process_time / wall_time`
- tamper failure rate
- wrong-key failure rate

What makes it stronger than the simple script:

- deterministic payload generation from a seed
- multiple file sizes
- multiple trials per size
- baseline consistency through one-time key setup
- explicit security failure-rate checks

### How tamper and wrong-key rates are computed

For each trial:

- the harness attempts a tampered decrypt or tampered verify path
- the harness attempts a wrong-key path
- it records whether the system blocked the invalid action

The final report stores:

- `tamper_failure_rate = tamper_bypass_count / trials`
- `wrong_key_failure_rate = wrong_key_bypass_count / trials`

Interpretation:

- values near `0.0` are what you want
- they are security validation statistics, not performance metrics

## 10. How Real-Time Local Processing Works

This answers the "how are we implementing and processing them in real time on our local machine" part directly.

## 10.1 Backend Execution Model

The platform backend is a local FastAPI server started by:

- `scripts/run_project.py`
- normally through `make run-platform`

Routes:

- `/api/benchmark/run`
- `/api/attack/shors`
- `/api/attack/grovers`
- `/api/attack/lattice`
- `/api/attack/harvest-risk`
- `/api/vault/encrypt`

When the user clicks a control in React:

1. React hook sends an HTTP POST to `http://127.0.0.1:8000/api/...`
2. FastAPI parses the request with Pydantic models
3. The matching service function runs locally in Python
4. Real crypto or heuristic computation happens in the backend process
5. JSON response is returned to the frontend
6. React components render cards, charts, and logs

## 10.2 What Runs in Python vs What Runs in React

Runs in Python backend:

- cryptography
- liboqs operations
- benchmark loops
- risk-model formulas
- SQLite writes
- per-step timers

Runs in React frontend:

- user controls
- tab switching
- charts and bars
- terminal-style logs
- exporting JSON from Arena

The frontend does not compute the important cryptographic metrics itself. It renders backend output.

## 10.3 Why It Feels "Live"

It feels live for three reasons:

1. the backend is genuinely executing local operations
2. the frontend renders step-level results and charts immediately after response
3. a deliberate 2 to 5 second artificial delay is added before requests to create a visible simulation/loading experience

That last point should be disclosed in a project defense so reviewers do not confuse UI delay with actual algorithm runtime.

## 11. Security and Authenticity Backing

## 11.1 What the Tests Prove

Security tests cover:

- ciphertext tampering detection
- item-name tampering detection
- AES tag corruption fail-closed behavior
- signature substitution rejection
- wrong public key verification rejection
- cross-user access denial
- metadata nonce replay rejection

Integration tests cover:

- register
- login
- store
- retrieve
- delete
- password change

During my verification pass on June 2, 2026, the local test runs succeeded:

- `python3 -m pytest -q tests/security` -> 7 passed
- `python3 -m pytest -q tests/integration` -> 7 passed

Observed environment warning:

- `liboqs` native version `0.15.0`
- `liboqs-python` version `0.14.1`

The tests still passed, but the version mismatch should be treated as an environment caveat.

## 11.2 Practical Authenticity Summary

### Highly authentic / directly measured

- vault encryption and decryption flow
- signature verification gate
- database write timing in Vault Lens
- Arena operation-block latency
- overhead bytes based on actual output sizes
- benchmark harness memory and CPU measurements
- failure rates in the benchmark harness

### Derived from measured data

- throughput values
- speedup factor
- winner labels
- latency gap and p95 gap

### Heuristic or presentation-layer values

- quantum risk score
- quantum readiness score
- Attack Lab verdicts and forecasts
- harvest risk percentages
- security bands in lattice mode

## 12. Limitations and Important Caveats

1. The modern platform is partly experimental.
   `platform/backend/routers/auth.py` is only a scaffold and returns a demo token.

2. Attack Lab is explanatory, not empirical.
   It should not be presented as a measured quantum attack benchmark.

3. Signature mechanism selection is not perfectly strict.
   The UI can label a run as `Dilithium3` or `ML-DSA-65`, but helper functions resolve the first supported mechanism from `liboqs`.

4. `Kyber-768` in Vault Lens is a real execution path but uses ephemeral service-level keys for that run, not the persisted user key path used by the legacy vault.

5. `throughput_mbps` is named like megabits per second but is actually calculated as megabytes per second.

6. Frontend delay is partly simulated.
   The `waitRandomSimulationDelay()` helper adds 2 to 5 seconds before API calls.

7. Energy metrics are mentioned in some high-level UI/README language, but no dedicated backend energy model is currently implemented in the inspected services.

8. In-memory zeroization exists only in limited places.
   Shared secrets are zeroed in `vault_manager`, but Python object lifecycle still limits hard guarantees for full memory sanitization.

## 13. How to Describe This Project in a Final Report or Viva

Recommended wording:

"This project is a dual-stack post-quantum cryptographic platform. The legacy vault stack implements a real end-to-end secure storage pipeline using Argon2id, PBKDF2, Kyber KEM, Dilithium or ML-DSA signatures, AES-256-GCM, and SQLite. The modern platform adds three research labs: Algorithm Arena for measured crypto benchmarking, Attack Lab for transparent threat modeling, and Vault Lens for real step-by-step instrumentation of the secure vault pipeline. Measured metrics are separated from heuristic scores so that performance and risk claims remain defensible."

## 14. Bottom-Line Assessment

If the question is "how authentic are the metrics?" the honest answer is:

- the secure vault path is real
- Vault Lens timings are real
- Arena timings are real within a tightly scoped crypto-only measurement boundary
- Attack Lab is modeled, not experimentally measured
- readiness and risk scores are heuristic overlays

So the project is strongest when presented as:

- a real PQC vault implementation
- a real benchmark and instrumentation workspace
- plus a transparent research visualization layer for threat communication

It is weaker if presented as:

- a complete production platform
- a formal cryptanalysis framework
- a source of precise real-world quantum break forecasts
