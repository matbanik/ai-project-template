#!/usr/bin/env python3
"""
Key Vault - API Keys Encryption/Decryption Tool
================================================

Cross-platform encryption for sensitive fields in api-keys.json using
machine-specific salt + passphrase derivation.

## Quick Reference

    # Encrypt all sensitive fields in a file
    python key_vault.py encrypt api-keys.local.json

    # Get a decrypted value (for scripts to call)
    python key_vault.py get google_search.api_key

    # Show encryption status
    python key_vault.py status api-keys.local.json

    # Decrypt entire file to stdout (use carefully!)
    python key_vault.py decrypt api-keys.local.json --stdout

## Environment Variables

    KEYVAULT_PASSPHRASE  - Master passphrase (required for encrypt/decrypt)

## Security Notes

    - Uses Fernet (AES-128-CBC + HMAC-SHA256)
    - PBKDF2 with 480,000 iterations (OWASP 2023)
    - Machine-bound: encrypted files only decrypt on same machine
    - Passphrase never stored on disk

Requirements:
    pip install cryptography
"""

import argparse
import base64
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Lazy import cryptography to provide helpful error message
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Prefix for encrypted values in JSON
ENCRYPTED_PREFIX = "ENC:"

# Fields that should be encrypted by default
SENSITIVE_FIELDS = {
    "api_key",
    "client_secret",
    "cse_id",
    "application_id",
    "tenant_id",
    "target_mailbox",
    "secret",
    "password",
    "token",
}

# PBKDF2 iterations (OWASP 2023 recommendation for SHA-256)
PBKDF2_ITERATIONS = 480_000


def get_machine_id() -> str:
    """
    Generate a machine-specific identifier.

    Cross-platform approach:
    - Windows: MachineGuid from registry
    - Linux: /etc/machine-id or /var/lib/dbus/machine-id
    - macOS: IOPlatformUUID via ioreg
    - Fallback: MAC address via uuid.getnode()

    Returns:
        Stable machine identifier string
    """
    system = platform.system()

    try:
        if system == "Windows":
            # Read MachineGuid from Windows registry
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            )
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return machine_guid

        elif system == "Linux":
            # Try /etc/machine-id first (systemd)
            for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        return f.read().strip()

        elif system == "Darwin":  # macOS
            # Get IOPlatformUUID
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split("\n"):
                if "IOPlatformUUID" in line:
                    # Extract UUID from line like: "IOPlatformUUID" = "XXXXXXXX-..."
                    uuid = line.split("=")[1].strip().strip('"')
                    return uuid
    except Exception as e:
        print(f"[WARN] Could not get machine ID via primary method: {e}")

    # Fallback: use MAC address
    import uuid
    mac = uuid.getnode()
    # Check if it's a real MAC (not random)
    if (mac >> 40) % 2:
        print("[WARN] Using random MAC fallback - encryption may not be portable")
    return f"mac-{mac:012x}"


def derive_key(passphrase: str, machine_id: Optional[str] = None) -> bytes:
    """
    Derive a Fernet-compatible key using PBKDF2HMAC.

    Combines passphrase with machine ID to create machine-bound encryption.

    Args:
        passphrase: User-provided secret passphrase
        machine_id: Machine identifier (auto-detected if None)

    Returns:
        Base64-encoded 32-byte key suitable for Fernet
    """
    if not CRYPTO_AVAILABLE:
        print("[ERROR] cryptography library required: pip install cryptography")
        sys.exit(1)

    if machine_id is None:
        machine_id = get_machine_id()

    # Use machine_id as salt (ensures same passphrase = different key per machine)
    salt = machine_id.encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )

    key = kdf.derive(passphrase.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def encrypt_value(plaintext: str, key: bytes) -> str:
    """
    Encrypt a value using Fernet.

    Args:
        plaintext: Value to encrypt
        key: Fernet key (from derive_key)

    Returns:
        Encrypted value with ENC: prefix
    """
    if not CRYPTO_AVAILABLE:
        print("[ERROR] cryptography library required: pip install cryptography")
        sys.exit(1)

    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode("utf-8"))
    return f"{ENCRYPTED_PREFIX}{encrypted.decode('utf-8')}"


def decrypt_value(ciphertext: str, key: bytes) -> str:
    """
    Decrypt a value that has ENC: prefix.

    Args:
        ciphertext: Encrypted value (with or without ENC: prefix)
        key: Fernet key (from derive_key)

    Returns:
        Decrypted plaintext

    Raises:
        InvalidToken: If key is wrong or data corrupted
    """
    if not CRYPTO_AVAILABLE:
        print("[ERROR] cryptography library required: pip install cryptography")
        sys.exit(1)

    # Remove prefix if present
    if ciphertext.startswith(ENCRYPTED_PREFIX):
        ciphertext = ciphertext[len(ENCRYPTED_PREFIX):]

    f = Fernet(key)
    return f.decrypt(ciphertext.encode("utf-8")).decode("utf-8")


