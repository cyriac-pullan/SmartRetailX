#!/usr/bin/env python3
"""
import_products2.py
-------------------
Reads products_combined_remapped.csv and inserts products PROD00501-PROD01000
(rows 501-1000) into the `products2` table in NeonDB.
"""
import csv
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed.")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR.parent / "database" / "products_unique_remapped.csv"

NEON_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)


def main():
    print("=" * 70)
    print("SMARTRETAILX - IMPORT PRODUCTS 501-1000 INTO products2")
    print("=" * 70)

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found: {CSV_PATH}")
        sys.exit(1)
    print(f"✓ Found CSV: {CSV_PATH.name}")

    # Connect
    print("\nConnecting to NeonDB...")
    try:
        conn = psycopg2.connect(NEON_DSN, sslmode="require")
        cur = conn.cursor()
        print("✓ Connected")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Create products2 table (same schema as products)
    print("\nCreating/resetting products2 table...")
    try:
        cur.execute("DROP TABLE IF EXISTS products2 CASCADE;")
        cur.execute("""
            CREATE TABLE products2 (
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
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products2_barcode ON products2(barcode);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products2_category ON products2(category);")
        conn.commit()
        print("✓ products2 table ready")
    except Exception as e:
        print(f"✗ Table creation error: {e}")
        sys.exit(1)

    # Read CSV and filter rows 501-1000 by Product_ID
    print("\nReading CSV, selecting PROD00501-PROD01000...")
    count = 0
    errors = []

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row.get("Product_ID", "").strip()
            if not pid.startswith("PROD"):
                continue
            try:
                num = int(pid[4:])
            except ValueError:
                continue
            if num < 501 or num > 1000:
                continue  # Only products 501-1000

            try:
                payload = (
                    pid,
                    row["Barcode"].strip(),
                    row["Product_Name"].strip(),
                    float(row["Price"]),
                    float(row["Weight_kg"]),
                    row["Category"].strip(),
                    row.get("Sub_Category", "").strip() or None,
                    int(row["Aisle_No"]),
                    int(row["Partition_No"]),
                    row["Shelf_No"].strip(),
                    row["Position_Tag"].strip(),
                    row.get("Side", "Left").strip() or "Left",
                    int(row["Stock_Quantity"]),
                    int(row["Reorder_Level"]),
                )
                cur.execute("""
                    INSERT INTO products2
                    (product_id, barcode, name, price, weight_kg, category, sub_category,
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
                """, payload)
                count += 1
                if count % 100 == 0:
                    conn.commit()
                    print(f"  - Inserted {count} rows...")
            except Exception as e:
                errors.append(f"{pid}: {e}")

    try:
        conn.commit()
    except Exception as e:
        print(f"✗ Final commit error: {e}")
        conn.rollback()
        sys.exit(1)

    # Verify
    cur.execute("SELECT COUNT(*) FROM products2")
    final_count = cur.fetchone()[0]

    cur.execute("SELECT aisle, COUNT(*) FROM products2 GROUP BY aisle ORDER BY aisle")
    aisle_rows = cur.fetchall()

    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Products inserted into products2 : {count}")
    print(f"Total in products2 (DB)          : {final_count}")
    print(f"Errors                           : {len(errors)}")
    print("\nBy Aisle in products2:")
    for a, c in aisle_rows:
        print(f"  Aisle {a}: {c} products")

    if errors:
        print("\nErrors (first 10):")
        for e in errors[:10]:
            print(f"  - {e}")

    cur.close()
    conn.close()

    print("\n" + "=" * 70)
    if final_count == 500:
        print("✓ SUCCESS! 500 products (PROD00501-PROD01000) in products2")
    else:
        print(f"⚠ Expected 500 but got {final_count}. Check errors above.")
    print("=" * 70)


if __name__ == "__main__":
    main()
