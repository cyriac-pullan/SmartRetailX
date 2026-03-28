import sqlite3
import networkx as nx
import pandas as pd
import json

class DBGraphBuilder:
    def __init__(self, db_path):
        self.db_path = db_path
        self.graph = nx.Graph()
        self.partitions = {}
        self.node_coords = {}
        self.df = self.load_products_from_db()
        self.build_graph()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def load_products_from_db(self):
        """Load minimal product data needed for navigation into a DataFrame"""
        query = """
        SELECT 
            product_id, 
            name as Product_Name, 
            price as Price, 
            aisle as Aisle_No, 
            position_tag as Position_Tag,
            category as Category
        FROM products
        WHERE position_tag IS NOT NULL
        """
        try:
            conn = self.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            # Ensure Aisle_No is int
            df['Aisle_No'] = df['Aisle_No'].fillna(0).astype(int)
            return df
        except Exception as e:
            print(f"Error loading products from DB: {e}")
            return pd.DataFrame()

    def build_graph(self):
        if self.df.empty:
            print("Warning: No products found in DB to build graph.")
            return

        # 1. Map Position Tags to Coordinates (Rough Estimate)
        unique_positions = self.df.groupby('Position_Tag').agg({
            'Aisle_No': 'first'
        }).reset_index().sort_values(by=['Aisle_No', 'Position_Tag'])
        
        self.partitions_list = unique_positions['Position_Tag'].tolist()
        
        # Group partitions per aisle to distribute 'Y' coordinates
        aisle_groups = unique_positions.groupby('Aisle_No')
        
        for aisle, group in aisle_groups:
            # Sort partitions in this aisle
            sorted_parts = sorted(group['Position_Tag'].tolist())
            count = len(sorted_parts)
            
            # Base X for this aisle
            base_x = 3 + (aisle - 1) * 4
            
            # Distribute Y from 2 to 12
            for i, p_tag in enumerate(sorted_parts):
                y_step = 10 / max(count, 1)
                y_pos = 2 + (i * y_step)
                self.node_coords[p_tag] = (base_x, y_pos)
                self.graph.add_node(p_tag, pos=(base_x, y_pos), aisle=aisle)

        # 2. Add Intra-Aisle Edges
        for aisle, group in aisle_groups:
            sorted_parts = sorted(group['Position_Tag'].tolist())
            for i in range(len(sorted_parts) - 1):
                u = sorted_parts[i]
                v = sorted_parts[i+1]
                self.graph.add_edge(u, v, weight=1)

        # 3. Add Inter-Aisle Edges (Snake/Zig-Zag Pattern)
        aisles = sorted(aisle_groups.groups.keys())
        for i in range(len(aisles) - 1):
            curr_a = aisles[i]
            next_a = aisles[i+1]
            
            curr_parts = sorted(aisle_groups.get_group(curr_a)['Position_Tag'].tolist())
            next_parts = sorted(aisle_groups.get_group(next_a)['Position_Tag'].tolist())
            
            if not curr_parts or not next_parts: continue

            # Zig-Zag Logic: Connect Top-Top or Bottom-Bottom alternating
            if i % 2 == 0:
                u = curr_parts[-1]
                v = next_parts[-1]
            else:
                u = curr_parts[0]
                v = next_parts[0]
                
            self.graph.add_edge(u, v, weight=3)


    def get_product_location(self, product_name):
        # 1. Exact or full-substring match
        matches = self.df[self.df['Product_Name'].str.contains(product_name, case=False, na=False)]
        
        # 2. Reverse substring match (e.g. NeonDB "Product 1kg" contains SQLite "Product")
        if matches.empty:
            pn_lower = product_name.lower()
            matches = self.df[self.df['Product_Name'].apply(lambda n: str(n).lower() in pn_lower)]
            
        # 3. Keyword match fallback
        if matches.empty:
            ignore = {'and', 'the', 'with', 'for', 'pack', 'size', 'attr'}
            kw = {w.lower() for w in product_name.replace('-', ' ').split() if len(w) > 3 and w.lower() not in ignore}
            if kw:
                scores = self.df['Product_Name'].apply(lambda n: sum(1 for w in kw if w in str(n).lower()))
                best_score = scores.max()
                if best_score > 0:
                    matches = self.df[scores == best_score]

        if matches.empty: return None
        item = matches.iloc[0]
        return {
            'name': item['Product_Name'],
            'position': item['Position_Tag'],
            'aisle': int(item['Aisle_No']), # Ensure serializable
            'price': float(item['Price'])
        }
    
    def get_partitions_by_aisle(self):
        unique_positions = self.df.groupby('Position_Tag').agg({
            'Aisle_No': 'first'
        }).reset_index()
        
        partitions = {}
        for _, row in unique_positions.iterrows():
            aisle = int(row['Aisle_No'])
            if aisle not in partitions: partitions[aisle] = []
            partitions[aisle].append(row['Position_Tag'])
        # Sort
        for k in partitions:
            partitions[k].sort()
        return partitions


class DBMarketBasket:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_recommendations(self, product_name):
        """
        Fetch recommendations from DB. 
        Since DB links barcodes, we first find the barcode for the product name,
        then find linked barcodes, then their names.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Get barcode for the product name
        cursor.execute("SELECT barcode FROM products WHERE name LIKE ? LIMIT 1", (f"%{product_name}%",))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return []
        
        input_barcode = row['barcode']
        
        # 2. Get recommended barcodes from 'recommendations' table (bidirectional check)
        # Table structure likely: product_barcode, recommended_product_barcode, ...
        # Based on create_db.py: product_barcode, recommended_product_barcode, co_occurrence_count
        
        recs = []
        
        # Forward
        cursor.execute("""
            SELECT recommended_product_barcode FROM recommendations 
            WHERE product_barcode = ? 
            ORDER BY co_occurrence_count DESC LIMIT 3
        """, (input_barcode,))
        recs.extend([r[0] for r in cursor.fetchall()])
        
        # Reverse (if not enough)
        cursor.execute("""
            SELECT product_barcode FROM recommendations 
            WHERE recommended_product_barcode = ? 
            ORDER BY co_occurrence_count DESC LIMIT 3
        """, (input_barcode,))
        recs.extend([r[0] for r in cursor.fetchall()])
        
        if not recs:
            conn.close()
            return []
            
        # 3. Get names for these barcodes
        placeholders = ','.join(['?'] * len(recs))
        query = f"SELECT name FROM products WHERE barcode IN ({placeholders})"
        cursor.execute(query, recs)
        
        names = [r['name'] for r in cursor.fetchall()]
        conn.close()
        
        return list(set(names))
