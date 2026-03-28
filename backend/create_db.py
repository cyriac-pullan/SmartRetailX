import sqlite3
import csv
from datetime import datetime

# Connect to database (creates if doesn't exist)
conn = sqlite3.connect('smartretail.db')
cursor = conn.cursor()

# ===== PRODUCTS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    weight_kg REAL NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    aisle INT,
    partition_no INT,
    shelf_no TEXT,
    position_tag TEXT,
    side TEXT,
    stock_quantity INT DEFAULT 100,
    reorder_level INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# ===== CARTS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS carts (
    cart_id TEXT PRIMARY KEY,
    customer_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);
''')

# ===== CART_ITEMS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    barcode TEXT NOT NULL,
    quantity INT NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY(cart_id) REFERENCES carts(cart_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
''')

# ===== BILLS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS bills (
    bill_id TEXT PRIMARY KEY,
    cart_id TEXT NOT NULL,
    customer_id TEXT,
    items_count INT,
    subtotal REAL,
    tax REAL,
    discount REAL,
    total_amount REAL NOT NULL,
    expected_weight_kg REAL,
    actual_weight_kg REAL,
    weight_variance_kg REAL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cart_id) REFERENCES carts(cart_id)
);
''')

# ===== WEIGHT_READINGS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS weight_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id TEXT NOT NULL,
    expected_weight REAL,
    actual_weight REAL,
    variance REAL,
    tolerance_threshold REAL DEFAULT 0.5,
    status TEXT DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(bill_id) REFERENCES bills(bill_id)
);
''')

# ===== CUSTOMERS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# ===== TRANSACTIONS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    bill_id TEXT NOT NULL,
    customer_id TEXT,
    payment_method TEXT,
    amount REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(bill_id) REFERENCES bills(bill_id)
);
''')

# ===== RECOMMENDATIONS TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_barcode TEXT NOT NULL,
    recommended_product_barcode TEXT NOT NULL,
    co_occurrence_count INT DEFAULT 1,
    confidence REAL DEFAULT 0.0,
    FOREIGN KEY(product_barcode) REFERENCES products(barcode),
    FOREIGN KEY(recommended_product_barcode) REFERENCES products(barcode)
);
''')

# ===== DEMAND_FORECAST TABLE =====
cursor.execute('''
CREATE TABLE IF NOT EXISTS demand_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    forecast_date DATE,
    predicted_quantity INT,
    actual_quantity INT,
    forecast_accuracy REAL,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
''')

# Create indexes for fast lookup
cursor.execute('CREATE INDEX IF NOT EXISTS idx_barcode ON products(barcode);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_cart_id ON cart_items(cart_id);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_bill_id ON bills(bill_id);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_category ON products(category);')

print("✓ Database schema created successfully!")
conn.commit()
conn.close()

