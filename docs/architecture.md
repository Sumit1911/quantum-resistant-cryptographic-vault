# Quantum Vault Architecture

## System Overview

The project is a Streamlit-first application with a modular Python core:

- `app/`: user interface pages and components.
- `core/`: cryptography, authentication, storage, and orchestration.
- `db/`: SQLite schema and migration scripts.
- `tests/`: unit, integration, security, and benchmark validations.

## Execution Flow

1. User logs in or registers from `app/pages/login.py`.
2. `core/vault_manager.py` orchestrates auth + crypto + storage calls.
3. Data is encrypted and signed before database persistence.
4. On retrieval, signatures are verified before decryption.
5. Streamlit pages render status and user actions.

## Cryptographic Building Blocks

- Kyber-512 (`core/crypto.py`) for KEM/session key exchange.
- Dilithium/ML-DSA (`core/crypto.py`) for signatures and tamper detection.
- AES-256-GCM (`core/crypto.py`) for payload encryption/authentication.
- Argon2id + PBKDF2 (`core/auth.py`) for password and key wrapping flows.

## Storage Model

- `users` table stores identity, password hash, and wrapped private keys.
- `vault_items` table stores encrypted data, metadata, capsule, and signature.
- Ownership checks and metadata-only listing are handled in `core/storage.py`.

## Security Properties

- No plaintext vault payloads are stored in the database.
- Signature verification happens before decryption attempts.
- Wrong-user access is denied by ownership-gated queries.
- Security tests explicitly cover tamper and signature-bypass scenarios.
