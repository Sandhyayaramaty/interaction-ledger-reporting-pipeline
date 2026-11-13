import os
from pathlib import Path

# Input data directory
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

# Generated report directory
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "reports"))

# Encryption key file
KEY_FILE = Path(
    os.getenv(
        "ENCRYPTION_KEY_FILE",
        str(Path(__file__).resolve().parent / "keys.json"),
    )
)