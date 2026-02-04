import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIRECTORY / "data"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"

# External URLs & environment variables
FAKE_STORE_API_URL = os.getenv("FAKE_STORE_API_URL")
EXCHANGE_RATE_API_URL = os.getenv("EXCHANGE_RATE_API_URL")


def ensure_directories():
    """Create data directories if they don't exist."""
    if not DATA_DIRECTORY.exists():
        DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    if not RAW_DATA_DIRECTORY.exists():
        RAW_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)


class Config:
    """Simple container for configuration constants."""

    BASE_DIRECTORY = BASE_DIRECTORY
    DATA_DIRECTORY = DATA_DIRECTORY
    RAW_DATA_DIRECTORY = RAW_DATA_DIRECTORY
    FAKE_STORE_API_URL = FAKE_STORE_API_URL

    @staticmethod
    def ensure_dirs():
        ensure_directories()


__all__ = [
    "BASE_DIRECTORY",
    "DATA_DIRECTORY",
    "RAW_DATA_DIRECTORY",
    "FAKE_STORE_API_URL",
    "ensure_directories",
    "Config",
]
