-- Add replay-resistant metadata nonce to vault items.
ALTER TABLE vault_items ADD COLUMN metadata_nonce BLOB;

-- Backfill existing rows with deterministic non-null placeholder for compatibility.
UPDATE vault_items
SET metadata_nonce = x'00000000000000000000000000000000'
WHERE metadata_nonce IS NULL;
