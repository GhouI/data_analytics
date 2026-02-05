import sys
from pathlib import Path

# Add src directory to Python path so imports resolve correctly
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from config import RAW_DATA_DIRECTORY, Config
from etl_pipeline import (
    create_db_schema,
    extract_products,
    get_first_product,
    load_data_to_database,
    save_data,
    transform_data,
)


def main():
    Config.ensure_dirs()
    data = extract_products()
    _ = save_data(data, RAW_DATA_DIRECTORY / "raw_products.json")
    transformed_data = transform_data(data)
    _ = save_data(
        transformed_data.to_dict(orient="records"),
        Config.PROCESSED_DATA_DIRECTORY / "processed_products.json",
    )
    create_db_schema()
    load_data_to_database(transformed_data)
    print(get_first_product())


if __name__ == "__main__":
    main()
