import os, uuid, random, calendar
from datetime import datetime
import psycopg2
import psycopg2.extras

NEON_DB_DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def main():
    conn = psycopg2.connect(NEON_DB_DSN, cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()

    print("Wiping corrupted historical data...")
    cur.execute("TRUNCATE TABLE bills, bill_items, purchase_history, billings RESTART IDENTITY CASCADE;")
    
    print("Fetching remaining 1000 products...")
    cur.execute("SELECT product_id, barcode, name, price, weight_kg, category FROM products LIMIT 500;")
    p1 = cur.fetchall()
    
    cur.execute("SELECT product_id, barcode, name, price, weight_kg, category FROM products2 LIMIT 500;")
    p2 = cur.fetchall()
    
    products = p1 + p2
    
    cur.execute("SELECT customer_id FROM customers ORDER BY created_at ASC LIMIT 1")
    row = cur.fetchone()
    default_customer = row['customer_id'] if row else 'CUST_SEED'
    
    months = [
        (2025, 12, 10),   # Dec 2025: 10 bills
        (2026, 1, 15),    # Jan 2026: 15 bills
        (2026, 2, 20),    # Feb 2026: 20 bills
        (2026, 3, 20),    # Mar 2026: 20 bills
    ]

    total_bills = 0

    for (year, month, bill_count) in months:
        days_in_month = calendar.monthrange(year, month)[1]
        if year == 2026 and month == 3:
            days_in_month = min(days_in_month, datetime.now().day)
            
        for i in range(bill_count):
            day    = random.randint(1, max(1, days_in_month))
            hour   = random.randint(8, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            created_at = datetime(year, month, day, hour, minute, second)

            n_items = random.randint(2, 6)
            items_chosen = random.sample(products, min(n_items, len(products)))

            item_details = []
            for p in items_chosen:
                qty = random.randint(1, 4)
                item_details.append({
                    'product_id': p['product_id'],
                    'barcode':    p['barcode'],
                    'name':       p['name'],
                    'price':      float(p['price'] or 0),
                    'weight_kg':  float(p['weight_kg'] or 0),
                    'qty':        qty
                })

            subtotal = round(sum(x['price'] * x['qty'] for x in item_details), 2)
            tax      = round(subtotal * 0.05, 2)
            total    = round(subtotal + tax, 2)
            expected_weight = round(sum(x['weight_kg'] * x['qty'] for x in item_details), 3)

            ts_suffix = created_at.strftime('%Y%m%d_%H%M%S')
            bill_id   = f"BILL_{ts_suffix}_{uuid.uuid4().hex[:8]}"

            cur.execute("""
                INSERT INTO bills
                    (bill_id, customer_id, items_count, subtotal, tax, total_amount,
                     expected_weight_kg, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', %s)
            """, (
                bill_id, default_customer, len(item_details),
                subtotal, tax, total, expected_weight, created_at
            ))

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

            for it in item_details:
                cur.execute("""
                    INSERT INTO purchase_history
                        (customer_id, barcode, quantity, purchased_at)
                    VALUES (%s, %s, %s, %s)
                """, (default_customer, it['barcode'], it['qty'], created_at))

            txn_id = f"TXN_{ts_suffix}_{uuid.uuid4().hex[:8]}"
            cur.execute("""
                INSERT INTO billings
                    (transaction_id, bill_id, customer_id, payment_method, amount, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (txn_id, bill_id, default_customer, 'cash', total, created_at))

            total_bills += 1

    print("Forcing 10 products to stock quantity 0 for Restock UI feature...")
    zero_stock_items = random.sample(products, 10)
    for p in zero_stock_items:
        cur.execute("UPDATE products SET stock_quantity = 0 WHERE barcode = %s", (p['barcode'],))
        cur.execute("UPDATE products2 SET stock_quantity = 0 WHERE barcode = %s", (p['barcode'],))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully wiped and reseeded {total_bills} bills for {len(products)} products.")

if __name__ == '__main__':
    main()
