-- Categories Table
CREATE TABLE IF NOT EXISTS Categories(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL
);
-- Products
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price_usd REAL NOT NULL,
    price_eur REAL NOT NULL,
    description TEXT,
    category_id INTEGER,
    image_url TEXT,
    price_category TEXT CHECK(price_category IN ('low', 'medium', 'high')),
    price_per_rating REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
CREATE TABLE IF NOT EXISTS Ratings (
    product_id INTEGER PRIMARY KEY,
    customer_rating REAL NOT NULL,
    customer_reviews INTEGER NOT NULL,
    product_highly_recommended BOOLEAN NOT NULL,
    confidence_score REAL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
CREATE INDEX IF NOT EXISTS idx_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_price_category ON products(price_category);
CREATE INDEX IF NOT EXISTS idx_highly_rated ON ratings(product_highly_recommended);
