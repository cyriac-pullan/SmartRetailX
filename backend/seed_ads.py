import psycopg2, random, sys
from datetime import datetime, timedelta

DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
conn = psycopg2.connect(DSN, sslmode="require", connect_timeout=10)
cur = conn.cursor()
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Check current state
cur.execute("SELECT COUNT(*) FROM ad_impressions")
imp_count = cur.fetchone()[0]
cur.execute("SELECT ad_id FROM advertisements")
ad_ids = [r[0] for r in cur.fetchall()]
print(f"Ads: {len(ad_ids)}, existing impressions: {imp_count}")

# Seed ad_impressions
if imp_count < 200:
    print("Seeding ad impressions...")
    inserted = 0
    for ad_id in ad_ids:
        for _ in range(random.randint(30, 150)):
            days_ago = random.randint(0, 30)
            shown_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0,23))
            rev = round(random.uniform(0.5, 5.0), 2)
            cur.execute(
                "INSERT INTO ad_impressions (ad_id, customer_id, position_tag, aisle, shown_at, revenue_earned) VALUES (%s,%s,%s,%s,%s,%s)",
                (ad_id, f"CUST_{random.randint(1000,9999)}", f"P{random.randint(101,136):03d}",
                 random.randint(1,3), shown_at, rev)
            )
            inserted += 1
    conn.commit()
    print(f"Inserted {inserted} impression rows")

# Update revenue_per_impression on advertisements
print("Updating revenue_per_impression on advertisements...")
cur.execute("""
    UPDATE advertisements SET revenue_per_impression = sub.avg_rev
    FROM (
        SELECT ad_id, ROUND(AVG(revenue_earned)::numeric, 2) as avg_rev
        FROM ad_impressions GROUP BY ad_id
    ) sub
    WHERE advertisements.ad_id = sub.ad_id
""")
conn.commit()
print(f"Updated {cur.rowcount} ads")

# Verify
cur.execute("""
    SELECT a.ad_id, a.title[:30], a.revenue_per_impression, COUNT(i.id) as impressions
    FROM advertisements a
    LEFT JOIN ad_impressions i ON a.ad_id = i.ad_id
    GROUP BY a.ad_id, a.title, a.revenue_per_impression
    LIMIT 5
""")
print("\nSample ads after seed:")
for r in cur.fetchall():
    print(f"  ID:{r[0]} title:{r[1]} rev:{r[2]} impressions:{r[3]}")

cur.close()
conn.close()
print("Done!")
