
import base64
import hashlib
import hmac
import json
import secrets
from pathlib import Path

from cryptography.fernet import Fernet


from solution.paths import KEY_FILE


def generate_keys():
    """Generate encryption keys once and save them locally."""
    if KEY_FILE.exists():
        raise FileExistsError(
            "Keys already exist. Existing keys will not be overwritten."
        )

    fernet_key = Fernet.generate_key()
    hmac_key = base64.urlsafe_b64encode(secrets.token_bytes(32))

    keys = {
        "fernet_key": fernet_key.decode("utf-8"),
        "hmac_key": hmac_key.decode("utf-8"),
    }

    KEY_FILE.write_text(
        json.dumps(keys, indent=4),
        encoding="utf-8",
    )


def load_keys():
    """Load the persistent encryption and HMAC keys."""
    if not KEY_FILE.exists():
        raise FileNotFoundError(
            "Encryption keys are missing. Generate them first."
        )

    keys = json.loads(KEY_FILE.read_text(encoding="utf-8"))

    fernet_key = keys["fernet_key"].encode("utf-8")
    hmac_key = base64.urlsafe_b64decode(keys["hmac_key"])

    return fernet_key, hmac_key


def encrypt_value(value: str) -> bytes | None:
    if value is None:
        return None

    fernet_key, _ = load_keys()
    return Fernet(fernet_key).encrypt(value.encode("utf-8"))


def decrypt_value(encrypted_value: bytes) -> str | None:
    if encrypted_value is None:
        return None

    fernet_key, _ = load_keys()
    return Fernet(fernet_key).decrypt(encrypted_value).decode("utf-8")


def hash_phone(normalized_phone: str) -> bytes:
    """Create a deterministic HMAC-SHA256 lookup hash."""
    _, hmac_key = load_keys()

    return hmac.new(
        hmac_key,
        normalized_phone.encode("utf-8"),
        hashlib.sha256,
    ).digest()
