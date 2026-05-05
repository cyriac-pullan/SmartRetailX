import asyncio
import threading
import time
import json
import os
import random
from bleak import BleakScanner
from path_planner import GraphBuilder, MarketBasket, PathFinder
from visualizer import StoreVisualizer
from esp32_tracker import IndoorPositioning

import os
# Config
CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "products_unique_remapped.csv")
ASSOCIATIONS_FILE = "associations.json"
CALIBRATION_FILE = "calibration_config.json"
ESP_CORRIDORS = {"ESP32_AISLE_1": "L", "ESP32_AISLE_2": "12", "ESP32_AISLE_3": "23", "ESP32_AISLE_4": "R"}

class SmartCartService:
    def __init__(self):
        self.lock = threading.Lock()
        
        # State
        self.current_location = {"aisle": None, "partition": None, "esp": None}
        self.last_ad = None
        self.is_scanning = False
        self.calibration_mode = None  # {target: "ESP1", type: "min"/"max"}
        
        # Modules
        self.gb = GraphBuilder(CSV_FILE)
        self.mb = MarketBasket(ASSOCIATIONS_FILE)
        self.pf = PathFinder(self.gb, self.mb)
        
        # Override Visualizer to output to static web folder
        # We need to access the inner Viz object of PathFinder 
        if not os.path.exists("static"):
            os.makedirs("static")
        self.pf.viz.output_path = "static/navigation_map.png"
        
        # Calibration
        self.rssi_config = {}
        self.load_calibration()
        
        # Advanced ESP32 Tracker Engine
        self.tracker = IndoorPositioning(walkway_length_m=1.5)
        
        # Thread control
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def load_calibration(self):
        if os.path.exists(CALIBRATION_FILE):
             try:
                 with open(CALIBRATION_FILE, 'r') as f:
                     self.rssi_config = json.load(f)
             except: pass

    def save_calibration(self):
        try:
             with open(CALIBRATION_FILE, 'w') as f:
                 json.dump(self.rssi_config, f, indent=4)
        except: pass

    def trigger_calibration(self, esp_name, measure_type):
        """
        measure_type: 'max_rssi' (Near) or 'min_rssi' (Far)
        """
        with self.lock:
            self.calibration_mode = {"target": esp_name, "type": measure_type}

    def search_product(self, query):
        with self.lock:
            start = self.current_location["partition"]
            if not start:
                return {"error": "Location unknown. Please wait for scan."}
            
            result, msg = self.pf.get_path(start, query)
            if not result:
                return {"error": msg}
                
            rec_node = None
            if result.get('recommendation'):
                rec_node = result['recommendation'].get('position')
                
            return {
                "success": True, 
                "target": result['target']['name'] if isinstance(result['target'], dict) else result['target'], 
                "target_node": result['target'].get('position') if isinstance(result['target'], dict) else None,
                "recommendation": result['recommendation']['name'] if isinstance(result['recommendation'], dict) else result['recommendation'],
                "recommendation_node": rec_node,
                "route": result['route']
            }

    def get_status(self):
        with self.lock:
            return {
                "location": self.current_location,
                "ad": self.last_ad,
                "calibration": self.rssi_config
            }

    def get_map_data(self):
        """
        Return graph nodes, edges, and other static data for frontend rendering.
        """
        with self.lock:
            # 1. Nodes
            nodes = {}
            for node, data in self.gb.graph.nodes(data=True):
                # data contains 'pos'=(x,y), 'aisle'=...
                nodes[node] = {
                    "x": data['pos'][0],
                    "y": data['pos'][1],
                    "aisle": data.get('aisle')
                }
            
            # 2. Edges
            edges = []
            for u, v in self.gb.graph.edges():
                edges.append((u, v))

            # 3. Aisle Metadata (Hardcoded for now, same as Visualizer)
            # (id, name, x_start, y_start, color)
            aisles = [
                {"id": 1, "name": "Aisle 1", "x": 2, "y": 2, "color": "red", "width": 2, "height": 10},
                {"id": 2, "name": "Aisle 2", "x": 6, "y": 2, "color": "orange", "width": 2, "height": 10},
                {"id": 3, "name": "Aisle 3", "x": 10, "y": 2, "color": "blue", "width": 2, "height": 10},
            ]

            # Generate Partition Nodes precisely along the aisle height
            # Height = 10 units mapping to 6 meters. So 10/6 interval splits.
            # 6 partitions: P101(Start) to P106(End)
            partition_names = []
            for aisle in aisles:
                for i in range(1, 7): # 1 to 6
                    node_name = f"Aisle {aisle['id_val'] if 'id_val' in aisle else aisle['id']} - P10{i}" # e.g. Aisle 1 - P101
                    partition_names.append(node_name)
                    
                    # Calculate Y offset scaling perfectly 
                    y_offset = (i - 0.5) * (aisle['height'] / 6)
                    nodes[node_name] = {"x": aisle['x'] + aisle['width']/2, "y": aisle['y'] + y_offset}
                    
                    # Connect partition to previous partition inline
                    if i > 1:
                        prev_node = f"Aisle {aisle['id']} - P10{i-1}"
                        edges.append((prev_node, node_name))
            
            # Connect the Entry to the first partition of each aisle
            for aisle in aisles:
                edges.append(("Entry", f"Aisle {aisle['id']} - P101"))

            return {
                "nodes": nodes,
                "edges": edges,
                "aisles": aisles
            }

    def _estimate_partition(self, rssi, corridor_id):
        # Find which ESP serves this corridor
        esp_name = None
        for name, corr in ESP_CORRIDORS.items():
            if corr == corridor_id:
                esp_name = name
                break
        if not esp_name:
            esp_name = f"ESP32_AISLE_{corridor_id}"
        max_rssi = -30
        min_rssi = -90
        
        if esp_name in self.rssi_config:
            max_rssi = self.rssi_config[esp_name].get("max_rssi", -30)
            min_rssi = self.rssi_config[esp_name].get("min_rssi", -90)
            
        # Standardize normalization bounds mapping linearly to distance
        normalized = min(max(rssi, min_rssi), max_rssi) 
        if max_rssi == min_rssi: strength = 0.5
        else: strength = (normalized - min_rssi) / (max_rssi - min_rssi)
        
        # Map to corridor partitions
        CORRIDOR_PARTS = {
            "L":  list(range(101, 107)),
            "12": list(range(107, 119)),
            "23": list(range(119, 131)),
            "R":  list(range(131, 137)),
        }
        parts = CORRIDOR_PARTS.get(corridor_id, list(range(101, 107)))
        index = min(int(strength * len(parts)), len(parts) - 1)
        return f"P{parts[index]}"

    def _run_async_loop(self):
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        print("Backend Service Started")
        while not self.stop_event.is_set():
            try:
                # 1. Calibration Mode Priority
                calib_target = None
                with self.lock:
                    if self.calibration_mode:
                        calib_target = self.calibration_mode
                        self.calibration_mode = None # Convert to local task
                
                if calib_target:
                    print(f"Calibrating {calib_target['target']}...")
                    val = await self._scan_average(calib_target['target'], 5)
                    if val:
                        with self.lock:
                            if calib_target['target'] not in self.rssi_config:
                                self.rssi_config[calib_target['target']] = {}
                            self.rssi_config[calib_target['target']][calib_target['type']] = val
                        self.save_calibration()
                    continue

                # 2. Normal Scan Mode
                rssi_data = {name: [] for name in ESP_CORRIDORS}
                def callback(device, advertisement_data):
                     if device.name in ESP_CORRIDORS and advertisement_data.rssi > -95:
                         rssi_data[device.name].append(advertisement_data.rssi)
                
                scanner = BleakScanner(callback)
                await scanner.start()
                await asyncio.sleep(2)
                await scanner.stop()
                
                # Process
                medians = {}
                for name, vals in rssi_data.items():
                    if vals: medians[name] = sorted(vals)[len(vals)//2]
                
                if medians:
                    location_data = self.tracker.update_rssi(medians)
                    if location_data:
                        partition = location_data['partition']
                        corridor_id = location_data['corridor']
                        best_name = location_data['esp']
                        best_rssi = location_data['raw_rssi']
                        distance = location_data['distance_m']
                        
                        with self.lock:
                            self.current_location = location_data
                            
                            # Determine aisle from corridor for backward compatibility
                            corridor_to_aisle = {"L": 1, "12": 1, "23": 2, "R": 3}
                            aisle_id = corridor_to_aisle.get(corridor_id, 0)
    
                            # Set Ad (Simple Logic)
                            subset = self.gb.df[(self.gb.df["Aisle_No"] == aisle_id) & (self.gb.df["Position_Tag"] == partition)]
                            if not subset.empty:
                                item = subset.sample(1).iloc[0]
                                self.last_ad = f"OFFER: {item['Product_Name']} @ ₹{item['Price']}"
                            else:
                                self.last_ad = "Welcome to Smart Mart!"
                        
                        print(f"📍 Pos: {partition} | Dist: {distance}m | Corr: {corridor_id} | ESP: {best_name} (Raw: {best_rssi}, Smooth: {location_data['smoothed_rssi']})")
                    else:
                        print("📡 Position data could not be resolved this cycle")
                else:
                    print("📡 No ESP32 beacons detected this scan cycle")
                
            except Exception as e:
                print(f"Loop Error: {e}")
                await asyncio.sleep(10)

    async def _scan_average(self, target, duration):
        vals = []
        def cb(d, ad):
            if d.name == target: vals.append(ad.rssi)
        
        s = BleakScanner(cb)
        await s.start()
        await asyncio.sleep(duration)
        await s.stop()
        return sum(vals)/len(vals) if vals else None
