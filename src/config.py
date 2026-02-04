import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIRECTORY / "data"
PROCESSED_DATA_DIRECTORY = DATA_DIRECTORY / "processed"
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
    if not PROCESSED_DATA_DIRECTORY.exists():
        PROCESSED_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)


class Config:
    """Simple container for configuration constants."""

    BASE_DIRECTORY = BASE_DIRECTORY
    DATA_DIRECTORY = DATA_DIRECTORY
    RAW_DATA_DIRECTORY = RAW_DATA_DIRECTORY
    PROCESSED_DATA_DIRECTORY = PROCESSED_DATA_DIRECTORY

    FAKE_STORE_API_URL = FAKE_STORE_API_URL
    EXCHANGE_RATE_API_URL = EXCHANGE_RATE_API_URL

    # Transformation Configuration
    TARGET_CURRENCY = "EUR"
    LOW_PRICE_THRESHOLD = 5
    HIGH_PRICE_THRESHOLD = 100
    RATING_THRESHOLD = 4.5

    @staticmethod
    def ensure_dirs():
        ensure_directories()


__all__ = [
    "BASE_DIRECTORY",
    "DATA_DIRECTORY",
    "RAW_DATA_DIRECTORY",
    "PROCESSED_DATA_DIRECTORY",
    "FAKE_STORE_API_URL",
    "ensure_directories",
    "Config",
]
