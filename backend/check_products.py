"""Check what products exist in the DB for biryani ingredients — output to file."""
import sys
import os
sys.path.insert(0, r"m:\Projects\MAJ FIN LAT\MAJ FIN\backend")
import psycopg2
import psycopg2.extras

NEON_DB_DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

terms = [
    "Chicken", "Basmati", "Rice", "Yogurt", "Curd", "Ghee", "Onion", "Mint",
    "Saffron", "Ginger", "Garlic", "Tomato", "Spice", "Paneer", "Dal", "Lentil",
    "Butter", "Cream", "Bread", "Egg", "Potato", "Pea", "Cauliflower", "Mutton",
    "Lamb", "Fish", "Prawn", "Semolina", "Atta", "Flour", "Salt", "Oil",
    "Sugar", "Milk", "Coconut", "Cardamom", "Pepper", "Cheese", "Cashew",
    "Pasta", "Noodle", "Soy", "Ketchup", "Mayo", "Honey", "Raisin",
]

conn = psycopg2.connect(NEON_DB_DSN, sslmode="require")
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

lines = []
for term in terms:
    for table in ["products", "products2"]:
        cur.execute(f"SELECT name FROM {table} WHERE LOWER(name) LIKE LOWER(%s) ORDER BY name LIMIT 4", (f'%{term}%',))
        rows = cur.fetchall()
        if rows:
            names = [r['name'] for r in rows]
            lines.append(f"[{table}] '{term}': {names}")

cur.close()
conn.close()

result = "\n".join(lines)
print(result)
open(r"m:\Projects\MAJ FIN LAT\MAJ FIN\backend\product_check.txt", "w", encoding="utf-8").write(result)
print("\nDone - written to product_check.txt")
