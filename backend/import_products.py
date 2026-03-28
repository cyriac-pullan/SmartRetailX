import csv
import os
import sqlite3
from pathlib import Path

import psycopg2

# Resolve paths relative to this file to avoid CWD issues
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "smartretail.db"
CSV_PATHS = [
    BASE_DIR.parent / "database" / "products_complete.csv",
    BASE_DIR / "database" / "products_complete.csv",
    BASE_DIR / "products_complete.csv",
]

NEON_PRODUCTS_DSN = os.getenv(
    "NEON_PRODUCTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

csv_path = next((p for p in CSV_PATHS if p.exists()), None)
if not csv_path:
    raise FileNotFoundError("products_complete.csv not found in expected locations")

print(f"Reading products from: {csv_path}")
print(f"Importing into SQLite DB: {DB_PATH}")
print("Connecting to Neon products DB...")
print(f"Neon DSN: {NEON_PRODUCTS_DSN[:50]}...")  # Show first 50 chars

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Connect to Neon and ensure table exists
try:
    pg_conn = psycopg2.connect(NEON_PRODUCTS_DSN, sslmode="require")
    pg_cur = pg_conn.cursor()
    
    # Ensure products table exists in Neon
    pg_cur.execute("""
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
        CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
    """)
    pg_conn.commit()
    print("✓ Neon products table verified/created")
except Exception as e:
    print(f"✗ Error connecting to Neon DB: {e}")
    raise

print("Starting import...")

count = 0
errors = 0
with open(csv_path, "r", encoding="utf-8") as f:
    csv_reader = csv.DictReader(f)
    total_rows = sum(1 for _ in csv_reader)
    f.seek(0)
    csv_reader = csv.DictReader(f)
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
        try:
            payload = (
                row["Product_ID"].strip(),
                row["Barcode"].strip(),
                row["Product_Name"].strip(),
                float(row["Price"]),
                float(row["Weight_kg"]),
                row["Category"].strip(),
                row.get("Sub_Category", "").strip(),
                int(row["Aisle_No"]),
                int(row["Partition_No"]),
                row["Shelf_No"].strip(),
                row["Position_Tag"].strip(),
                row.get("Side", "Left").strip() or "Left",
                int(row["Stock_Quantity"]),
                int(row["Reorder_Level"]),
            )

            # Insert into SQLite
            cursor.execute(
                """
                INSERT OR REPLACE INTO products 
                (product_id, barcode, name, price, weight_kg, category, sub_category,
                 aisle, partition_no, shelf_no, position_tag, side,
                 stock_quantity, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload,
            )

            # Insert into Neon
            pg_cur.execute(
                """
                INSERT INTO products (product_id, barcode, name, price, weight_kg, category, sub_category,
                 aisle, partition_no, shelf_no, position_tag, side,
                 stock_quantity, reorder_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    barcode = EXCLUDED.barcode,
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    weight_kg = EXCLUDED.weight_kg,
                    category = EXCLUDED.category,
                    sub_category = EXCLUDED.sub_category,
                    aisle = EXCLUDED.aisle,
                    partition_no = EXCLUDED.partition_no,
                    shelf_no = EXCLUDED.shelf_no,
                    position_tag = EXCLUDED.position_tag,
                    side = EXCLUDED.side,
                    stock_quantity = EXCLUDED.stock_quantity,
                    reorder_level = EXCLUDED.reorder_level
                """,
                payload,
            )

            count += 1
            if count % 50 == 0:
                print(f"  Imported {count} products...")
                
        except KeyError as e:
            print(f"✗ Missing column '{e}' in CSV row {row_num}")
            errors += 1
            continue
        except Exception as e:
            print(f"✗ Error importing row {row_num} (Barcode: {row.get('Barcode', 'N/A')}): {e}")
            errors += 1
            continue

try:
conn.commit()
    print(f"✓ SQLite: Committed {count} products")
except Exception as e:
    print(f"✗ SQLite commit error: {e}")

try:
    pg_conn.commit()
    print(f"✓ Neon: Committed {count} products")
except Exception as e:
    print(f"✗ Neon commit error: {e}")
    raise

# Verify import
pg_cur.execute("SELECT COUNT(*) FROM products")
neon_count = pg_cur.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM products")
sqlite_count = cursor.fetchone()[0]

print(f"\n{'='*50}")
print(f"Import Summary:")
print(f"  CSV rows processed: {count}")
print(f"  Errors: {errors}")
print(f"  SQLite products: {sqlite_count}")
print(f"  Neon products: {neon_count}")
print(f"{'='*50}")

if neon_count == 0:
    print("\n⚠ WARNING: Neon products table is empty!")
    print("Check the connection string and try again.")

cursor.close()
conn.close()
pg_cur.close()
pg_conn.close()

