## 6. Development Action Plan

Development is broken into five phases. Each phase must pass its own tests before moving to the next.

---

### Phase 0 — Environment Setup (Day 1)

| Task | Details |
|------|---------|
| Create virtualenv | `python -m venv venv && source venv/bin/activate` |
| Install liboqs | Build from source or use `pip install liboqs-python` |
| Install dependencies | `pip install streamlit cryptography argon2-cffi pytest` |
| Verify liboqs | Run `python -c "import oqs; print(oqs.get_enabled_kem_mechanisms())"` — must include Kyber512 |
| Initialize database | Run `scripts/setup_db.py` |
| Create `.env` file | Copy from `.env.example`, set `DB_PATH`, `SECRET_SALT` |

**Exit criterion:** `import oqs` succeeds and `Kyber512` appears in enabled mechanisms.

---

### Phase 1 — Cryptographic Layer (Days 2–4)

Build and test `core/crypto.py` in complete isolation. No GUI, no database.

**Step 1.1 — Key generation**
- Implement `generate_kyber_keypair()`
- Implement `generate_dilithium_keypair()`
- Write `tests/unit/test_crypto.py::test_keypair_generation`
- Assert key lengths match spec (Kyber-512 public: 800 bytes, private: 1632 bytes)

**Step 1.2 — Kyber KEM round-trip**
- Implement `kyber_encapsulate()` and `kyber_decapsulate()`
- Test: encapsulate with public key → decapsulate with private key → shared secrets must match
- Test: decapsulate with wrong private key → shared secrets must NOT match

**Step 1.3 — AES-256-GCM encryption**
- Implement `aes_encrypt()` and `aes_decrypt()`
- Test: encrypt plaintext → decrypt → assert equality
- Test: flip one bit in ciphertext → `aes_decrypt` must raise `InvalidTag`
- Test: flip one bit in IV → `aes_decrypt` must raise `InvalidTag`

**Step 1.4 — Dilithium signatures**
- Implement `dilithium_sign()` and `dilithium_verify()`
- Test: sign payload → verify → must return True
- Test: sign payload → modify payload by one byte → verify → must return False
- Test: sign payload → verify with wrong public key → must return False

**Step 1.5 — Signing payload builder**
- Implement `build_signing_payload()`
- Test: same inputs always produce identical bytes (deterministic)

**Exit criterion:** All `tests/unit/test_crypto.py` tests pass with 100% coverage of crypto.py.

---

### Phase 2 — Authentication Layer (Days 5–6)

Build and test `core/auth.py`.

**Step 2.1 — Password hashing**
- Implement `hash_master_password()` using Argon2id
- Implement `verify_master_password()`
- Test: hash → verify with correct password → True
- Test: hash → verify with wrong password → False
- Test: two hashes of same password produce different strings (salt randomness)

**Step 2.2 — Key protection**
- Implement `derive_protection_key()`
- Implement `wrap_private_key()` and `unwrap_private_key()`
- Test: wrap → unwrap → bytes identical to original
- Test: unwrap with wrong protection key → raise `InvalidTag`

**Step 2.3 — Registration and login flows**
- Implement `register_user()` and `login_user()` against an in-memory SQLite DB
- Test: register → login → session keys match the generated key pairs
- Test: login with wrong password → returns None
- Test: register duplicate username → raises IntegrityError

**Exit criterion:** All `tests/unit/test_auth.py` tests pass.

---

### Phase 3 — Storage Layer (Day 7)

Build and test `core/storage.py`.

**Step 3.1 — Schema init**
- Implement `init_db()` — apply schema.sql
- Test: run twice → no error (idempotent)

**Step 3.2 — User CRUD**
- Implement `create_user()` and `get_user_by_username()`
- Test: create → retrieve → all fields match
- Test: retrieve non-existent username → None

**Step 3.3 — Vault item CRUD**
- Implement `store_vault_item()`, `get_vault_item()`, `list_vault_items()`, `delete_vault_item()`
- Test: store → list → item appears in list
- Test: store → get by id → all blobs match exactly
- Test: get by id with wrong user_id → None (ownership check)
- Test: delete → get → None

**Exit criterion:** All `tests/unit/test_storage.py` tests pass.

---

### Phase 4 — Orchestration & Integration (Days 8–10)

Build `core/vault_manager.py` and run integration tests.

