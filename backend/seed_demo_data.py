"""
Seed demo bills and bill_items into Neon DB for dashboard demo.
Run once: python seed_demo_data.py
"""
import os, random, uuid
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

CUSTOMERS = ["CUST_A1B2", "CUST_C3D4", "CUST_E5F6", "22RA257", "ADMIN_001", "CUST_G7H8", "CUST_I9J0"]
CUSTOMER_NAMES = ["Arjun Sharma", "Priya Singh", "Mohit Kumar", "Deepak Verma", "Sneha Patel", "Rahul Gupta", "Anjali Roy"]

def get_conn():
    return psycopg2.connect(DSN, sslmode="require", connect_timeout=15)

def ensure_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id TEXT PRIMARY KEY,
            customer_id TEXT,
            total_amount REAL,
            status TEXT DEFAULT 'paid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id SERIAL PRIMARY KEY,
            bill_id TEXT REFERENCES bills(bill_id),
            barcode TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity INT,
            unit_price REAL,
            total_price REAL
        );
    """)

SAMPLE_PRODUCTS = [
    ("890100001",  "PROD00001", "Cinthol Body Wash 500g",        284.0),
    ("890100010",  "PROD00010", "Colgate Toothpaste 200g",       99.0),
    ("890100020",  "PROD00020", "Parle-G Biscuits 800g",         45.0),
    ("890100030",  "PROD00030", "Britannia Good Day Cashew",     60.0),
    ("890100050",  "PROD00050", "Amul Full Cream Milk 1L",       68.0),
    ("890100060",  "PROD00060", "Amul Butter 500g",              275.0),
    ("890100070",  "PROD00070", "Nestle KitKat 4 Finger",        50.0),
    ("890100080",  "PROD00080", "Cadbury Dairy Milk 50g",        55.0),
    ("890100090",  "PROD00090", "Lays Classic Salted 52g",       20.0),
    ("890100100",  "PROD00100", "Kurkure Masala Munch 90g",      20.0),
    ("8901000101", "PROD00101", "Tata Salt 1kg",                 28.0),
    ("8901000110", "PROD00110", "Aashirvaad Atta 5kg",           250.0),
    ("8901000120", "PROD00120", "India Gate Basmati Rice 5kg",   400.0),
    ("8901000130", "PROD00130", "Tata Tea Premium 500g",         220.0),
    ("8901000140", "PROD00140", "Nescafe Classic Coffee 50g",    180.0),
]

def main():
    print("Connecting to Neon DB...")
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    ensure_tables(cur)
    conn.commit()

    # Check existing count
    cur.execute("SELECT COUNT(*) FROM bills;")
    existing = cur.fetchone()[0]
    if existing >= 50:
        print(f"Already have {existing} bills - skipping seed.")
        conn.close()
        return

    print("Seeding 90 demo bills over last 30 days...")
    now = datetime.utcnow()
    bills_inserted = 0
    items_inserted = 0

    for day_offset in range(30):
        day = now - timedelta(days=day_offset)
        # 2-5 bills per day
        num_bills = random.randint(2, 5)
        for _ in range(num_bills):
            bill_id = "BILL_" + uuid.uuid4().hex[:12].upper()
            ci = random.randint(0, len(CUSTOMERS)-1)
            customer_id = CUSTOMERS[ci]

            # Pick 1-5 random items
            items = random.sample(SAMPLE_PRODUCTS, k=random.randint(1, 5))
            total = 0.0
            bill_items_data = []
            for barcode, prod_id, name, price in items:
                qty = random.randint(1, 3)
                line_total = round(price * qty, 2)
                total += line_total
                bill_items_data.append((bill_id, barcode, prod_id, name, qty, price, line_total))

            total = round(total, 2)
            bill_time = day.replace(
                hour=random.randint(9, 20),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0
            )

            cur.execute(
                "INSERT INTO bills (bill_id, customer_id, total_amount, status, created_at) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (bill_id, customer_id, total, "paid", bill_time)
            )
            psycopg2.extras.execute_values(cur,
                "INSERT INTO bill_items (bill_id, barcode, product_id, product_name, quantity, unit_price, total_price) VALUES %s ON CONFLICT DO NOTHING",
                bill_items_data
            )
            bills_inserted += 1
            items_inserted += len(bill_items_data)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM bills;")
    cur.execute("SELECT COALESCE(SUM(total_amount),0) FROM bills;")
    total_rev = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bills;")
    total_bills = cur.fetchone()[0]
    print(f"Done! Inserted {bills_inserted} bills, {items_inserted} items")
    print(f"DB now has {total_bills} bills, total revenue Rs.{total_rev:,.0f}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
