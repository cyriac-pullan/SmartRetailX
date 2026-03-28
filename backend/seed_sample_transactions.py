"""
seed_sample_transactions.py
Run once to insert realistic sample bills/bill_items for Dec 2025, Jan 2026, Feb 2026
so the admin sales chart shows data for those months.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, uuid, random, calendar
from datetime import datetime
import psycopg2
import psycopg2.extras

NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def get_conn():
    return psycopg2.connect(NEON_DB_DSN, cursor_factory=psycopg2.extras.RealDictCursor)

def ensure_bill_items_table(cur):
    """Create bill_items table if it doesn't already exist."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id SERIAL PRIMARY KEY,
            bill_id TEXT NOT NULL,
            product_id TEXT,
            product_name TEXT,
            barcode TEXT,
            quantity INT NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_bill_items_bill ON bill_items(bill_id);
        CREATE INDEX IF NOT EXISTS idx_bill_items_barcode ON bill_items(barcode);
    """)

def main():
    conn = get_conn()
    cur = conn.cursor()

    # Ensure bill_items table exists
    ensure_bill_items_table(cur)
    conn.commit()
    print("bill_items table ensured.")

    # ── Fetch real product data ──────────────────────────────────────────────
    cur.execute("""
        SELECT product_id, barcode, name, price, weight_kg, category
        FROM products
        WHERE price > 0
        ORDER BY RANDOM()
        LIMIT 50
    """)
    products = list(cur.fetchall())

    if not products:
        print("No products found – aborting.")
        conn.close()
        return

    print(f"Loaded {len(products)} products.")

    # Use the first customer
    cur.execute("SELECT customer_id FROM customers ORDER BY created_at ASC LIMIT 1")
    row = cur.fetchone()
    default_customer = row['customer_id'] if row else 'CUST_SEED'
    print(f"Using customer: {default_customer}")

    # ── Month ranges to seed ─────────────────────────────────────────────────
    months = [
        (2025, 12, 18),   # December 2025 – 18 bills
        (2026,  1, 20),   # January  2026 – 20 bills
        (2026,  2, 16),   # February 2026 – 16 bills
    ]

    total_bills = 0

    for (year, month, bill_count) in months:
        days_in_month = calendar.monthrange(year, month)[1]
        print(f"\nInserting {bill_count} bills for {year}-{month:02d}...")

        for i in range(bill_count):
            day    = random.randint(1, days_in_month)
            hour   = random.randint(8, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created_at = datetime(year, month, day, hour, minute, second)

            # Pick 2-5 random products
            n_items = random.randint(2, 5)
            items_chosen = random.sample(products, min(n_items, len(products)))

            item_details = []
            for p in items_chosen:
                qty = random.randint(1, 3)
                item_details.append({
                    'product_id': p['product_id'],
                    'barcode':    p['barcode'],
                    'name':       p['name'],
                    'price':      float(p['price']),
                    'weight_kg':  float(p['weight_kg'] or 0),
                    'qty':        qty
                })

            subtotal = round(sum(x['price'] * x['qty'] for x in item_details), 2)
            tax      = round(subtotal * 0.05, 2)
            total    = round(subtotal + tax, 2)
            expected_weight = round(sum(x['weight_kg'] * x['qty'] for x in item_details), 3)

            ts_suffix = created_at.strftime('%Y%m%d_%H%M%S')
            bill_id   = f"BILL_{ts_suffix}_{uuid.uuid4().hex[:8]}"

            # ── Insert bill ──────────────────────────────────────────────────
            cur.execute("""
                INSERT INTO bills
                    (bill_id, customer_id, items_count, subtotal, tax, total_amount,
                     expected_weight_kg, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', %s)
                ON CONFLICT (bill_id) DO NOTHING
            """, (
                bill_id, default_customer, len(item_details),
                subtotal, tax, total, expected_weight, created_at
            ))

            # ── Insert bill_items ────────────────────────────────────────────
            for it in item_details:
                cur.execute("""
                    INSERT INTO bill_items
                        (bill_id, product_id, product_name, barcode, quantity,
                         unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    bill_id, it['product_id'], it['name'], it['barcode'],
                    it['qty'], it['price'], round(it['price'] * it['qty'], 2)
                ))

            # ── Insert purchase_history ──────────────────────────────────────
            for it in item_details:
                cur.execute("""
                    INSERT INTO purchase_history
                        (customer_id, barcode, quantity, purchased_at)
                    VALUES (%s, %s, %s, %s)
                """, (default_customer, it['barcode'], it['qty'], created_at))

            # ── Insert billings (transaction record) ─────────────────────────
            txn_id = f"TXN_{ts_suffix}_{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO billings
                    (transaction_id, bill_id, customer_id, payment_method, amount, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
            """, (txn_id, bill_id, default_customer, 'cash', total, created_at))

            total_bills += 1

            # Commit every 10 bills to avoid large transactions
            if total_bills % 10 == 0:
                conn.commit()
                print(f"  Committed {total_bills} bills so far...")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nDone! Inserted {total_bills} sample bills across Dec 2025, Jan 2026, Feb 2026.")

if __name__ == '__main__':
    main()
