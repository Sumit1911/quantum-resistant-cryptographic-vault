# Threat Model

## Assets

- User master passwords.
- PQC private keys (Kyber and Dilithium).
- Stored vault payloads (files/metadata).

## In-Scope Adversaries

- Offline attacker with DB access attempting decryption.
- Attacker modifying ciphertext or metadata in the database.
- Unauthorized user attempting cross-account item retrieval.
- Future quantum adversary targeting classical public-key schemes.

## Security Controls

- Argon2id password hashing for authentication.
- PBKDF2-derived protection keys for private-key wrapping.
- AES-256-GCM for confidentiality + integrity of payloads.
- Dilithium signatures over deterministic payloads to detect tampering.
- Ownership checks on item retrieval and deletion.

## Assumptions

- Runtime host is trusted while application process is active.
- `liboqs` implementation is correctly built and linked.
- Master password strength is user-dependent.

## Known Limitations

- In-memory key material lifecycle is partially hardened but not fully zeroized across all objects.
- Side-channel resistance and secure enclave integration are out of scope.
- Backups and operational key-rotation policies are not automated.

## Verification Coverage

- Unit tests validate cryptographic and storage behavior.
- Integration tests validate end-to-end flows.
- Security tests validate tamper detection, signature bypass resistance, and ownership controls.
