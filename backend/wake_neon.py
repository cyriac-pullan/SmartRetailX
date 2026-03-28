import psycopg2, time, sys
DSN = "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
for i in range(5):
    try:
        conn = psycopg2.connect(DSN, connect_timeout=15)
        cur = conn.cursor()
        cur.execute('SELECT version();')
        print('✅ Connected –', cur.fetchone()[0])
        cur.close()
        conn.close()
        sys.exit(0)
    except Exception as e:
        print(f'Attempt {i+1} failed: {e}')
        time.sleep(5)
print('❌ All attempts failed')
