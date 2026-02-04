import json
import logging
import sqlite3
from datetime import datetime, timezone

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


def get_exchange_rate():
    # Fetch target currency rate
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

    df["created_at"] = datetime.now(timezone.utc).isoformat()
    return df


def create_db_schema():
    """
    Creates the database tables if they do not exist.
    """
    connection = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connection.cursor()
    schema = Config.DATABASE_SCHEMA
    with open(schema, "r") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    connection.commit()
    connection.close()


def load_to_database(df):
    """Transforms the data into the SQL Database"""
    # Run schema script
    connection = sqlite3.connect(Config.DATABASE_PATH)
    cursor = connection.cursor()
    with open(Config.DATABASE_SCHEMA, "r") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    connection.commit()
    connection.close()


def load_data_to_database(df):
    # Insert categories, products, and ratings
    connection = sqlite3.connect(Config.DATABASE_PATH)
    try:
        existing = pd.read_sql("SELECT COUNT(*) as cnt FROM Products", connection)
        if existing["cnt"].iloc[0] > 0:
            print("Database already has data, skipping load.")
            connection.close()
            return

        unique_categories = df["category"].unique()
        cursor = connection.cursor()
        for cat in unique_categories:
            cursor.execute("INSERT INTO Categories (category_name) VALUES (?)", (cat,))
        connection.commit()
        categories_map = pd.read_sql(
            "SELECT category_id, category_name FROM Categories", connection
        )
        df = df.merge(
            categories_map, left_on="category", right_on="category_name", how="left"
        )
        for _, row in df.iterrows():
            cursor.execute(
                """INSERT INTO Products (id, title, price_usd, price_eur, description,
                   category_id, image_url, price_category, price_per_rating, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"],
                    row["title"],
                    row["price_usd"],
                    row["price_eur"],
                    row["description"],
                    row["category_id"],
                    row["image_url"],
                    str(row["price_category"]),
                    row["price_per_rating"],
                    row["created_at"],
                ),
            )
            cursor.execute(
                """INSERT INTO Ratings (product_id, customer_rating, customer_reviews,
                   product_highly_recommended) VALUES (?, ?, ?, ?)""",
                (
                    row["id"],
                    row["customer_rating"],
                    row["customer_reviews"],
                    bool(row["product_highly_recommended"]),
                ),
            )
        connection.commit()
        print("data loaded successfully")

    except Exception as e:
        connection.rollback()
        print(f"Error loading categories: {e}")


def get_first_product():
    # Get first product row
    connection = sqlite3.connect(Config.DATABASE_PATH)
    row = pd.read_sql("SELECT * FROM Products LIMIT 1", connection)
    connection.close()
    return row


if __name__ == "__main__":
    data = extract_products()
    save_data(data, RAW_DATA_DIRECTORY / "raw_products.json")
    transformed_data = transform_data(data)
    df = transformed_data.to_dict(orient="records")
    save_data(df, Config.PROCESSED_DATA_DIRECTORY / "processed_products.json")
    create_db_schema()
    load_data_to_database(transformed_data)
    print(get_first_product())
