import os
import certifi
import psycopg2

from app import NEON_PRODUCTS_DSN

def fix_ads():
    try:
        conn = psycopg2.connect(NEON_PRODUCTS_DSN)
        cur = conn.cursor()
        print("Connected.")
        
        cur.execute("UPDATE advertisements SET description = REPLACE(description, '$', '₹');")
        cur.execute("UPDATE advertisements SET title = REPLACE(title, '$', '₹');")
        conn.commit()
        
        print(f"Updated records. Rows affected: {cur.rowcount}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_ads()
