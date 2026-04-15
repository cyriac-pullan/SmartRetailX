import sqlite3

def check_partitions():
    try:
        conn = sqlite3.connect('smartretail.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check distinct partition_no values
        cur.execute("SELECT DISTINCT partition_no FROM products ORDER BY partition_no")
        rows = cur.fetchall()
        print("--- Existing Partitions in 'products' table ---")
        for row in rows:
            print(f"Partition: {row['partition_no']}")
            
        cur.execute("SELECT count(*) FROM products")
        count = cur.fetchone()[0]
        print(f"\nTotal products: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_partitions()
