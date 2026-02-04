# Data Analytics Pipeline

ETL pipeline that extracts product data from the Fake Store API, transforms it with currency conversion and categorization, and loads it into a SQLite database.

## Pipeline Stages

1. **Extract** — Fetches product data from the [Fake Store API](https://fakestoreapi.com) and saves raw JSON locally.
2. **Transform** — Converts prices from USD to GBP, categorizes products by price tier (low/medium/high), and flags highly rated items.
3. **Load** — Writes the transformed data into a SQLite database.

## Configuration

Settings are defined in `config.py`. The following can be overridden with environment variables:

| Variable | Default | Description |
|---|---|---|
| `FAKE_STORE_API_URL` | `https://fakestoreapi.com` | Product data source |
| `EXCHANGE_RATE_API_URL` | `https://api.exchangerate-api.com/v4/latest/USD` | Exchange rate provider |
| `DATABASE_NAME` | `products.db` | SQLite database filename |

### Thresholds

| Setting | Value |
|---|---|
| Low price | < $20 |
| High price | > $100 |
| Highly rated | >= 4.0 stars |

## Project Structure

```
data_analytics/
├── config.py
├── data/
│   ├── raw/          # Timestamped raw JSON extracts
│   └── database/     # SQLite database
└── README.md
```

## Usage

```bash
pip install -r requirements.txt
python main.py
```
