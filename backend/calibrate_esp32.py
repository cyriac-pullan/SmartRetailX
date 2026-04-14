import asyncio
from bleak import BleakScanner

# Constants matching your backend
TARGET_ESPS = ["ESP32_AISLE_1", "ESP32_AISLE_2", "ESP32_AISLE_3", "ESP32_AISLE_4"]

async def scan():
    print("Scanning for ESP32 Beacons... (Press Ctrl+C to stop)")
    print("For calibration: Stand exactly 1 meter away from a beacon to find its baseline tx_power.")
    
    while True:
        results = {name: [] for name in TARGET_ESPS}
        
        def callback(device, advertisement_data):
            if device.name in TARGET_ESPS:
                results[device.name].append(advertisement_data.rssi)
                
        scanner = BleakScanner(callback)
        await scanner.start()
        await asyncio.sleep(3) # Collect data for 3 seconds
        await scanner.stop()
        
        # Calculate averages for smooth reading
        print("-" * 40)
        found_any = False
        for name, rssi_list in results.items():
            if len(rssi_list) > 0:
                avg_rssi = sum(rssi_list) / len(rssi_list)
                print(f"FOUND -> {name}: {avg_rssi:.1f} dBm ({len(rssi_list)} packets)")
                found_any = True
                
        if not found_any:
            print("MISSING -> No ESP32 Beacons detected in this cycle.")

if __name__ == "__main__":
    try:
        asyncio.run(scan())
    except KeyboardInterrupt:
        print("\nCalibration stopped.")
