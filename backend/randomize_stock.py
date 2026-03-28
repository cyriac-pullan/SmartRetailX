"""
randomize_stock.py
One-time script: update stock_quantity for all products to random values,
ensuring ~30% are at or below reorder_level to trigger the restock dashboard.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, random
import psycopg2
import psycopg2.extras

NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def get_conn():
    return psycopg2.connect(NEON_DB_DSN, cursor_factory=psycopg2.extras.RealDictCursor)

def randomize(total, products):
    """Return list of (stock_qty, reorder_level, product_id)"""
    updates = []
    for i, p in enumerate(products):
        reorder = random.randint(8, 20)            # realistic reorder threshold

        # ~30% of products below or at reorder level (show as critical/low)
        rnd = random.random()
        if rnd < 0.15:
            # Critical — below reorder level
            qty = random.randint(0, reorder - 1)
        elif rnd < 0.30:
            # Low — just above reorder (up to 2x reorder)
            qty = random.randint(reorder, reorder * 2)
        else:
            # Healthy stock
            qty = random.randint(reorder * 2 + 1, 120)

        updates.append((qty, reorder, p['product_id']))

    return updates

def main():
    conn = get_conn()
    cur  = conn.cursor()

    # Fetch all products from primary table
    cur.execute("SELECT product_id, name, stock_quantity, reorder_level FROM products")
    products = list(cur.fetchall())
    print(f"Found {len(products)} products in 'products' table.")

    if not products:
        print("No products found — exiting.")
        conn.close()
        return

    updates = randomize(len(products), products)

    # Batch update
    cur.executemany(
        "UPDATE products SET stock_quantity = %s, reorder_level = %s WHERE product_id = %s",
        updates
    )

    # Also update products2 if it exists
    try:
        cur.execute("SELECT product_id FROM products2 LIMIT 1")
        cur.execute("SELECT product_id, name FROM products2")
        products2 = list(cur.fetchall())
        if products2:
            updates2 = randomize(len(products2), products2)
            cur.executemany(
                "UPDATE products2 SET stock_quantity = %s, reorder_level = %s WHERE product_id = %s",
                updates2
            )
            print(f"Updated {len(products2)} rows in 'products2' table.")
    except Exception:
        pass  # products2 may not exist

    conn.commit()

    # Summary
    critical = sum(1 for u in updates if u[0] < u[1])
    low      = sum(1 for u in updates if u[1] <= u[0] <= u[1]*2)
    healthy  = len(updates) - critical - low

    cur.close()
    conn.close()

    print(f"\nDone!")
    print(f"  Critical (below reorder): {critical} products ({critical*100//len(updates)}%)")
    print(f"  Low stock (≤ 2x reorder): {low} products ({low*100//len(updates)}%)")
    print(f"  Healthy stock:            {healthy} products ({healthy*100//len(updates)}%)")

if __name__ == '__main__':
    main()
