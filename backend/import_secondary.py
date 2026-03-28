#!/usr/bin/env python3
"""
Script to import products_part2.csv to the Secondary Neon DB
"""
import csv
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR.parent / "database" / "products_part2.csv"

# Secondary DB DSN
NEON_PRODUCTS_DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def main():
    print("=" * 70)
    print("SMARTRETAILX - SECONDARY DB IMPORT (Part 2)")
    print("=" * 70)
    
    if not CSV_PATH.exists():
        print(f"\nERROR: CSV file not found at: {CSV_PATH}")
        sys.exit(1)
    print(f"✓ Found CSV: {CSV_PATH.name}")
    
    # Connect
    print(f"\nConnecting to Secondary Neon DB...")
    try:
        pg_conn = psycopg2.connect(NEON_PRODUCTS_DSN, sslmode="require")
        pg_cur = pg_conn.cursor()
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)
    
    # Reset Table
    print("\nResetting products table...")
    try:
        pg_cur.execute("DROP TABLE IF EXISTS products CASCADE;")
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
        """)
        pg_cur.execute("CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);")
        pg_cur.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
        pg_conn.commit()
        print("✓ Table reset and created")
    except Exception as e:
        print(f"✗ Table error: {e}")
        sys.exit(1)
    
    # Import
    print(f"\nImporting {CSV_PATH.name}...")
    count = 0
    errors = []
    
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                if not row.get("Barcode") or not row.get("Product_ID"):
                    continue
                
                payload = (
                    row["Product_ID"].strip(),
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
                
                pg_cur.execute("""
                    INSERT INTO products 
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
                    print(f"  Processed {count} items...")
                    pg_conn.commit()
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {e}")
    
    pg_conn.commit()
    print(f"\n✓ Successfully imported {count} products to Secondary DB")
    
    pg_cur.close()
    pg_conn.close()

if __name__ == "__main__":
    main()
