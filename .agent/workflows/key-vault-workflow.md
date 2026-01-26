---
description: Encrypt/decrypt API keys using machine-bound key vault
---

# Key Vault Workflow

Use `tools/key_vault.py` to encrypt sensitive fields in `api-keys.json` files.

## Prerequisites

```bash
# Verify cryptography library is installed
pip show cryptography

# If not installed:
pip install cryptography
```

## Commands Reference

```bash
# Show machine identifier (for debugging)
python tools/key_vault.py machine-id

# Check encryption status of a file
python tools/key_vault.py status api-keys.local.json

# Encrypt all sensitive fields (requires KEYVAULT_PASSPHRASE)
set KEYVAULT_PASSPHRASE=user-passphrase
python tools/key_vault.py encrypt api-keys.local.json

# Get a single decrypted value
python tools/key_vault.py get google_search.api_key

# Decrypt entire file to stdout (use carefully!)
python tools/key_vault.py decrypt api-keys.local.json --stdout
```

## Workflow: Setting Up Encrypted Keys

// turbo-all

1. **Check if local keys file exists**
   ```bash
   dir api-keys.local.json
   ```
   If not, copy from sample: `copy api-keys.sample.json api-keys.local.json`

2. **Check current encryption status**
   ```bash
   python tools/key_vault.py status api-keys.local.json
   ```
   - 🔒 = encrypted
   - ⚪ = placeholder (YOUR_...)
   - ⚠️ = plaintext (needs encryption!)

3. **Set passphrase and encrypt** (if plaintext values exist)
   ```powershell
   $env:KEYVAULT_PASSPHRASE="<ask user for passphrase>"
   python tools/key_vault.py encrypt api-keys.local.json
   ```

4. **Verify encryption succeeded**
   ```bash
   python tools/key_vault.py status api-keys.local.json
   ```

## Workflow: Reading Encrypted Keys in Scripts

For scripts that need API keys, use the `get_api_key` helper:

```python
from tools.key_vault import get_api_key

# Returns decrypted value (requires KEYVAULT_PASSPHRASE env var)
api_key = get_api_key("google_search")  # Gets api_key field
cse_id = get_api_key("google_search", "cse_id")  # Gets specific field
```

Or use CLI for one-off retrieval:
```bash
python tools/key_vault.py get brave_search.api_key
```

## Auto-Detected Sensitive Fields

These field names are automatically encrypted:
- `api_key`, `client_secret`, `cse_id`
- `application_id`, `tenant_id`, `target_mailbox`
- `secret`, `password`, `token`

## Security Notes

- **Machine-bound**: Encrypted files only decrypt on the same machine
- **Passphrase required**: Must set `KEYVAULT_PASSPHRASE` environment variable
- **No plaintext storage**: Passphrase is never written to disk
- **Placeholder skip**: Values starting with `YOUR_` are not encrypted

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `KEYVAULT_PASSPHRASE not set` | Run `$env:KEYVAULT_PASSPHRASE="..."` |
| `Decryption failed - wrong passphrase` | Check passphrase matches what was used to encrypt |
| `Decryption failed - different machine` | File was encrypted on a different computer |