**Step 4.1 — store_file / retrieve_file round-trip**
- Test: register user → login → store a 1 KB file → retrieve → bytes match original
- Test: store a 10 MB file → retrieve → bytes match (performance must be < 5 seconds)

**Step 4.2 — Signature verification gate**
- Test: store file → manually flip one byte in ciphertext column → retrieve → must raise IntegrityError BEFORE decryption
- This is the critical security test — the vault must not attempt decryption on tampered data

**Step 4.3 — Wrong key rejection**
- Test: register two users → user A stores file → user B attempts to retrieve it by item_id → returns None (ownership check in storage layer catches this)

**Step 4.4 — Delete**
- Test: store → delete → retrieve → returns None

**Exit criterion:** All `tests/integration/` tests pass.

---

### Phase 5 — GUI (Days 11–14)

Build the Streamlit interface, wired to vault_manager.py.

**Step 5.1 — Login page (`app/pages/login.py`)**
- Two tabs: Login / Register
- Calls `vault_manager.login()` → stores session in `st.session_state`
- Show error on wrong credentials without revealing which field is wrong

**Step 5.2 — Vault page (`app/pages/vault.py`)**
- List all vault items as cards (file_card.py component)
- File uploader widget → calls `vault_manager.store_file()`
- Download button per item → calls `vault_manager.retrieve_file()` → `st.download_button()`
- Delete button per item with confirmation dialog

**Step 5.3 — Settings page (`app/pages/settings.py`)**
- Display public key fingerprints (SHA-256 of public keys, hex-encoded)
- Change master password flow (re-wraps private keys with new protection key)

**Step 5.4 — Error handling**
- Display user-friendly error on IntegrityError (tampered file detected)
- Display user-friendly error on wrong password
- Never show raw exception tracebacks in the UI

**Exit criterion:** Manual end-to-end walkthrough: register → login → upload file → logout → login → download file → bytes match → logout.

---

## 7. Testing Strategy

### 7.1 Unit Tests

Location: `tests/unit/`

| Test file | What it covers |
|-----------|---------------|
| `test_crypto.py` | Key generation, KEM round-trip, AES round-trip, signature sign/verify, payload builder |
| `test_auth.py` | Password hashing, key wrapping, register/login flows |
| `test_storage.py` | CRUD for users and vault items, ownership checks |

Run with: `pytest tests/unit/ -v`

### 7.2 Integration Tests

Location: `tests/integration/`

| Test file | What it covers |
|-----------|---------------|
| `test_store_retrieve.py` | Full store → retrieve round-trip for files and passwords |
| `test_full_workflow.py` | Register → login → store → logout → login → retrieve → delete |

Run with: `pytest tests/integration/ -v`

### 7.3 Security Tests

Location: `tests/security/`

These tests verify that the vault CORRECTLY FAILS when under attack.

| Test file | Scenario | Expected behaviour |
|-----------|----------|--------------------|
| `test_tamper_detection.py` | Flip one byte in ciphertext in DB | `IntegrityError` raised before decryption |
| `test_tamper_detection.py` | Modify item_name in DB | `IntegrityError` (name is part of signing payload) |
| `test_wrong_key.py` | User B tries to retrieve User A's file | `None` returned (ownership gate) |
| `test_signature_bypass.py` | Replace signature with valid sig from another item | `IntegrityError` (payload mismatch) |
| `test_signature_bypass.py` | Verify with wrong Dilithium public key | `False` returned |

Run with: `pytest tests/security/ -v`

All security tests must **pass** (i.e., the attack must be **blocked**).

### 7.4 Performance Benchmarks

Location: `tests/benchmarks/bench_crypto.py`

| Benchmark | Target |
|-----------|--------|
| Kyber-512 encapsulation | < 1 ms |
| Kyber-512 decapsulation | < 1 ms |
| Dilithium sign (1 KB payload) | < 5 ms |
| Dilithium verify (1 KB payload) | < 5 ms |
| AES-256-GCM encrypt 1 MB | > 100 MB/s |
| Full store_file (1 MB file) | < 200 ms |
| Full retrieve_file (1 MB file) | < 200 ms |

Run with: `python tests/benchmarks/bench_crypto.py`

### 7.5 Code Coverage

Target: **90% coverage** across `core/` modules.

Run with: `pytest --cov=core --cov-report=term-missing tests/`

---

## 8. Dependency Management

