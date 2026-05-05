import os
import json

class IndoorPositioning:
    def __init__(self, walkway_length_m=1.5):
        # ── Classroom / Demo config (ESP32s spaced 0.5 m apart) ──────────────
        self.walkway_length_m = 1.5   # 4 beacons × 0.5 m gaps = 1.5 m total span
        self.partitions = 6
        self.partition_size = self.walkway_length_m / self.partitions
        
        self.calibration = self._load_calibration()

        # Filtering — fast response for short distances
        self.ema_alpha = 0.35          # Higher = reacts faster (good for close range)
        self.smoothed_rssi = {}
        self.current_walkway = None
        self.hysteresis_threshold = 2.0  # Lower = switches corridor sooner (needed at 0.5 m)

        # TX Power at 1 m — tuned for close-range classroom
        # At 0.5 m spacing the strongest beacon is very loud; calibrate to actual readings
        self.tx_power = {
            "ESP32_AISLE_1": -60,   # Left end — adjust after calibration
            "ESP32_AISLE_2": -62,   # Left-centre
            "ESP32_AISLE_3": -62,   # Right-centre
            "ESP32_AISLE_4": -60    # Right end
        }
        self.n_path_loss = 2.0   # 2.0 = open-air / classroom (no metal shelves)
        
        self.esp_corridors = {
            "ESP32_AISLE_1": "L",
            "ESP32_AISLE_2": "12",
            "ESP32_AISLE_3": "23",
            "ESP32_AISLE_4": "R"
        }
        
        self.corridor_parts = {
            "L":  list(range(101, 107)),
            "12": list(range(107, 119)),
            "23": list(range(119, 131)),
            "R":  list(range(131, 137)),
        }

    def _load_calibration(self):
        calib_path = os.path.join(os.path.dirname(__file__), 'calibration_config.json')
        if os.path.exists(calib_path):
            try:
                with open(calib_path, 'r') as f:
                    return json.load(f).get("corridors", {})
            except Exception:
                pass
        return {}

    def update_rssi(self, incoming_signals):
        """
        Process new BLE signals, apply EMA filtering, update location and return current state.
        incoming_signals: dict like {'ESP32_AISLE_2': -75, 'ESP32_AISLE_3': -80}
        """
        # 1. Apply EMA Filter to incoming signals
        # Only process ESP names we know
        valid_signals = {k: v for k, v in incoming_signals.items() if k in self.esp_corridors}
        
        if not valid_signals:
            return None

        for esp_id, raw_rssi in valid_signals.items():
            if esp_id in self.smoothed_rssi:
                 self.smoothed_rssi[esp_id] = (self.ema_alpha * raw_rssi) + ((1 - self.ema_alpha) * self.smoothed_rssi[esp_id])
            else:
                 self.smoothed_rssi[esp_id] = raw_rssi
                 
        # 2. Determine Location
        corridor_id = "L"
        distance_m = 0.0
        
        if self.calibration:
            # ── k-NN Fingerprint Matching (High Accuracy) ──
            points = []
            for corr, positions in self.calibration.items():
                for pos, f_rssi in positions.items():
                    error = 0
                    for esp_id in self.esp_corridors:
                        s_val = self.smoothed_rssi.get(esp_id, -100)
                        f_val = f_rssi.get(esp_id, -100)
                        if f_val is None: f_val = -100
                        error += (s_val - f_val) ** 2
                    
                    if pos == "start": d_m = 0.0
                    elif pos == "middle": d_m = self.walkway_length_m / 2.0
                    else: d_m = self.walkway_length_m
                    
                    points.append((error, corr, d_m))
            
            # Sort by lowest error
            points.sort(key=lambda x: x[0])
            best_error, best_corr, best_dm = points[0]
            
            # Interpolate distance with 2nd best point if it's in the same corridor
            if len(points) > 1:
                err2, corr2, dm2 = points[1]
                if corr2 == best_corr and err2 > 0:
                    w1 = 1.0 / (best_error + 0.1)
                    w2 = 1.0 / (err2 + 0.1)
                    distance_m = (best_dm * w1 + dm2 * w2) / (w1 + w2)
                else:
                    distance_m = best_dm
            else:
                distance_m = best_dm
                
            corridor_id = best_corr
            # Update current_walkway for state tracking
            corr_to_esp = {v: k for k, v in self.esp_corridors.items()}
            self.current_walkway = corr_to_esp.get(corridor_id, list(self.esp_corridors.keys())[0])
            active_rssi = self.smoothed_rssi.get(self.current_walkway, -100)
            
        else:
            # ── Fallback Log-Distance Path Loss Model ──
            strongest_esp = max(self.smoothed_rssi, key=self.smoothed_rssi.get)
            strongest_rssi = self.smoothed_rssi[strongest_esp]
            
            if self.current_walkway != strongest_esp:
                if self.current_walkway is None or (strongest_rssi > self.smoothed_rssi.get(self.current_walkway, -100) + self.hysteresis_threshold):
                    self.current_walkway = strongest_esp
            
            active_rssi = self.smoothed_rssi[self.current_walkway]
            baseline_tx = self.tx_power.get(self.current_walkway, -60)
            distance_m = 10 ** ((baseline_tx - active_rssi) / (10 * self.n_path_loss))
            corridor_id = self.esp_corridors.get(self.current_walkway, "L")

        # 3. Map into Partitions
        parts = self.corridor_parts.get(corridor_id, list(range(101, 107)))
        
        # Assuming ESP is placed at the start of the corridor.
        # Shortest distance (0m) -> Start of array
        # Longest distance (walkway_length_m) -> End of array
        # partition_index will be 0 to len(parts)-1
        
        parts_count = len(parts)
        partition_size_dynamic = self.walkway_length_m / parts_count
        
        index = int(distance_m / partition_size_dynamic)
        index = max(0, min(parts_count - 1, index)) # Clamp to bounds
        
        partition_tag = f"P{parts[index]}"
        
        return {
            'corridor': corridor_id,
            'esp': self.current_walkway,
            'partition': partition_tag,
            'distance_m': round(distance_m, 2),
            'smoothed_rssi': round(active_rssi, 2),
            'raw_rssi': valid_signals.get(self.current_walkway),
            'all_smoothed': {k: round(v, 2) for k, v in self.smoothed_rssi.items()}
        }
