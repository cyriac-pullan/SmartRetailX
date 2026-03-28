import os, psycopg2, json
dsn = os.environ.get('NEON_DB_DSN', '')
with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'products'")
        cols = [r[0] for r in cur.fetchall()]
        with open('m:/Projects/MAJ FIN/backend/schema.json', 'w') as f:
            json.dump(cols, f)
