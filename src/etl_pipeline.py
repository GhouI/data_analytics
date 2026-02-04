import json
import logging

import pandas as pd
import requests

from config import Config


def extract_products():
    """This function extracts products data from the Fake Store API."""
    if not Config.FAKE_STORE_API_URL:
        logging.info(Config.FAKE_STORE_API_URL)
        raise ValueError("FAKE_STORE_API_URL is not set")
    try:
        response = requests.get(Config.FAKE_STORE_API_URL + "/products")
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

    file_path = Config.RAW_DATA_DIRECTORY / "products.json"
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
    df = df.rename(columns={"image": "image_url"})  # Being more specific

    return df


data = extract_products()
save_raw_data(data)
