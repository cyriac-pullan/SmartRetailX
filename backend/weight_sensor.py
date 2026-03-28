"""
Weight Sensor Integration for Raspberry Pi
Requires: HX711 amplifier, Load Cell, RPi.GPIO
"""

try:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False
    print("Warning: Hardware libraries not available. Using mock mode.")

import time
from flask import Flask, jsonify

app = Flask(__name__)

# HX711 pins (adjust based on your wiring)
DT_PIN = 27
SCK_PIN = 17

# Calibration factor (adjust based on your calibration)
CALIBRATION_FACTOR = -1000

if HAS_HARDWARE:
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    
    # Initialize scale
    hx = HX711(DT_PIN, SCK_PIN)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(CALIBRATION_FACTOR)
    hx.reset()
    
    # Wait for sensor to stabilize
    time.sleep(1)

def calibrate_scale():
    """Calibration procedure"""
    if not HAS_HARDWARE:
        return None
    
    print("\n=== WEIGHT SCALE CALIBRATION ===")
    print("1. Place nothing on the scale")
    input("Press ENTER when ready...")
    hx.tare()
    print("✓ Tare set (0kg)")
    
    print("\n2. Place 5kg reference weight on scale")
    input("Press ENTER when ready...")
    readings = []
    for i in range(10):
        readings.append(hx.get_weight(5))
        time.sleep(0.1)
    avg_reading = sum(readings) / len(readings)
    print(f"Average reading: {avg_reading}")
    
    # Calculate calibration factor
    calibration = avg_reading / 5.0
    print(f"Calibration factor: {calibration}")
    return calibration

def read_weight():
    """Read current weight"""
    if not HAS_HARDWARE:
        # Mock mode - return simulated weight
        import random
        base_weight = 20.0  # kg
        variance = random.uniform(-0.2, 0.2)
        return round(base_weight + variance, 2)
    
    try:
        weight = hx.get_weight(5)
        return round(weight, 2)
    except Exception as e:
        print(f"Error reading weight: {e}")
        return None

@app.route('/api/weight/read', methods=['GET'])
def get_weight():
    """API endpoint for weight reading"""
    weight = read_weight()
    if weight is None:
        return jsonify({'error': 'Failed to read weight'}), 500
    return jsonify({
        'weight_kg': weight, 
        'timestamp': time.time(),
        'mode': 'hardware' if HAS_HARDWARE else 'mock'
    })

@app.route('/api/weight/calibrate', methods=['POST'])
def calibrate():
    """Calibration endpoint"""
    if not HAS_HARDWARE:
        return jsonify({'error': 'Hardware not available'}), 400
    
    calibration_factor = calibrate_scale()
    if calibration_factor:
        return jsonify({
            'calibration_factor': calibration_factor,
            'status': 'calibrated'
        })
    return jsonify({'error': 'Calibration failed'}), 500

if __name__ == '__main__':
    print("Weight sensor initialized")
    print(f"Mode: {'Hardware' if HAS_HARDWARE else 'Mock'}")
    app.run(host='0.0.0.0', port=5001, debug=True)