**`requirements.txt`:**
```
streamlit>=1.32.0
liboqs-python>=0.9.0
cryptography>=42.0.0
argon2-cffi>=23.1.0
pytest>=8.0.0
pytest-cov>=5.0.0
python-dotenv>=1.0.0
```

**liboqs build note:** `liboqs-python` requires the native `liboqs` C library to be compiled and installed first. On Ubuntu/Debian:
```bash
sudo apt install cmake ninja-build libssl-dev
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja .. -DBUILD_SHARED_LIBS=ON
ninja && sudo ninja install
pip install liboqs-python
```

---

## 9. Security Hardening Checklist

Before any release, verify each item:

- [ ] Private keys are zeroed from memory after use (use `ctypes.memset` or `bytearray` and overwrite)
- [ ] Session dict is cleared from `st.session_state` on logout
- [ ] No secrets appear in log output or exception messages
- [ ] The signing payload is built identically on store and retrieve (test with `test_payload_determinism`)
- [ ] AES IV is freshly generated per-file (never reused)
- [ ] Database file permissions are `600` (owner read/write only)
- [ ] No raw SQL string concatenation — use parameterized queries everywhere in storage.py
- [ ] Streamlit is not exposed on a public IP without HTTPS

---

## 10. CI/CD Pipeline (GitHub Actions)

**`.github/workflows/test.yml`:**

```yaml
name: Test suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install liboqs native library
        run: |
          sudo apt install cmake ninja-build libssl-dev -y
          git clone https://github.com/open-quantum-safe/liboqs.git
          cd liboqs && mkdir build && cd build
          cmake -GNinja .. -DBUILD_SHARED_LIBS=ON
          ninja && sudo ninja install
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Python dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Run security tests
        run: pytest tests/security/ -v
      - name: Coverage report
        run: pytest --cov=core --cov-report=term-missing tests/
```

---

## 11. Documentation Plan

| Document | Location | Content |
|----------|----------|---------|
| README.md | root | Project overview, installation steps, 5-minute quickstart |
| instructions.md | root | This file — full dev plan |
| docs/architecture.md | docs/ | Detailed architecture diagrams, data flow |
| docs/api_reference.md | docs/ | Function signatures and docstrings for core/ |
| docs/threat_model.md | docs/ | What attacks the vault defends against and what it does not |

Docstrings follow Google style. Every public function in `core/` must have a docstring with Args, Returns, and Raises sections.

---

## 12. Future Scope (Post-MVP)

These are not part of the initial build but are planned extensions:

| Feature | Description |
|---------|-------------|
| Key rotation | Re-encapsulate all Kyber capsules under a new key pair without re-encrypting file content |
| Hybrid mode | Run Kyber alongside X25519 for transitional deployments where both classical and PQC clients exist |
| Cloud backend | Replace SQLite3 with an encrypted S3/Azure Blob backend for multi-device access |
| Hardware acceleration | FPGA/ASIC offload for Kyber and Dilithium lattice operations |
| Audit log | Tamper-evident log of all store/retrieve/delete actions per user |
| SPHINCS+ signing | Optional stateless hash-based signature as a second signing layer |
| CLI interface | `vault-cli` command alongside the Streamlit GUI for scripting and automation |

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| PQC | Post-Quantum Cryptography — algorithms believed secure against quantum computers |
| KEM | Key Encapsulation Mechanism — a way to establish a shared secret using a public key |
| ML-KEM | Module Lattice KEM — the NIST standardized name for Kyber |
| ML-DSA | Module Lattice DSA — the NIST standardized name for Dilithium |
| AES-GCM | Advanced Encryption Standard in Galois/Counter Mode — provides confidentiality + integrity |
| Session key | A short-lived symmetric key generated per-file, used for AES encryption |
| Capsule | The 768-byte output of Kyber encapsulation; contains the session key encrypted for the recipient |
| Protection key | AES key derived from the user's master password; used to wrap PQC private keys at rest |
| PBKDF2 | Password-Based Key Derivation Function 2 — stretches a password into a strong key |
| Argon2id | Memory-hard password hashing algorithm; resistant to GPU brute-force |
| Signing payload | The byte string that gets signed by Dilithium: ciphertext ∥ capsule ∥ metadata |
| Harvest now, decrypt later | Attack strategy of storing encrypted data now to decrypt once quantum hardware exists |

---

