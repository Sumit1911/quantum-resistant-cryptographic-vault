# instructions.md — Quantum-Resistant Cryptographic Vault
## Development Action Plan & Architecture Reference

---

## Purpose of This File

This document is the **single source of truth** for building the Quantum-Resistant Cryptographic Vault. It describes:

- What the software is and why it exists
- The full system architecture and how components relate
- Every module and component broken down line-by-line
- A concrete, ordered development action plan
- Testing strategy across unit, integration, and security levels
- All other engineering concerns: dependency management, CI/CD, documentation, and deployment

Anyone reading this file should be able to understand the entire project and begin contributing immediately.

---

## 1. What We Are Building

A **desktop/web application** that allows users to securely store and retrieve files and passwords using **post-quantum cryptography (PQC)** standards finalized by NIST in 2022.

Modern encryption (RSA, ECC) will be broken by sufficiently powerful quantum computers via Shor's Algorithm. Our vault replaces those algorithms with:

- **Kyber-512 (ML-KEM)** — for key encapsulation (replaces RSA key exchange)
- **Dilithium (ML-DSA)** — for digital signatures (replaces RSA/ECDSA signing)
- **AES-256-GCM** — for symmetric encryption of actual file content (already quantum-resistant with 256-bit keys)

The threat we are specifically defending against is **"Harvest Now, Decrypt Later"** — adversaries capturing encrypted data today and storing it until quantum hardware matures. Data stored in this vault remains confidential even in that scenario.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit GUI (frontend)               │
│         Login · Upload · Download · Manage vault          │
└────────────────────────┬────────────────────────────────-┘
                         │ calls
┌────────────────────────▼─────────────────────────────────┐
│                   Vault Core (Python)                     │
│   auth.py · crypto.py · storage.py · vault_manager.py    │
└────────────────────────┬─────────────────────────────────┘
                         │ uses
┌────────────────────────▼─────────────────────────────────┐
│              Cryptographic Layer                          │
│         liboqs-python  ·  cryptography (PyCA)            │
│      Kyber-512 (KEM)   ·  Dilithium (DSA)  · AES-GCM    │
└────────────────────────┬─────────────────────────────────┘
                         │ persists to
┌────────────────────────▼─────────────────────────────────┐
│                   SQLite3 Database                        │
│    users · vault_items · keys (all fields encrypted)     │
└──────────────────────────────────────────────────────────┘
```

**Design principles:**
- Application-level encryption: data is encrypted before it hits the disk
- Separation of concerns: signing keys and encryption keys are distinct key pairs
- Modular PQC layer: algorithms can be swapped as NIST standards evolve
- No plaintext secrets ever written to disk

---

## 3. Repository Structure

```
quantum-vault/
│
├── instructions.md          ← this file
├── README.md                ← project overview and quickstart
├── requirements.txt         ← Python dependencies
├── .env.example             ← environment variable template
│
├── app/
│   ├── main.py              ← Streamlit entry point
│   ├── pages/
│   │   ├── login.py         ← login and registration UI
│   │   ├── vault.py         ← file upload/download UI
│   │   └── settings.py      ← key management UI
│   └── components/
│       ├── file_card.py     ← reusable UI card for a vault item
│       └── status_bar.py    ← status/notification bar
│
├── core/
│   ├── auth.py              ← user authentication logic
│   ├── crypto.py            ← all cryptographic operations
│   ├── storage.py           ← database read/write operations
│   └── vault_manager.py     ← orchestrates auth + crypto + storage
│
├── db/
│   ├── schema.sql           ← SQLite3 schema definition
│   └── migrations/          ← schema version migration scripts
│
├── tests/
│   ├── unit/
│   │   ├── test_auth.py
│   │   ├── test_crypto.py
│   │   └── test_storage.py
│   ├── integration/
│   │   ├── test_store_retrieve.py
│   │   └── test_full_workflow.py
│   ├── security/
│   │   ├── test_tamper_detection.py
│   │   ├── test_wrong_key.py
│   │   └── test_signature_bypass.py
│   └── benchmarks/
│       └── bench_crypto.py
│
├── scripts/
│   ├── setup_db.py          ← initializes the SQLite3 database
│   ├── benchmark.py         ← runs and prints perf benchmarks
│   └── keygen.py            ← standalone key pair generation utility
│
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── threat_model.md
```

---

## 4. Database Schema

**File: `db/schema.sql`**

```sql
-- Stores registered users
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    -- Argon2/PBKDF2 hash of master password
    password_hash TEXT  NOT NULL,
    -- Kyber-512 public key (stored in plaintext — public by design)
    kyber_public_key    BLOB NOT NULL,
    -- Kyber-512 private key encrypted with derived key from password
    kyber_private_key   BLOB NOT NULL,
    -- Dilithium public key
    dilithium_public_key  BLOB NOT NULL,
    -- Dilithium private key encrypted with derived key from password
    dilithium_private_key BLOB NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stores each encrypted vault item (file or password)
