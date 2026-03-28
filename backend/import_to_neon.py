#!/usr/bin/env python3
"""
Standalone script to import products to Neon DB
Run this: python import_to_neon.py
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
CSV_FILES = [
    BASE_DIR.parent / "database" / "products_unique_remapped.csv"
]

NEON_PRODUCTS_DSN = os.getenv(
    "NEON_PRODUCTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def main():
    print("=" * 70)
    print("SMARTRETAILX - PRODUCT IMPORT TO NEON")
    print("=" * 70)
    
    # Check CSVs
    for csv_path in CSV_FILES:
        if not csv_path.exists():
            print(f"\nERROR: CSV file not found at: {csv_path}")
            sys.exit(1)
        print(f"✓ Found CSV: {csv_path.name}")
    
    # Connect to Neon
    print(f"\nConnecting to Neon Products DB...")
    try:
        pg_conn = psycopg2.connect(NEON_PRODUCTS_DSN, sslmode="require")
        pg_cur = pg_conn.cursor()
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print(f"\nCheck your Neon connection string:")
        print(f"  {NEON_PRODUCTS_DSN[:60]}...")
        sys.exit(1)
    
    # Create table
    print("\nCreating/verifying products table...")
    try:
        # Reset table as requested by user
        print("  ! Force reset: Dropping existing products table...")
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
        print("✓ Table created/verified")
    except Exception as e:
        print(f"✗ Table creation error: {e}")
        sys.exit(1)
    
    # Count existing products
    pg_cur.execute("SELECT COUNT(*) FROM products")
    existing_count = pg_cur.fetchone()[0]
    print(f"✓ Current products in DB: {existing_count}")
    
    # Read CSVs
    print(f"\nReading CSV files...")
    count = 0
    errors = []
    
    for csv_path in CSV_FILES:
        print(f"  Processing {csv_path.name}...")
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    if not row.get("Barcode") or not row.get("Product_ID"):
                        errors.append(f"Row {row_num} in {csv_path.name}: Missing Barcode or Product_ID")
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
                    
                    # Insert/Update in Neon
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
                        print(f"    - Processed {count} items total...")
                        pg_conn.commit()  # Commit in batches
                        
                except KeyError as e:
                    errors.append(f"Row {row_num} in {csv_path.name}: Missing column {e}")
                except ValueError as e:
                    errors.append(f"Row {row_num} in {csv_path.name}: Invalid value - {e}")
                except Exception as e:
                    errors.append(f"Row {row_num} in {csv_path.name}: {e}")
    
    # Final commit
    try:
        pg_conn.commit()
        print(f"\n✓ Committed {count} products to Neon")
    except Exception as e:
        print(f"\n✗ Commit error: {e}")
        pg_conn.rollback()
        sys.exit(1)
    
    # Verify
    pg_cur.execute("SELECT COUNT(*) FROM products")
    final_count = pg_cur.fetchone()[0]
    
    # Show sample
    pg_cur.execute("SELECT barcode, name FROM products ORDER BY product_id LIMIT 5")
    samples = pg_cur.fetchall()
    
    print("\n" + "=" * 70)
    print("IMPORT SUMMARY")
    print("=" * 70)
    print(f"Products processed: {count}")
    print(f"Errors: {len(errors)}")
    print(f"Total products in DB: {final_count}")
    
    if samples:
        print(f"\nSample products:")
        for barcode, name in samples:
            print(f"  {barcode}: {name[:60]}")
    
    if errors:
        print(f"\nErrors encountered (showing first 10):")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    pg_cur.close()
    pg_conn.close()
    
    print("\n" + "=" * 70)
    if final_count > 0:
        print("✓ IMPORT SUCCESSFUL!")
        print(f"✓ {final_count} products are now in Neon DB")
        print("\nYou can now run: python app.py")
    else:
        print("⚠ WARNING: No products imported!")
        print("Check the errors above and try again.")
    print("=" * 70)

if __name__ == "__main__":
    main()
