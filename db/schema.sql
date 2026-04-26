-- Stores registered users
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password_hash TEXT  NOT NULL,
    kyber_public_key    BLOB NOT NULL,
    kyber_private_key   BLOB NOT NULL,
    dilithium_public_key  BLOB NOT NULL,
    dilithium_private_key BLOB NOT NULL,
    kdf_salt    BLOB NOT NULL,
    kyber_private_key_iv BLOB NOT NULL,
    dilithium_private_key_iv BLOB NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stores each encrypted vault item (file or password)
CREATE TABLE IF NOT EXISTS vault_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    item_name   TEXT    NOT NULL,
    item_type   TEXT    NOT NULL,
    metadata_nonce BLOB NOT NULL,
    ciphertext  BLOB    NOT NULL,
    aes_iv      BLOB    NOT NULL,
    aes_tag     BLOB    NOT NULL,
    kyber_capsule BLOB  NOT NULL,
    dilithium_signature BLOB NOT NULL,
    original_size INTEGER,
    mime_type   TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
