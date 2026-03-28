import RPi.GPIO as GPIO
import time
import threading
import json
from flask import Flask, jsonify, request
from hx711 import HX711
import sqlite3
from datetime import datetime


class WeightScale:
    """Raspberry Pi weight scale with calibration and persistence."""

    def __init__(self, dt_pin=27, sck_pin=17):
        self.dt_pin = dt_pin
        self.sck_pin = sck_pin
        self.hx = HX711(dt_pin, sck_pin)
        self.calibration_factor = -1000
        self.is_calibrated = False
        self.current_weight = 0
        self.lock = threading.Lock()

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        self.hx.set_reading_format("MSB", "MSB")
        self.hx.set_reference_unit(self.calibration_factor)
        self.hx.reset()
        time.sleep(1)

    def calibrate(self):
        """Interactive calibration routine using 5kg reference."""
        print("\n" + "=" * 50)
        print("WEIGHT SCALE CALIBRATION PROCEDURE")
        print("=" * 50)

        print("\n[STEP 1] Tare (Zero Point)")
        print("Ensure nothing is on the scale")
        input("Press ENTER when ready...")
        self.hx.tare()
        print("✓ Tare set to 0kg")

        print("\n[STEP 2] Reference Weight Calibration")
        print("Place exactly 5kg on the scale")
        input("Press ENTER when ready...")

        readings = []
        for i in range(20):
            reading = self.hx.get_weight(5)
            readings.append(reading)
            print(f"Reading {i+1}: {reading:.2f}")
            time.sleep(0.1)

        avg_reading = sum(readings) / len(readings)
        self.calibration_factor = avg_reading / 5.0
        print(f"\n✓ Calibration Factor: {self.calibration_factor:.4f}")
        self.is_calibrated = True
        self._save_calibration()
        print("\nCalibration complete!")
        return self.calibration_factor

    def _save_calibration(self):
        with open('calibration.json', 'w') as f:
            json.dump({'calibration_factor': self.calibration_factor, 'timestamp': datetime.now().isoformat()}, f)

    def _load_calibration(self):
        try:
            with open('calibration.json', 'r') as f:
                data = json.load(f)
                self.calibration_factor = data['calibration_factor']
                self.is_calibrated = True
                print(f"Loaded calibration factor: {self.calibration_factor}")
        except FileNotFoundError:
            print("No calibration file found. Running calibration...")
            self.calibrate()

    def read_weight(self):
        with self.lock:
            try:
                weight = self.hx.get_weight(5)
                weight = round(weight, 2)
                self.current_weight = weight
                return weight
            except Exception as e:
                print(f"Error reading weight: {e}")
                return None

    def tare(self):
        self.hx.tare()
        self.current_weight = 0


app = Flask(__name__)
scale = WeightScale()


@app.before_request
def startup():
    if not hasattr(app, 'scale_initialized'):
        scale.setup()
        scale._load_calibration()
        app.scale_initialized = True


@app.route('/api/weight/read', methods=['GET'])
def get_weight():
    weight = scale.read_weight()
    if weight is None:
        return jsonify({'error': 'Failed to read weight'}), 500
    return jsonify({'weight_kg': weight, 'is_calibrated': scale.is_calibrated, 'timestamp': datetime.now().isoformat()})


@app.route('/api/weight/calibrate', methods=['POST'])
def calibrate_scale():
    try:
        factor = scale.calibrate()
        return jsonify({'status': 'calibrated', 'calibration_factor': factor})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weight/tare', methods=['POST'])
def tare_scale():
    scale.tare()
    return jsonify({'status': 'tared', 'weight': 0})


@app.route('/api/weight/verify', methods=['POST'])
def verify_bill_weight():
    data = request.get_json()
    bill_id = data.get('bill_id')
    expected_weight = data.get('expected_weight_kg')
    tolerance = data.get('tolerance', 0.5)

    actual_weight = scale.read_weight()
    if actual_weight is None:
        return jsonify({'error': 'Cannot read scale'}), 500

    variance = abs(actual_weight - expected_weight)
    if variance <= tolerance:
        status = 'verified'
        message = 'Weight verified. You may exit.'
    elif variance <= tolerance * 2:
        status = 'caution'
        message = 'Small weight difference. Check cart.'
    else:
        status = 'suspect'
        message = 'Large weight difference. Please contact staff.'

    conn = sqlite3.connect('smartretail.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bills 
        SET actual_weight_kg = ?, weight_variance_kg = ?, status = ?
        WHERE bill_id = ?
    ''', (actual_weight, variance, status, bill_id))
    cursor.execute('''
        INSERT INTO weight_readings 
        (bill_id, expected_weight, actual_weight, variance, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (bill_id, expected_weight, actual_weight, variance, status))
    conn.commit()
    conn.close()

    return jsonify({
        'bill_id': bill_id,
        'expected_weight_kg': expected_weight,
        'actual_weight_kg': actual_weight,
        'variance_kg': round(variance, 2),
        'status': status,
        'message': message,
        'tolerance_kg': tolerance
    })


@app.route('/api/weight/health', methods=['GET'])
def weight_health():
    weight = scale.read_weight()
    return jsonify({'status': 'healthy' if weight is not None else 'error', 'calibrated': scale.is_calibrated, 'current_weight': weight})


if __name__ == '__main__':
    print("""
    ╔═════════════════════════════════════╗
    ║  SmartRetailX Weight Scale Service  ║
    ║  Running on http://0.0.0.0:5001    ║
    ╚═════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5001, debug=False)
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