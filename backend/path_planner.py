import pandas as pd
import networkx as nx
import json
import heapq
from visualizer import StoreVisualizer

class GraphBuilder:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.graph = nx.Graph()
        self.partitions = {}
        self.node_coords = {}
        self.build_graph()

    def build_graph(self):
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
        matches = self.df[self.df['Product_Name'].str.contains(product_name, case=False, na=False)]
        if matches.empty: return None
        item = matches.iloc[0]
        return {
            'name': item['Product_Name'],
            'position': item['Position_Tag'],
            'aisle': item['Aisle_No'],
            'price': item['Price']
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


class MarketBasket:
    def __init__(self, rules_file):
        try:
            with open(rules_file, 'r') as f: self.rules = json.load(f)
        except: self.rules = {}

    def get_recommendations(self, product_name):
        recommendations = []
        for key, recs in self.rules.items():
            if key.lower() in product_name.lower():
                recommendations.extend(recs)
        return list(set(recommendations))


class PathFinder:
    def __init__(self, graph_builder, market_basket):
        self.gb = graph_builder
        self.mb = market_basket
        self.viz = StoreVisualizer(self.gb.node_coords)

    def get_path(self, start_position, target_product_name):
        target_info = self.gb.get_product_location(target_product_name)
        if not target_info: return None, "Product not found."
            
        target_pos = target_info['position']
        if start_position not in self.gb.graph: return None, f"Current {start_position} invalid."

        recs = self.mb.get_recommendations(target_info['name'])
        stops = [self.gb.get_product_location(r) for r in recs if self.gb.get_product_location(r)]
        
        best_rec = None
        min_total_dist = float('inf')
        
        # Optimization: Find best recommendation stop
        if stops:
            try:
                for stop in stops:
                    stop_pos = stop['position']
                    if stop_pos == target_pos: continue 
                    try:
                        d1 = nx.shortest_path_length(self.gb.graph, start_position, stop_pos)
                        d2 = nx.shortest_path_length(self.gb.graph, stop_pos, target_pos)
                        total = d1 + d2
                        
                        if total < min_total_dist:
                            min_total_dist = total
                            best_rec = stop
                    except: continue
            except: pass
        
        final_route = []
        
        if best_rec:
            p1 = nx.shortest_path(self.gb.graph, start_position, best_rec['position'])
            p2 = nx.shortest_path(self.gb.graph, best_rec['position'], target_pos)
            final_route = p1 + p2[1:]
            
            # GENERATE MAP
            try:
                self.viz.generate_map(final_route, start_position, target_pos, best_rec['position'])
            except Exception as e:
                print(f"Viz Error: {e}")
            
            return {
                "route": final_route,
                "target": target_info,
                "recommendation": best_rec
            }, "Path with Suggestion"
        else:
            final_route = nx.shortest_path(self.gb.graph, start_position, target_pos)
            
            # GENERATE MAP
            try:
                 self.viz.generate_map(final_route, start_position, target_pos, None)
            except Exception as e:
                print(f"Viz Error: {e}")
            
            return {
                "route": final_route,
                "target": target_info,
                "recommendation": None
            }, "Direct Path"
