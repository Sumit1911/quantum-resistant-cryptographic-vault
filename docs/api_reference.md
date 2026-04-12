# API Reference (Module-Level)

This project currently exposes module APIs (Python functions) rather than a formal HTTP API in the root Streamlit implementation.

## `core.auth`

- `hash_master_password(password: str) -> str`
- `verify_master_password(password: str, stored_hash: str) -> bool`
- `derive_protection_key(password: str, salt: bytes) -> bytes`
- `wrap_private_key(private_key_bytes: bytes, protection_key: bytes) -> tuple[bytes, bytes]`
- `unwrap_private_key(ciphertext: bytes, iv: bytes, protection_key: bytes) -> bytes`
- `register_user(username: str, password: str, db_conn) -> bool`
- `login_user(username: str, password: str, db_conn) -> dict | None`

## `core.crypto`

- `generate_kyber_keypair() -> tuple[bytes, bytes]`
- `generate_dilithium_keypair() -> tuple[bytes, bytes]`
- `kyber_encapsulate(kyber_public_key: bytes) -> tuple[bytes, bytes]`
- `kyber_decapsulate(capsule: bytes, kyber_private_key: bytes) -> bytes`
- `aes_encrypt(plaintext: bytes, session_key: bytes) -> tuple[bytes, bytes, bytes]`
- `aes_decrypt(ciphertext: bytes, iv: bytes, tag: bytes, session_key: bytes) -> bytes`
- `dilithium_sign(payload: bytes, dilithium_private_key: bytes) -> bytes`
- `dilithium_verify(payload: bytes, signature: bytes, dilithium_public_key: bytes) -> bool`
- `build_signing_payload(ciphertext: bytes, capsule: bytes, item_name: str, user_id: int) -> bytes`

## `core.storage`

- `get_connection(db_path: str = "vault.db") -> sqlite3.Connection`
- `init_db(db_path: str = "vault.db") -> None`
- `create_user(...) -> int`
- `get_user_by_username(conn, username: str) -> dict | None`
- `store_vault_item(...) -> int`
- `list_vault_items(conn, user_id: int) -> list[VaultItem]`
- `get_vault_item(conn, item_id: int, user_id: int) -> VaultItem | None`
- `delete_vault_item(conn, item_id: int, user_id: int) -> bool`

## `core.vault_manager`

- `register(username: str, password: str, db_conn) -> bool`
- `login(username: str, password: str, db_conn) -> dict | None`
- `store_file(session: dict, file_name: str, file_bytes: bytes, mime_type: str) -> int`
- `retrieve_file(session: dict, item_id: int) -> bytes | None`
- `delete_file(session: dict, item_id: int) -> bool`
- `list_files(session: dict) -> list`
- `change_master_password(session: dict, old_password: str, new_password: str) -> bool`

## Scripts

- `python3 scripts/setup_db.py` initializes DB schema.
- `python3 scripts/benchmark.py` runs performance benchmark output.
- `python3 scripts/keygen.py` generates and prints keypair details.
