"""
BLE Beacon Scanner for Indoor Navigation
Requires: bleak library for BLE scanning
"""

try:
    import asyncio
    from bleak import BleakScanner
    HAS_BLE = True
except ImportError:
    HAS_BLE = False
    print("Warning: BLE libraries not available. Using mock mode.")

from flask import Flask, jsonify

app = Flask(__name__)

# Beacon configuration
BEACONS = {
    'UUID1': {'name': 'Aisle 1 - Grains', 'location': (0, 0)},
    'UUID2': {'name': 'Aisle 2 - Oils', 'location': (10, 0)},
    'UUID3': {'name': 'Aisle 3 - Snacks', 'location': (20, 0)},
    'UUID4': {'name': 'Aisle 4 - Beverages', 'location': (30, 0)},
    'UUID5': {'name': 'Exit', 'location': (40, 0)},
}

async def scan_beacons():
    """Scan for nearby BLE beacons"""
    if not HAS_BLE:
        # Mock mode - return simulated beacons
        return [
            {
                'uuid': 'UUID1',
                'rssi': -60,
                'name': BEACONS['UUID1']['name'],
                'location': BEACONS['UUID1']['location']
            },
            {
                'uuid': 'UUID2',
                'rssi': -70,
                'name': BEACONS['UUID2']['name'],
                'location': BEACONS['UUID2']['location']
            }
        ]
    
    devices = await BleakScanner.discover(timeout=5.0)
    nearby_beacons = []
    
    for device in devices:
        if device.address in BEACONS:
            nearby_beacons.append({
                'uuid': device.address,
                'rssi': device.rssi,
                'name': BEACONS[device.address]['name'],
                'location': BEACONS[device.address]['location']
            })
    
    return nearby_beacons

def estimate_position(beacons):
    """Estimate cart position from beacon signals"""
    if not beacons:
        return None
    
    # Simple weighted average based on signal strength
    total_weight = 0
    weighted_x = 0
    weighted_y = 0
    
    for beacon in beacons:
        # RSSI to distance conversion
        rssi = beacon['rssi']
        distance = 10 ** ((rssi + 50) / -20)  # Rough estimate
        weight = 1 / (distance ** 2) if distance > 0 else 0
        
        total_weight += weight
        weighted_x += weight * beacon['location'][0]
        weighted_y += weight * beacon['location'][1]
    
    if total_weight == 0:
        return None
    
    return {
        'x': weighted_x / total_weight,
        'y': weighted_y / total_weight,
        'beacons_detected': len(beacons)
    }

@app.route('/api/navigation/position', methods=['GET'])
def get_position():
    """Get current cart position"""
    if HAS_BLE:
        beacons = asyncio.run(scan_beacons())
    else:
        beacons = scan_beacons()
    
    position = estimate_position(beacons)
    
    return jsonify({
        'position': position,
        'beacons': beacons,
        'mode': 'hardware' if HAS_BLE else 'mock'
    })

@app.route('/api/navigation/beacons', methods=['GET'])
def get_beacons():
    """Get all configured beacons"""
    return jsonify({
        'beacons': BEACONS,
        'total': len(BEACONS)
    })

if __name__ == '__main__':
    print("BLE Scanner initialized")
    print(f"Mode: {'Hardware' if HAS_BLE else 'Mock'}")
    app.run(host='0.0.0.0', port=5002, debug=True)

