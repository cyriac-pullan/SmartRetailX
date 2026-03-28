"""
fix_product_count.py  –  run-once script
Goal: products table = exactly 500, products2 table = exactly 500 (total 1000)
Strategy:
  - Count rows in each table
  - Delete excess rows (keeping the lowest product_ids / earliest created)
  - Print final counts
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os
import psycopg2
import psycopg2.extras

NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
TARGET = 500   # rows per table

def get_conn():
    return psycopg2.connect(NEON_DB_DSN, cursor_factory=psycopg2.extras.RealDictCursor)

def trim_table(cur, table: str, target: int):
    cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
    cnt = cur.fetchone()['cnt']
    print(f"  {table}: {cnt} rows", end="")
    if cnt <= target:
        print(f" — already at or below {target}, nothing to do.")
        return 0
    excess = cnt - target
    print(f" — deleting {excess} excess rows...")
    # Delete the excess highest-barcode rows (keep earlier ones)
    cur.execute(f"""
        DELETE FROM {table}
        WHERE barcode IN (
            SELECT barcode FROM {table}
            ORDER BY barcode DESC
            LIMIT %s
        )
    """, (excess,))
    return excess

def main():
    conn = get_conn()
    cur  = conn.cursor()
    print("=== Product table trim ===")
    deleted1 = trim_table(cur, "products",  TARGET)
    deleted2 = trim_table(cur, "products2", TARGET)
    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) AS cnt FROM products")
    c1 = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) AS cnt FROM products2")
    c2 = cur.fetchone()['cnt']

    cur.close()
    conn.close()

    print(f"\nDone! products={c1}, products2={c2}, total={c1+c2}")
    print(f"Deleted: {deleted1 + deleted2} rows total")

if __name__ == '__main__':
    main()