CREATE TABLE vault_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    item_name   TEXT    NOT NULL,         -- filename or credential label
    item_type   TEXT    NOT NULL,         -- 'file' or 'password'
    -- AES-256-GCM encrypted content
    ciphertext  BLOB    NOT NULL,
    -- AES nonce/IV used during encryption
    aes_iv      BLOB    NOT NULL,
    -- GCM authentication tag
    aes_tag     BLOB    NOT NULL,
    -- Kyber-encapsulated session key
    kyber_capsule BLOB  NOT NULL,
    -- Dilithium signature over (ciphertext || kyber_capsule || metadata)
    dilithium_signature BLOB NOT NULL,
    -- Original file size in bytes (metadata)
    original_size INTEGER,
    -- MIME type if file
    mime_type   TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Component Breakdown — Line by Line

### 5.1 `core/auth.py` — Authentication

**Responsibility:** Handle user registration, login, and master-password-based key protection.

```python
# --- Imports ---
import os
import argon2          # pip install argon2-cffi
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Constants ---
ARGON2_TIME_COST = 3       # iterations
ARGON2_MEMORY_COST = 65536 # 64 MB
ARGON2_PARALLELISM = 2
KEY_DERIVATION_SALT_SIZE = 16  # bytes
PROTECTION_KEY_SIZE = 32       # 256-bit AES key for wrapping private keys

# --- Functions to implement ---

def hash_master_password(password: str) -> str:
    """
    Hash the master password using Argon2id.
    Returns a string suitable for storage in the users table.
    Never store the raw password.
    """

def verify_master_password(password: str, stored_hash: str) -> bool:
    """
    Verify a login attempt against the stored Argon2 hash.
    Returns True if password matches.
    """

def derive_protection_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES key from the master password using PBKDF2-HMAC-SHA256.
    This key is used to wrap (encrypt) the user's PQC private keys.
    Salt must be stored alongside the encrypted private keys.
    """

def wrap_private_key(private_key_bytes: bytes, protection_key: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt a PQC private key using AES-256-GCM with the protection key.
    Returns (iv, ciphertext+tag) to be stored in the database.
    """

def unwrap_private_key(ciphertext: bytes, iv: bytes, protection_key: bytes) -> bytes:
    """
    Decrypt a wrapped private key using AES-256-GCM.
    Called after successful login to load keys into memory.
    Raise ValueError on authentication failure (wrong password).
    """

def register_user(username: str, password: str, db_conn) -> bool:
    """
    Full registration flow:
    1. Hash master password with Argon2id
    2. Derive protection key from password
    3. Generate Kyber-512 key pair (via crypto.py)
    4. Generate Dilithium key pair (via crypto.py)
    5. Wrap both private keys with protection key
    6. Store everything in users table
    Returns True on success, raises on duplicate username.
    """

def login_user(username: str, password: str, db_conn) -> dict | None:
    """
    Full login flow:
    1. Fetch user row from database
    2. Verify password against stored Argon2 hash
    3. Derive protection key from password
    4. Unwrap Kyber private key
    5. Unwrap Dilithium private key
    6. Return session dict: {user_id, kyber_pk, kyber_sk, dil_pk, dil_sk}
    Returns None if authentication fails.
    """
```

