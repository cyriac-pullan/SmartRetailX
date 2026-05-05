import psycopg2, random

DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
conn = psycopg2.connect(DSN, sslmode="require", connect_timeout=10)
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)

# Find ads table
ads_table = next((t for t in tables if 'ad' in t.lower()), None)
print("Ads table:", ads_table)

if ads_table:
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{ads_table}' ORDER BY ordinal_position")
    cols = [r[0] for r in cur.fetchall()]
    print("Columns:", cols)
    cur.execute(f"SELECT * FROM {ads_table} LIMIT 2")
    all_cols = [d[0] for d in cur.description]
    for r in cur.fetchall():
        d = dict(zip(all_cols, r))
        print("Row:", {k: d[k] for k in ['ad_id' if 'ad_id' in d else all_cols[0], 'impressions' if 'impressions' in d else all_cols[1], 'revenue_per_impression' if 'revenue_per_impression' in d else all_cols[2]]})

conn.close()
