"""
Import all mapped products from store_inventory_optimized.csv into Neon DB.
Splits into products (first 500) and products2 (next 500) tables.
Uses UPSERT so re-running is safe.
"""
import os, sys
import pandas as pd
import psycopg2
import psycopg2.extras

DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "store_inventory_optimized.csv")

def get_conn():
    return psycopg2.connect(DSN, sslmode="require", connect_timeout=15)

def ensure_tables(cur):
    for tbl in ("products", "products2"):
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {tbl} (
                product_id   TEXT PRIMARY KEY,
                barcode      TEXT UNIQUE NOT NULL,
                name         TEXT NOT NULL,
                price        REAL NOT NULL,
                weight_kg    REAL NOT NULL,
                category     TEXT NOT NULL,
                sub_category TEXT,
                aisle        INT,
                partition_no INT,
                shelf_no     TEXT,
                position_tag TEXT,
                side         TEXT,
                stock_quantity INT DEFAULT 100,
                reorder_level  INT DEFAULT 5,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

UPSERT_SQL = """
    INSERT INTO {table} (product_id, barcode, name, price, weight_kg, category,
                         sub_category, aisle, partition_no, shelf_no, position_tag,
                         side, stock_quantity, reorder_level)
    VALUES %s
    ON CONFLICT (product_id) DO UPDATE SET
        barcode      = EXCLUDED.barcode,
        name         = EXCLUDED.name,
        price        = EXCLUDED.price,
        weight_kg    = EXCLUDED.weight_kg,
        category     = EXCLUDED.category,
        sub_category = EXCLUDED.sub_category,
        aisle        = EXCLUDED.aisle,
        partition_no = EXCLUDED.partition_no,
        shelf_no     = EXCLUDED.shelf_no,
        position_tag = EXCLUDED.position_tag,
        side         = EXCLUDED.side,
        stock_quantity = EXCLUDED.stock_quantity,
        reorder_level  = EXCLUDED.reorder_level;
"""

def import_df(cur, df, table):
    rows = [
        (
            str(r["Product_ID"]),
            str(r["Barcode"]),
            str(r["Product_Name"]),
            float(r["Price"]),
            float(r["Weight_kg"]),
            str(r["Category"]),
            str(r["Sub_Category"]) if pd.notna(r["Sub_Category"]) else None,
            int(r["Aisle_No"]),
            int(r["Partition_No"]),
            str(r["Shelf_No"]),
            str(r["Position_Tag"]),
            str(r["Side"]),
            int(r["Stock_Quantity"]),
            int(r["Reorder_Level"]),
        )
        for _, r in df.iterrows()
    ]
    psycopg2.extras.execute_values(cur, UPSERT_SQL.format(table=table), rows, page_size=100)
    return len(rows)

def main():
    print("Reading: " + CSV_PATH)
    df = pd.read_csv(CSV_PATH)
    print("Total rows: " + str(len(df)))

    # Split 500 / 500 (matching backend split)
    df1 = df.iloc[:500].reset_index(drop=True)
    df2 = df.iloc[500:].reset_index(drop=True)
    print("  -> products:  " + str(len(df1)) + " rows")
    print("  -> products2: " + str(len(df2)) + " rows")

    print("\nConnecting to Neon DB...")
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    print("Ensuring tables exist...")
    ensure_tables(cur)
    conn.commit()

    print("Upserting products table...")
    n1 = import_df(cur, df1, "products")
    conn.commit()
    print("  OK " + str(n1) + " rows upserted into products")

    print("Upserting products2 table...")
    n2 = import_df(cur, df2, "products2")
    conn.commit()
    print("  OK " + str(n2) + " rows upserted into products2")

    # Verify
    cur.execute("SELECT COUNT(*) FROM products;")
    c1 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM products2;")
    c2 = cur.fetchone()[0]
    print("\nDone! Neon DB now has " + str(c1) + " rows in products, " + str(c2) + " rows in products2")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