---

### 5.2 `core/crypto.py` — Cryptographic Operations

**Responsibility:** All PQC and symmetric crypto operations. This module is the only place in the codebase that touches liboqs and PyCA directly.

```python
# --- Imports ---
import os
import oqs                    # liboqs-python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- Constants ---
KYBER_ALG = "Kyber512"
DILITHIUM_ALG = "Dilithium3"
AES_KEY_SIZE = 32    # 256 bits
AES_IV_SIZE  = 12    # 96-bit nonce for GCM

# --- Key Generation ---

def generate_kyber_keypair() -> tuple[bytes, bytes]:
    """
    Generate a Kyber-512 key pair.
    Returns (public_key, private_key) as raw bytes.
    """

def generate_dilithium_keypair() -> tuple[bytes, bytes]:
    """
    Generate a Dilithium key pair.
    Returns (public_key, private_key) as raw bytes.
    """

# --- Key Encapsulation (Kyber) ---

def kyber_encapsulate(kyber_public_key: bytes) -> tuple[bytes, bytes]:
    """
    Encapsulate a fresh 256-bit session key using the recipient's Kyber public key.
    Returns (capsule, shared_secret).
    - capsule: 768 bytes stored in the database
    - shared_secret: used directly as the AES-256 session key, never stored
    """

def kyber_decapsulate(capsule: bytes, kyber_private_key: bytes) -> bytes:
    """
    Recover the shared secret from a capsule using the Kyber private key.
    Returns the shared_secret (= AES session key).
    Raises on decapsulation failure.
    """

# --- Symmetric Encryption (AES-256-GCM) ---

def aes_encrypt(plaintext: bytes, session_key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt plaintext using AES-256-GCM.
    Returns (iv, ciphertext, tag).
    - iv: 12-byte random nonce, stored in the database
    - ciphertext: encrypted content
    - tag: 16-byte GCM authentication tag (appended to ciphertext by PyCA, split here for clarity)
    """

def aes_decrypt(ciphertext: bytes, iv: bytes, tag: bytes, session_key: bytes) -> bytes:
    """
    Decrypt AES-256-GCM ciphertext.
    Raises InvalidTag if ciphertext has been tampered with.
    Returns plaintext bytes.
    """

# --- Digital Signatures (Dilithium) ---

def dilithium_sign(payload: bytes, dilithium_private_key: bytes) -> bytes:
    """
    Sign an arbitrary payload using Dilithium.
    payload = ciphertext || kyber_capsule || item_name || user_id (concatenated bytes)
    Returns signature bytes to be stored in the database.
    """

def dilithium_verify(payload: bytes, signature: bytes, dilithium_public_key: bytes) -> bool:
    """
    Verify a Dilithium signature.
    Returns True if valid, False if tampered.
    Must be called BEFORE attempting decryption on retrieval.
    """

# --- High-level Helpers ---

def build_signing_payload(ciphertext: bytes, capsule: bytes, item_name: str, user_id: int) -> bytes:
    """
    Deterministically construct the byte payload that gets signed.
    Ensures signing and verification use identical inputs.
    """
```

---

### 5.3 `core/storage.py` — Database Operations

**Responsibility:** All SQLite3 read/write operations. No cryptography here — pure data access.

