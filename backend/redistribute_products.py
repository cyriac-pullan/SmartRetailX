import sqlite3

def redistribute():
    try:
        conn = sqlite3.connect('smartretail.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get all products
        cur.execute("SELECT product_id, name FROM products")
        products = cur.fetchall()
        
        if not products:
            print("No products found in database.")
            return

        print(f"Found {len(products)} products. Mapping to partitions 101-136...")
        
        # Corridors mapping for logic
        # L: 101-106 (Aisle 1 Left)
        # 12: 107-112 (A1R), 113-118 (A2L)
        # 23: 119-124 (A2R), 125-130 (A3L)
        # R: 131-136 (A3R)
        
        # We'll just loop through and assign sequentially to fill the space
        partitions = list(range(101, 137)) # 101 to 136
        
        for i, product in enumerate(products):
            # Use modulo to wrap around if more than 36 products
            p_no = partitions[i % len(partitions)]
            
            # Determine aisle and side for metadata consistency
            # Mapping based on LiveNavigationModal.jsx logic
            aisle_no = 0
            side = ""
            if 101 <= p_no <= 112: 
                aisle_no = 1
                side = "Left" if p_no <= 106 else "Right"
            elif 113 <= p_no <= 124: 
                aisle_no = 2
                side = "Left" if p_no <= 118 else "Right"
            elif 125 <= p_no <= 136: 
                aisle_no = 3
                side = "Left" if p_no <= 130 else "Right"
            
            pos_tag = f"P{p_no}"
            
            cur.execute("""
                UPDATE products 
                SET partition_no = ?, aisle = ?, side = ?, position_tag = ?
                WHERE product_id = ?
            """, (p_no, aisle_no, side, pos_tag, product['product_id']))
            
        conn.commit()
        print("✅ Redistribution complete! Products are now spread across all partitions.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    redistribute()
