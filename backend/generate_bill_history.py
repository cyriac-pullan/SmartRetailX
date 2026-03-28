"""
generate_bill_history.py
Clears all existing bills/transactions and seeds realistic data
from July 2025 → March 2026 across all customers.

Most-sold:  everyday staples (milk, bread, rice, tea, cooking oil, etc.)
Least-sold: niche/premium items (Starbucks instant, Toblerone, Ferrero Rocher, whey protein, baby formula, etc.)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, uuid, random, calendar
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

random.seed(99)

def get_conn():
    """Always return a fresh connection (NeonDB serverless can time out)."""
    return psycopg2.connect(NEON_DB_DSN,
                            connect_timeout=30,
                            cursor_factory=psycopg2.extras.RealDictCursor)


def run_sql(sql, params=None):
    """Execute a single statement with a fresh connection."""
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close()
    conn.close()

# ---------------------------------------------------------------------------
# PRODUCT WEIGHT CONFIG
# name fragments → how often picked (higher = more popular)
# ---------------------------------------------------------------------------
BESTSELLER_KEYWORDS  = [
    "Amul Taaza",        # milk
    "Amul Gold",         # milk
    "Mother Dairy Full Cream Milk",
    "Britannia 100% Whole Wheat Bread",
    "Modern Brown Bread",
    "Parle-G Glucose Biscuits 800g",
    "Tata Tea Gold",
    "Red Label Natural Care Tea",
    "Fortune Sunflower Oil 1L",
    "Saffola Gold Oil",
    "India Gate Basmati Rice Classic",
    "Aashirvaad Select Sharbati Atta 5kg",
    "Toor Dal 1kg",
    "Moong Dal Yellow Split",
    "Amul Pure Ghee 500ml",
    "Kissan Tomato Ketchup",
    "Nescafe Classic Instant Coffee 100g",
    "Maggi 2-Minute Noodles Masala 70g",
    "Colgate MaxFresh Toothpaste",
    "Lays Classic Salted 52g",
    "Kurkure Masala Munch",
    "Britannia Good Day Cashew",
    "Bisleri Mineral Water 1L",
    "Coca Cola 750ml",
    "Dairy Milk Silk",
    "Patanjali Cow Ghee",
    "Amul Masti Dahi",
    "Surf Excel Matic Liquid",
    "Harpic Power Plus",
    "Dove Beauty Cream Bar",
    "Head Shoulders",
    "Everest Turmeric Powder",
    "Tata Salt",
    "Haldirams Aloo Bhujia 200g",
    "Oreo Chocolate Sandwich",
    "Quaker Oats Rolled",
    "Kelloggs Corn Flakes",
    "Amul Salted Butter",
    "Dabur Honey 500g",
    "Britannia Marie Gold",
]

WORSTSELLER_KEYWORDS = [
    "Starbucks VIA",
    "Toblerone",
    "Ferrero Rocher",
    "MuscleBlaze Whey Active",
    "Nestle NanPro",             # infant formula - very specific need
    "Cerelac Stage",             # baby food
    "Borges Extra Virgin Olive Oil",  # expensive niche
    "Davidoff Rich Aroma",       # premium coffee
    "Lotus Biscoff",             # premium imported
    "Neutrogena Ultra Sheer",    # premium sunscreen
    "Cetaphil Gentle Skin",      # premium skincare
    "Pudin Hara Liquid",         # very specific
    "Starbucks",
    "Raw Pressery",
    "Mcvities Hobnobs",
    "Del Monte Pineapple Slices", # very specific canned
    "Catch Tuna in Brine",       # canned fish, niche
    "Ragu Tomato Sauce",
    "Kikkoman Soy Sauce",
    "Smucker Strawberry",
]

# ---------------------------------------------------------------------------

def ensure_bill_items_table(cur):
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


def assign_weight(name):
    """Return a pick-weight for a product: higher = more likely to be in a bill."""
    name_lower = name.lower()
    for kw in BESTSELLER_KEYWORDS:
        if kw.lower() in name_lower:
            return 30          # very high probability
    for kw in WORSTSELLER_KEYWORDS:
        if kw.lower() in name_lower:
            return 1           # very low probability
    return 8                   # normal everyday item


def random_datetime(year, month):
    """Random datetime within a calendar month, during store hours (8am–9pm)."""
    days = calendar.monthrange(year, month)[1]
    day    = random.randint(1, days)
    hour   = random.randint(8, 21)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(year, month, day, hour, minute, second)


def bills_for_month(year, month):
    """Number of bills to seed per month (ramp as the store gets more popular)."""
    base = {
        (2025, 7): 18,
        (2025, 8): 22,
        (2025, 9): 24,
        (2025,10): 28,
        (2025,11): 32,
        (2025,12): 38,
        (2026, 1): 42,
        (2026, 2): 40,
        (2026, 3): 30,   # March incomplete (up to today)
    }
    return base.get((year, month), 25)


def main():
    # ── Step 1: Ensure table exists ────────────────────────────────────────
    print("Ensuring bill_items table...")
    conn = get_conn()
    cur  = conn.cursor()
    ensure_bill_items_table(cur)
    conn.commit()
    cur.close()
    conn.close()

    # ── Step 2: Clear existing data (one table at a time, own connection) ──
    print("Clearing existing bill history...")
    for table in ["bill_items", "bills", "purchase_history", "billings"]:
        try:
            c = get_conn(); cu = c.cursor()
            cu.execute(f"DELETE FROM {table}")
            c.commit(); cu.close(); c.close()
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ⚠ Could not clear {table}: {e}")

    # ── Step 3: Load products (fresh connection) ───────────────────────────
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT product_id, barcode, name, price, weight_kg, category
        FROM products WHERE price > 0 ORDER BY product_id
    """)
    all_products = list(cur.fetchall())
    cur.execute("SELECT customer_id FROM customers ORDER BY created_at ASC")
    customers = [r['customer_id'] for r in cur.fetchall()] or ['CUST_DEFAULT']
    cur.close(); conn.close()

    if not all_products:
        print("No products found – aborting.")
        return
    print(f"  Loaded {len(all_products)} products, {len(customers)} customers.")

    product_weights = [assign_weight(p['name']) for p in all_products]
    payment_methods = ['cash', 'upi', 'card', 'upi', 'upi', 'cash']

    months = [
        (2025,7),(2025,8),(2025,9),(2025,10),
        (2025,11),(2025,12),(2026,1),(2026,2),(2026,3),
    ]

    total_bills = 0
    total_items = 0

    for (year, month) in months:
        bill_count = bills_for_month(year, month)
        print(f"\n  Seeding {bill_count} bills for {year}-{month:02d}...")

        # Fresh connection per month batch
        conn = get_conn()
        cur  = conn.cursor()
        month_bills = 0

        for _ in range(bill_count):
            created_at = random_datetime(year, month)
            if year == 2026 and month == 3 and created_at.day > 11:
                created_at = created_at.replace(day=random.randint(1, 11))

            customer_id    = random.choice(customers)
            payment_method = random.choice(payment_methods)

            n_items = random.randint(2, 8)
            chosen  = random.choices(all_products, weights=product_weights, k=n_items)
            seen, unique_items = set(), []
            for p in chosen:
                if p['barcode'] not in seen:
                    seen.add(p['barcode']); unique_items.append(p)

            item_details = []
            for p in unique_items:
                w   = assign_weight(p['name'])
                qty = random.choices([1,2,3,4], weights=[40,35,15,10])[0] if w >= 30 \
                      else random.choices([1,2,3], weights=[65,25,10])[0]
                item_details.append({
                    'product_id': p['product_id'],
                    'barcode':    p['barcode'],
                    'name':       p['name'],
                    'price':      float(p['price']),
                    'weight_kg':  float(p['weight_kg'] or 0),
                    'qty':        qty,
                })

            subtotal = round(sum(x['price']*x['qty'] for x in item_details), 2)
            tax      = round(subtotal * 0.05, 2)
            total    = round(subtotal + tax, 2)
            exp_wt   = round(sum(x['weight_kg']*x['qty'] for x in item_details), 3)

            ts_suffix = created_at.strftime('%Y%m%d_%H%M%S')
            bill_id   = f"BILL_{ts_suffix}_{uuid.uuid4().hex[:8]}"
            txn_id    = f"TXN_{ts_suffix}_{uuid.uuid4().hex[:8]}"

            cur.execute("""
                INSERT INTO bills (bill_id,customer_id,items_count,subtotal,tax,
                total_amount,expected_weight_kg,status,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'completed',%s)
                ON CONFLICT (bill_id) DO NOTHING
            """, (bill_id,customer_id,len(item_details),subtotal,tax,total,exp_wt,created_at))

            for it in item_details:
                cur.execute("""
                    INSERT INTO bill_items (bill_id,product_id,product_name,barcode,
                    quantity,unit_price,total_price) VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (bill_id,it['product_id'],it['name'],it['barcode'],
                      it['qty'],it['price'],round(it['price']*it['qty'],2)))

            for it in item_details:
                cur.execute("""
                    INSERT INTO purchase_history (customer_id,barcode,quantity,purchased_at)
                    VALUES (%s,%s,%s,%s)
                """, (customer_id,it['barcode'],it['qty'],created_at))

            cur.execute("""
                INSERT INTO billings (transaction_id,bill_id,customer_id,payment_method,amount,timestamp)
                VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (transaction_id) DO NOTHING
            """, (txn_id,bill_id,customer_id,payment_method,total,created_at))

            total_bills  += 1
            total_items  += len(item_details)
            month_bills  += 1

            # Commit every 5 bills to avoid long-held transactions
            if month_bills % 5 == 0:
                conn.commit()

        conn.commit()
        cur.close()
        conn.close()
        print(f"    ✓ {month_bills} bills committed for {year}-{month:02d}")

    print(f"\n✅ Done! {total_bills} bills, {total_items} line items seeded.")
    print(f"   Range: July 2025 – March 2026")
    print(f"   Bestsellers: everyday staples (milk, bread, rice, tea, oil...)")
    print(f"   Least sold:  niche/premium (Starbucks, Ferrero, whey protein...)")


if __name__ == '__main__':
    main()