```python
# --- Imports ---
import sqlite3
from dataclasses import dataclass

# --- Data Classes ---

@dataclass
class VaultItem:
    id: int
    user_id: int
    item_name: str
    item_type: str        # 'file' or 'password'
    ciphertext: bytes
    aes_iv: bytes
    aes_tag: bytes
    kyber_capsule: bytes
    dilithium_signature: bytes
    original_size: int
    mime_type: str

# --- Connection ---

def get_connection(db_path: str = "vault.db") -> sqlite3.Connection:
    """
    Return a SQLite3 connection. Enables WAL mode for concurrent reads.
    """

def init_db(db_path: str = "vault.db"):
    """
    Run schema.sql against a fresh database.
    Called once during setup. Safe to call on existing DB (IF NOT EXISTS).
    """

# --- User Operations ---

def create_user(conn, username, password_hash, kyber_pk, kyber_sk_enc, kyber_sk_iv,
                dil_pk, dil_sk_enc, dil_sk_iv, kdf_salt) -> int:
    """Insert a new user row. Returns the new user_id."""

def get_user_by_username(conn, username: str) -> dict | None:
    """Fetch a user row by username. Returns None if not found."""

# --- Vault Item Operations ---

def store_vault_item(conn, user_id: int, item_name: str, item_type: str,
                     ciphertext: bytes, aes_iv: bytes, aes_tag: bytes,
                     kyber_capsule: bytes, dilithium_signature: bytes,
                     original_size: int, mime_type: str) -> int:
    """Insert an encrypted vault item. Returns new item_id."""

def list_vault_items(conn, user_id: int) -> list[VaultItem]:
    """List all vault items for a user (metadata only, no ciphertext for listing)."""

def get_vault_item(conn, item_id: int, user_id: int) -> VaultItem | None:
    """Fetch a specific vault item including ciphertext. Returns None if not found or wrong user."""

def delete_vault_item(conn, item_id: int, user_id: int) -> bool:
    """Delete a vault item. Returns True if deleted, False if not found."""
```

---

### 5.4 `core/vault_manager.py` — Orchestrator

**Responsibility:** Ties auth, crypto, and storage together into high-level user-facing operations. This is what the GUI calls.

```python
# --- Imports ---
from core import auth, crypto, storage

# --- Functions ---

def register(username: str, password: str, db_conn) -> bool:
    """
    Register a new user:
    1. crypto.generate_kyber_keypair()
    2. crypto.generate_dilithium_keypair()
    3. auth.hash_master_password()
    4. auth.derive_protection_key()
    5. auth.wrap_private_key() for both key pairs
    6. storage.create_user()
    """

def login(username: str, password: str, db_conn) -> dict | None:
    """
    Login and return a session object:
    {user_id, kyber_pk, kyber_sk, dilithium_pk, dilithium_sk, db_conn}
    Returns None on failure.
    """

def store_file(session: dict, file_name: str, file_bytes: bytes, mime_type: str) -> int:
    """
    Full encrypt-and-store flow:
    1. crypto.kyber_encapsulate(session['kyber_pk']) → (capsule, session_key)
    2. crypto.aes_encrypt(file_bytes, session_key) → (iv, ciphertext, tag)
    3. Zero session_key from memory immediately after step 2
    4. crypto.build_signing_payload(ciphertext, capsule, file_name, user_id)
    5. crypto.dilithium_sign(payload, session['dilithium_sk'])
    6. storage.store_vault_item(...)
    Returns item_id.
    """

def retrieve_file(session: dict, item_id: int) -> bytes:
    """
    Full verify-and-decrypt flow:
    1. storage.get_vault_item(item_id, user_id)
    2. crypto.build_signing_payload(...)
    3. crypto.dilithium_verify(...) — ABORT if False, raise IntegrityError
    4. crypto.kyber_decapsulate(capsule, session['kyber_sk']) → session_key
    5. crypto.aes_decrypt(ciphertext, iv, tag, session_key) → plaintext
    6. Zero session_key from memory
    Returns plaintext bytes.
    """

def delete_file(session: dict, item_id: int) -> bool:
    """
    Delete a vault item. Verify ownership via user_id before deletion.
    """

def list_files(session: dict) -> list:
    """
    Return a list of VaultItem metadata objects for the authenticated user.
    Does NOT return ciphertext — only names, types, sizes, dates.
    """
```

---

### 5.5 `app/main.py` — Streamlit Entry Point

**Responsibility:** Application startup, session state initialization, page routing.

```python
# Streamlit session_state keys:
#   st.session_state['authenticated']  → bool
#   st.session_state['session']        → dict from vault_manager.login()
#   st.session_state['db_conn']        → sqlite3 connection

# Startup sequence:
# 1. storage.init_db() on first run
# 2. Check session_state['authenticated']
# 3. If not authenticated → render login.py page
# 4. If authenticated → render sidebar + vault.py page
```

---

