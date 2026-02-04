import json
import logging

import pandas as pd
import requests

from config import EXCHANGE_RATE_API_URL, FAKE_STORE_API_URL, RAW_DATA_DIRECTORY, Config


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


def save_data(data, file_path):
    """Saving the data to a directory."""
    if not data or not file_path:
        raise ValueError("Invalid data or file path. Please make sure to provide")
    if file_path.exists():
        logging.info(
            f"Data already exists at {file_path}. Please delete it before saving new data."
        )
    with open(file_path, "w") as file:
        json.dump(data, file)
    logging.info(f"Data saved to {file_path}")
    return file_path


def save_raw_data(data):
    """From the extracted data we save this to a file"""
    if not data:
        raise ValueError("No data to save")

    file_path = RAW_DATA_DIRECTORY / "products.json"
    if file_path.exists():
        logging.info(
            f"Raw data already exists at {file_path}. Please delete it before saving new data."
        )
        return
    with open(file_path, "w") as file:
        json.dump(data, file)

    logging.info(f"Raw data saved to {file_path}")
    return file_path


def save_processed_data(data):
    file_path = Config.PROCESSED_DATA_DIRECTORY / "products.json"
    if file_path.exists():
        logging.info(
            f"Processed data already exists at {file_path}. Please delete it before saving new data."
        )
        return
    with open(file_path, "w") as file:
        json.dump(data, file)

    logging.info(f"Processed data saved to {file_path}")
    return file_path


def get_exchange_rate():
    if not EXCHANGE_RATE_API_URL:
        raise ValueError("Exchange rate API URL is not configured")
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        euro_rates = data["rates"].get(Config.TARGET_CURRENCY)
        if not euro_rates:
            raise ValueError(
                f"Target currency {Config.TARGET_CURRENCY} not found in response"
            )
        return euro_rates
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch exchange rate: {e}")


def transform_data(data):
    if not get_exchange_rate():
        raise ValueError("Exchange rate not available")

    """Transform the raw data into a pandas DataFrame"""
    df = pd.DataFrame(data)

    # extract rating fields (average score and review count) into separate columns
    df["customer_rating"] = df["rating"].apply(lambda x: x["rate"])  # rating_mean
    df["customer_reviews"] = df["rating"].apply(lambda x: x["count"])  # rating_samples
    df = df.drop(columns=["rating"])

    # Renaming columns
    df = df.rename(
        columns={"image": "image_url", "price": "price_usd"}
    )  # Being more specific

    df["price_eur"] = (df["price_usd"] * get_exchange_rate()).round(2)

    # Price Categories via Vectors
    df["price_category"] = pd.cut(
        df["price_usd"],
        bins=[0, Config.LOW_PRICE_THRESHOLD, Config.HIGH_PRICE_THRESHOLD, float("inf")],
        labels=["low", "medium", "high"],
    )
    # Finding out if a product is highly recommended
    df["product_highly_recommended"] = df["customer_rating"] >= Config.RATING_THRESHOLD

    df["price_per_rating"] = (
        df["price_usd"] / df["customer_rating"].replace(0, float("nan"))
    ).round(2)
    return df


data = extract_products()
save_data(data, RAW_DATA_DIRECTORY / "raw_products.json")
transformed_data = transform_data(data)
df = transformed_data.to_dict(orient="records")
save_data(df, Config.PROCESSED_DATA_DIRECTORY / "processed_products.json")
print(transformed_data.to_string())
