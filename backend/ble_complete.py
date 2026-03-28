import asyncio
from bleak import BleakScanner
from flask import Flask, jsonify, request
import math
from datetime import datetime

app = Flask(__name__)

BEACONS = {
    '00:11:22:33:44:00': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB07647825', 'name': 'Entrance', 'location': (0, 0), 'aisle': 'Entrance', 'section': 'Entry Point'},
    '00:11:22:33:44:01': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB07647826', 'name': 'Aisle 1 - Grains', 'location': (10, 5), 'aisle': 1, 'section': 'Rice, Dal, Flour'},
    '00:11:22:33:44:02': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB07647827', 'name': 'Aisle 2 - Oils & Sauces', 'location': (20, 5), 'aisle': 2, 'section': 'Oils, Vinegar, Ketchup'},
    '00:11:22:33:44:03': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB07647828', 'name': 'Aisle 3 - Snacks', 'location': (30, 5), 'aisle': 3, 'section': 'Chips, Chocolate, Sweets'},
    '00:11:22:33:44:04': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB07647829', 'name': 'Aisle 4 - Beverages', 'location': (40, 5), 'aisle': 4, 'section': 'Milk, Juice, Drinks'},
    '00:11:22:33:44:05': {'uuid': 'FDA50693-A4E2-4FB1-AFCF-C6EB0764782A', 'name': 'Exit Checkout', 'location': (45, 0), 'aisle': 'Exit', 'section': 'Checkout Counter'}
}


class BeaconScanner:
    def __init__(self):
        self.nearby_beacons = []
        self.current_position = None

    async def scan_beacons(self):
        try:
            devices = await BleakScanner.discover()
            self.nearby_beacons = []
            for device in devices:
                if device.address in BEACONS:
                    info = BEACONS[device.address].copy()
                    info['rssi'] = device.rssi
                    info['distance'] = self._rssi_to_distance(device.rssi)
                    self.nearby_beacons.append(info)
            return self.nearby_beacons
        except Exception as e:
            print(f"Scan error: {e}")
            return []

    def _rssi_to_distance(self, rssi):
        tx_power = -59
        n = 2
        if rssi == 0:
            return -1
        distance = 10 ** ((rssi - tx_power) / (10 * n))
        return round(distance, 2)

    def estimate_position(self):
        if not self.nearby_beacons:
            return None
        valid = [b for b in self.nearby_beacons if 0 < b['distance'] < 50]
        if not valid:
            return None
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        for beacon in valid:
            dist = beacon['distance']
            weight = 1 / (dist ** 2) if dist > 0 else 0
            total_weight += weight
            weighted_x += weight * beacon['location'][0]
            weighted_y += weight * beacon['location'][1]
        if total_weight == 0:
            return None
        position = {
            'x': round(weighted_x / total_weight, 2),
            'y': round(weighted_y / total_weight, 2),
            'accuracy': 'good' if len(valid) >= 2 else 'fair',
            'beacons_detected': len(valid),
            'nearest_beacon': valid[0]['name'] if valid else None
        }
        self.current_position = position
        return position

    def get_navigation_help(self):
        if not self.current_position or not self.nearby_beacons:
            return None
        nearest = self.nearby_beacons[0]
        aisle = nearest.get('aisle')
        section = nearest.get('section')
        suggestions = {
            1: "Looking for Grains? Try Aisle 1 for Rice, Dal, and Flour.",
            2: "Need Oils and Condiments? You're in the right place!",
            3: "Check out our Snacks and Chocolate selection here!",
            4: "Beverages and Dairy products available in this aisle.",
            'Entrance': "Welcome! Start by scanning items or browsing the aisles.",
            'Exit': "Proceed to checkout counter to complete your purchase."
        }
        return {
            'current_location': f"Aisle {aisle}" if isinstance(aisle, int) else aisle,
            'section': section,
            'suggestion': suggestions.get(aisle, '')
        }


scanner = BeaconScanner()


@app.route('/api/navigation/position', methods=['GET'])
async def get_position():
    try:
        await scanner.scan_beacons()
        position = scanner.estimate_position()
        return jsonify({
            'position': position,
            'beacons_nearby': [
                {'name': b['name'], 'distance_m': b['distance'], 'rssi': b['rssi']}
                for b in scanner.nearby_beacons[:3]
            ],
            'navigation': scanner.get_navigation_help(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/navigation/directions', methods=['GET'])
def get_directions():
    target = request.args.get('target', 'Aisle 1')
    target_beacon = None
    for beacon_data in BEACONS.values():
        if beacon_data['name'].lower() == target.lower():
            target_beacon = beacon_data
            break
    if not target_beacon:
        return jsonify({'error': 'Target not found'}), 404
    if not scanner.current_position:
        return jsonify({'error': 'Current position unknown'}), 400
    current = scanner.current_position
    target_pos = target_beacon['location']
    distance = math.sqrt((target_pos[0] - current['x'])**2 + (target_pos[1] - current['y'])**2)
    return jsonify({
        'target': target_beacon['name'],
        'current_location': current.get('nearest_beacon'),
        'distance_m': round(distance, 2),
        'direction': 'straight ahead' if distance > 0 else 'you are here',
        'guidance': f"Head towards {target_beacon['name']} ({round(distance, 1)}m away)"
    })


@app.route('/api/navigation/beacons', methods=['GET'])
def get_all_beacons():
    beacon_list = [
        {'id': addr, 'name': info['name'], 'location': info['location'], 'section': info['section']}
        for addr, info in BEACONS.items()
    ]
    return jsonify({
        'total_beacons': len(beacon_list),
        'beacons': beacon_list,
        'store_map': {'width': 50, 'height': 10, 'unit': 'meters'}
    })


if __name__ == '__main__':
    print("""
    ╔═════════════════════════════════════╗
    ║   SmartRetailX BLE Navigation       ║
    ║   Running on http://0.0.0.0:5002   ║
    ╚═════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5002)
{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}