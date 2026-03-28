from flask import Flask, jsonify, request
import random
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Simulated base weight (kg) for testing
BASE_WEIGHT = 20.0
VARIANCE_RANGE = 0.3


@app.route('/api/weight/read', methods=['GET'])
def get_weight():
    variance = random.uniform(-VARIANCE_RANGE, VARIANCE_RANGE)
    weight = round(BASE_WEIGHT + variance, 2)
    return jsonify({
        'weight_kg': weight,
        'is_calibrated': True,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/weight/verify', methods=['POST'])
def verify_weight():
    data = request.get_json()
    bill_id = data.get('bill_id')
    expected_weight = data.get('expected_weight_kg')
    tolerance = data.get('tolerance', 0.5)

    variance = random.uniform(-0.2, 0.2)
    actual_weight = round(expected_weight + variance, 2)
    weight_var = abs(actual_weight - expected_weight)

    if weight_var <= tolerance:
        status = 'verified'
        message = 'Weight verified. Checkout successful!'
    else:
        status = 'suspect'
        message = 'Weight mismatch detected. Please verify items.'

    conn = sqlite3.connect('smartretail.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bills 
        SET actual_weight_kg = ?, weight_variance_kg = ?, status = ?
        WHERE bill_id = ?
    ''', (actual_weight, weight_var, status, bill_id))
    cursor.execute('''
        INSERT INTO weight_readings 
        (bill_id, expected_weight, actual_weight, variance, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (bill_id, expected_weight, actual_weight, weight_var, status))
    conn.commit()
    conn.close()

    return jsonify({
        'bill_id': bill_id,
        'expected_weight_kg': expected_weight,
        'actual_weight_kg': actual_weight,
        'variance_kg': round(weight_var, 2),
        'status': status,
        'message': message
    })


if __name__ == '__main__':
    print("Starting mock weight service on :5001")
    app.run(host='0.0.0.0', port=5001)
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