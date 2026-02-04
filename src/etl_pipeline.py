import json
import logging
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# DIRECTORIES
BASE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIRECTORY / "data"
RAW_DATA_DIRECTORY = DATA_DIRECTORY / "raw"
# URLS
FAKE_STORE_API_URL = os.getenv("FAKE_STORE_API_URL")


def extract_products():
    """This function extracts products data from the Fake Store API."""
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


def save_raw_data(data):
    """From the extracted data we save this to a file"""
    if not data:
        raise ValueError("No data to save")

    if not RAW_DATA_DIRECTORY.exists():
        RAW_DATA_DIRECTORY.mkdir(parents=True)

    file_path = RAW_DATA_DIRECTORY / "products.json"
    if file_path.exists():
        logging.info(
            f"Raw data already exists at {file_path}. Please delete it before saving new data."
        )
        return
    with open(file_path, "w") as file:
        json.dump(data, file)
    logging.info(f"Raw data saved to {file_path}")


def transform_data(data):
    """Transform the raw data into a pandas DataFrame"""
    df = pd.DataFrame(data)
    # extract rating fields (average score and review count) into separate columns
    df["customer_rating"] = df["rating"].apply(lambda x: x["rate"])  # rating_mean
    df["customer_reviews"] = df["rating"].apply(lambda x: x["count"])  # rating_samples
    df = df.drop(columns=["rating"], axis=1)

    # Renaming columns
    df = df.rename(columns={"image": "image_url"})
    return df


data = extract_products()
save_raw_data(data)
