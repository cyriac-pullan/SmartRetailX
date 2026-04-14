class IndoorPositioning:
    def __init__(self, walkway_length_m=6.0):
        # Configuration
        self.walkway_length_m = 2.0
        self.partitions = 6
        self.partition_size = self.walkway_length_m / self.partitions
        
        # Filtering State
        self.ema_alpha = 0.08  # Slower EMA for less jumping
        self.smoothed_rssi = {}
        self.current_walkway = None
        self.hysteresis_threshold = 4.0 # increased threshold to avoid bouncing between esp32s
        
        # Signal constants
        self.tx_power = -82  # calibrated RSSI at 1 meter
        self.n_path_loss = 3.5 # Env noise factor (higher means drop-off calculates shorter distances)
        
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
                 
        # 2. Determine Strongest Signal (Walkway Detection)
        strongest_esp = max(self.smoothed_rssi, key=self.smoothed_rssi.get)
        strongest_rssi = self.smoothed_rssi[strongest_esp]
        
        # Apply Hysteresis for switching walkways
        if self.current_walkway != strongest_esp:
            # Only switch if it beats the current walkway by the threshold
            if self.current_walkway is None or (strongest_rssi > self.smoothed_rssi.get(self.current_walkway, -100) + self.hysteresis_threshold):
                self.current_walkway = strongest_esp
        
        # 3. Convert RSSI to Distance using Log-Distance Path Loss Model
        # Using the active walkway's smoothed RSSI
        active_rssi = self.smoothed_rssi[self.current_walkway]
        distance_m = 10 ** ((self.tx_power - active_rssi) / (10 * self.n_path_loss))
        
        # 4. Map into Partitions
        corridor_id = self.esp_corridors.get(self.current_walkway, "L")
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