def is_encrypted(value: Any) -> bool:
    """Check if a value is encrypted (has ENC: prefix)."""
    return isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX)


def is_sensitive_field(field_name: str) -> bool:
    """Check if a field name indicates sensitive data."""
    field_lower = field_name.lower()
    return field_lower in SENSITIVE_FIELDS or any(
        s in field_lower for s in ["key", "secret", "password", "token"]
    )


def _process_dict(
    data: Dict,
    key: bytes,
    encrypt: bool,
    path: str = ""
) -> Tuple[Dict, int]:
    """
    Recursively process a dictionary, encrypting/decrypting sensitive fields.

    Args:
        data: Dictionary to process
        key: Fernet key
        encrypt: True to encrypt, False to decrypt
        path: Current path for logging

    Returns:
        Tuple of (processed dict, count of changes)
    """
    result = {}
    changes = 0

    for field, value in data.items():
        current_path = f"{path}.{field}" if path else field

        # Skip metadata fields
        if field.startswith("_"):
            result[field] = value
            continue

        if isinstance(value, dict):
            # Recurse into nested objects
            processed, sub_changes = _process_dict(value, key, encrypt, current_path)
            result[field] = processed
            changes += sub_changes

        elif isinstance(value, str):
            if encrypt:
                # Encrypt if: not already encrypted AND is sensitive field
                if not is_encrypted(value) and is_sensitive_field(field):
                    # Skip placeholder values
                    if value.startswith("YOUR_") or value == "":
                        result[field] = value
                    else:
                        result[field] = encrypt_value(value, key)
                        changes += 1
                        print(f"  [ENC] {current_path}")
                else:
                    result[field] = value
            else:
                # Decrypt if encrypted
                if is_encrypted(value):
                    try:
                        result[field] = decrypt_value(value, key)
                        changes += 1
                        print(f"  [DEC] {current_path}")
                    except InvalidToken:
                        print(f"  [ERR] {current_path} - decryption failed (wrong key?)")
                        result[field] = value
                else:
                    result[field] = value
        else:
            result[field] = value

    return result, changes


def get_passphrase() -> str:
    """Get passphrase from environment variable."""
    passphrase = os.environ.get("KEYVAULT_PASSPHRASE", "")
    if not passphrase:
        print("[ERROR] KEYVAULT_PASSPHRASE environment variable not set")
        print("        Set it with: set KEYVAULT_PASSPHRASE=your-secret-passphrase")
        sys.exit(1)
    return passphrase


def find_keys_file(filename: Optional[str] = None) -> Path:
    """
    Find the API keys file.

    Priority:
    1. Explicit filename argument
    2. api-keys.local.json in project root
    3. api-keys.json in project root
    """
    project_root = Path(__file__).parent.parent

    if filename:
        path = Path(filename)
        if not path.is_absolute():
            path = project_root / filename
        if path.exists():
            return path
        raise FileNotFoundError(f"File not found: {path}")

    # Auto-detect
    local_path = project_root / "api-keys.local.json"
    if local_path.exists():
        return local_path

    standard_path = project_root / "api-keys.json"
    if standard_path.exists():
        return standard_path

    raise FileNotFoundError(
        "No api-keys file found. Create api-keys.local.json from api-keys.sample.json"
    )


def encrypt_file(filepath: Path, output_path: Optional[Path] = None) -> int:
    """
    Encrypt sensitive fields in a JSON file.

    Args:
        filepath: Path to input JSON file
        output_path: Path for output (defaults to overwriting input)

    Returns:
        Number of fields encrypted
    """
    passphrase = get_passphrase()
    key = derive_key(passphrase)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[INFO] Encrypting: {filepath}")
    print(f"[INFO] Machine ID: {get_machine_id()[:8]}...")

    processed, changes = _process_dict(data, key, encrypt=True)

    out_path = output_path or filepath
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[OK] Encrypted {changes} field(s) -> {out_path}")
    return changes


def decrypt_file(filepath: Path, to_stdout: bool = False) -> int:
    """
    Decrypt encrypted fields in a JSON file.

    Args:
        filepath: Path to encrypted JSON file
        to_stdout: If True, print decrypted JSON instead of modifying file

    Returns:
        Number of fields decrypted
    """
    passphrase = get_passphrase()
    key = derive_key(passphrase)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not to_stdout:
        print(f"[INFO] Decrypting: {filepath}")

    processed, changes = _process_dict(data, key, encrypt=False)

    if to_stdout:
        print(json.dumps(processed, indent=2, ensure_ascii=False))
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[OK] Decrypted {changes} field(s)")

    return changes


