import os
import psycopg2
from psycopg2.extras import DictCursor
import random

NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def populate_ads():
    try:
        conn = psycopg2.connect(NEON_DB_DSN)
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # 1. Ensure tables exist
        print("Ensuring ad tables exist...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS advertisements (
                ad_id SERIAL PRIMARY KEY,
                product_id VARCHAR,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                position_tag VARCHAR(20),
                aisle INT,
                is_compulsory BOOLEAN DEFAULT FALSE,
                priority INT DEFAULT 0,
                revenue_per_impression NUMERIC(10,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS ad_impressions (
                id SERIAL PRIMARY KEY,
                ad_id INT REFERENCES advertisements(ad_id) ON DELETE CASCADE,
                customer_id VARCHAR,
                position_tag VARCHAR(20),
                aisle INT,
                shown_at TIMESTAMP DEFAULT NOW(),
                revenue_earned NUMERIC(10,2) DEFAULT 0
            );
        """)
        conn.commit()

        # 2. Clear existing ads (Optional, for clean state)
        print("Clearing existing advertisements...")
        cur.execute("DELETE FROM ad_impressions;")
        cur.execute("DELETE FROM advertisements;")
        conn.commit()
        
        # 3. Fetch products from the main table
        print("Fetching products from DB...")
        cur.execute("""
            SELECT product_id, barcode, name, price, category, aisle, position_tag 
            FROM products 
            WHERE position_tag IS NOT NULL
        """)
        products = cur.fetchall()
        
        # Also check products2 as fallback if needed to get more products
        cur.execute("""
            SELECT product_id, barcode, name, price, category, aisle, position_tag 
            FROM products2 
            WHERE position_tag IS NOT NULL
        """)
        products2 = cur.fetchall()
        
        # Combine and deduplicate by barcode
        all_products = {}
        for p in products + products2:
            all_products[p['barcode']] = p
            
        print(f"Total unique products found with position tags: {len(all_products)}")
        
        # Group products by partition (position_tag)
        partition_products = {}
        for p in all_products.values():
            ptag = p['position_tag']
            if ptag not in partition_products:
                partition_products[ptag] = []
            partition_products[ptag].append(p)
            
        print(f"Found {len(partition_products)} different partitions.")
        
        ads_to_insert = []
        
        # Generate up to 5 ads per partition
        for ptag, prods in partition_products.items():
            # Shuffle and pick up to 5 mapped to this partition
            # Note: if there are fewer than 5 products in this partition in the DB, it will just use all of them.
            # To strictly get 5 ads per partition even if short on products for that specific partition, 
            # we can pull random products from other partitions, but it's better to stick to the partition's actual products for relevance.
            # However, if user explicitly asked for 180 total, we might need to pad it.
            # Let's see how many we have first.
            selected = random.sample(prods, min(5, len(prods)))
            
            # Pad with random products if this partition has < 5 products
            if len(selected) < 5:
                needed = 5 - len(selected)
                available_for_padding = [p for p in all_products.values() if p not in selected]
                if needed <= len(available_for_padding):
                    selected.extend(random.sample(available_for_padding, needed))
            
            for p in selected:
                title = f"Exclusive: {p['name']}"
                desc = f"Special price for {p['name']} at just ₹{p['price']}."
                image_url = "" # None available in schema by default
                
                # ~10% chance to make compulsory
                is_compulsory = random.random() < 0.10
                priority = random.randint(1, 5)
                # Ensure compulsory ads have top priority
                if is_compulsory:
                    priority = 5
                
                revenue = round(random.uniform(0.10, 2.50), 2)
                aisle = p.get('aisle', 0)
                
                ads_to_insert.append((
                    p['product_id'], title, desc, image_url, ptag, aisle, 
                    is_compulsory, priority, revenue
                ))
                
        print(f"Generated {len(ads_to_insert)} advertisements to insert.")
        
        if ads_to_insert:
            cur.executemany("""
                INSERT INTO advertisements (
                    product_id, title, description, image_url, position_tag, 
                    aisle, is_compulsory, priority, revenue_per_impression
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ads_to_insert)
            conn.commit()
            print("Successfully inserted ads into database!")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    populate_ads()
