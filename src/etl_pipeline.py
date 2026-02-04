import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
# Extracting the data from the
FAKE_STORE_API_URL = os.getenv("FAKE_STORE_API_URL")


def extract_data():
    if not FAKE_STORE_API_URL:
        logging.info(FAKE_STORE_API_URL)
        raise ValueError("FAKE_STORE_API_URL is not set")
    try:
        response = requests.get(FAKE_STORE_API_URL + "/products")
        response.raise_for_status()
        data = response.json()
        logging.info("Data extracted successfully")
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch data from API: {e}")


print(extract_data())