def get_value(key_path: str, filepath: Optional[Path] = None) -> str:
    """
    Get a decrypted value from the API keys file.

    This is the primary function for other scripts to call.

    Args:
        key_path: Dot-notation path like "google_search.api_key"
        filepath: Optional path to keys file

    Returns:
        Decrypted value

    Example:
        >>> get_value("google_search.api_key")
        "AIzaSy..."
    """
    filepath = find_keys_file(str(filepath) if filepath else None)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Navigate to the value
    parts = key_path.split(".")
    value = data
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Key not found: {key_path}")
        value = value[part]

    if not isinstance(value, str):
        raise ValueError(f"Value at {key_path} is not a string")

    # Decrypt if encrypted
    if is_encrypted(value):
        passphrase = get_passphrase()
        key = derive_key(passphrase)
        return decrypt_value(value, key)

    return value


def show_status(filepath: Path) -> None:
    """Show encryption status of all fields in a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[INFO] Status: {filepath}\n")

    def _scan(obj: Dict, path: str = "") -> Tuple[int, int]:
        encrypted = 0
        plaintext = 0

        for field, value in obj.items():
            if field.startswith("_"):
                continue

            current = f"{path}.{field}" if path else field

            if isinstance(value, dict):
                e, p = _scan(value, current)
                encrypted += e
                plaintext += p
            elif isinstance(value, str) and is_sensitive_field(field):
                if is_encrypted(value):
                    print(f"  🔒 {current}")
                    encrypted += 1
                elif value.startswith("YOUR_") or value == "":
                    print(f"  ⚪ {current} (placeholder)")
                else:
                    print(f"  ⚠️  {current} (plaintext!)")
                    plaintext += 1

        return encrypted, plaintext

    enc_count, plain_count = _scan(data)
    print()
    print(f"  Encrypted: {enc_count}")
    print(f"  Plaintext: {plain_count}")

    if plain_count > 0:
        print(f"\n[WARN] Run 'python key_vault.py encrypt {filepath}' to encrypt")


def get_api_key(service: str, field: str = "api_key") -> str:
    """
    Convenience function for scripts to get API keys.

    Automatically handles encryption detection and decryption.

    Args:
        service: Service name (e.g., "google_search", "brave_search")
        field: Field name (default: "api_key")

    Returns:
        Decrypted API key value

    Example:
        >>> from key_vault import get_api_key
        >>> api_key = get_api_key("google_search")
    """
    return get_value(f"{service}.{field}")


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt/decrypt sensitive fields in API keys JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Encrypt all sensitive fields
    python key_vault.py encrypt api-keys.local.json

    # Get a single decrypted value
    python key_vault.py get google_search.api_key

    # Show encryption status
    python key_vault.py status

    # Decrypt to stdout (for debugging)
    python key_vault.py decrypt api-keys.local.json --stdout

    # Show machine ID (useful for debugging)
    python key_vault.py machine-id

Environment:
    KEYVAULT_PASSPHRASE - Master passphrase (required)
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # encrypt command
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt sensitive fields")
    enc_parser.add_argument("file", nargs="?", help="JSON file to encrypt")
    enc_parser.add_argument("-o", "--output", help="Output file (default: overwrite)")

    # decrypt command
    dec_parser = subparsers.add_parser("decrypt", help="Decrypt encrypted fields")
    dec_parser.add_argument("file", nargs="?", help="JSON file to decrypt")
    dec_parser.add_argument("--stdout", action="store_true",
                           help="Print to stdout instead of modifying file")

    # get command
    get_parser = subparsers.add_parser("get", help="Get a single decrypted value")
    get_parser.add_argument("path", help="Dot-notation path (e.g., google_search.api_key)")
    get_parser.add_argument("-f", "--file", help="JSON file to read from")

    # status command
    status_parser = subparsers.add_parser("status", help="Show encryption status")
    status_parser.add_argument("file", nargs="?", help="JSON file to check")

    # machine-id command
    subparsers.add_parser("machine-id", help="Show this machine's identifier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "encrypt":
            filepath = find_keys_file(args.file)
            output = Path(args.output) if args.output else None
            encrypt_file(filepath, output)

        elif args.command == "decrypt":
            filepath = find_keys_file(args.file)
            decrypt_file(filepath, args.stdout)

        elif args.command == "get":
            filepath = Path(args.file) if args.file else None
            value = get_value(args.path, filepath)
            print(value)

        elif args.command == "status":
            filepath = find_keys_file(args.file)
            show_status(filepath)

        elif args.command == "machine-id":
            print(f"Machine ID: {get_machine_id()}")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except InvalidToken:
        print("[ERROR] Decryption failed - wrong passphrase or different machine")
        sys.exit(1)


if __name__ == "__main__":
    main()
