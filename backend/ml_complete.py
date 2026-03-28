from flask import Flask, jsonify, request
import sqlite3
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from collections import Counter, defaultdict

app = Flask(__name__)


class RecommendationEngine:
    def __init__(self):
        self.category_preferences = defaultdict(Counter)

    def get_fbt_recommendations(self, product_id, limit=5):
        conn = sqlite3.connect('smartretail.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT ci2.product_id, p.name, p.price, COUNT(*) as freq
            FROM cart_items ci1
            JOIN cart_items ci2 ON ci1.cart_id = ci2.cart_id
            JOIN products p ON ci2.product_id = p.product_id
            WHERE ci1.product_id = ? AND ci2.product_id != ?
            GROUP BY ci2.product_id
            ORDER BY freq DESC
            LIMIT ?
        ''', (product_id, product_id, limit))
        recs = [
            {'product_id': r[0], 'name': r[1], 'price': r[2], 'frequency': r[3]}
            for r in cursor.fetchall()
        ]
        conn.close()
        return recs

    def get_category_recommendations(self, category, limit=5):
        conn = sqlite3.connect('smartretail.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT p.product_id, p.name, p.price, COUNT(ci.id) as purchases
            FROM products p
            LEFT JOIN cart_items ci ON p.product_id = ci.product_id
            WHERE p.category = ?
            GROUP BY p.product_id
            ORDER BY purchases DESC
            LIMIT ?
        ''', (category, limit))
        recs = [
            {'product_id': r[0], 'name': r[1], 'price': r[2], 'popularity': r[3]}
            for r in cursor.fetchall()
        ]
        conn.close()
        return recs


class DemandForecaster:
    def forecast_product(self, product_id, days_ahead=7):
        conn = sqlite3.connect('smartretail.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(created_at) as date, SUM(quantity) as qty
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.cart_id
            WHERE ci.product_id = ?
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        ''', (product_id,))
        history = cursor.fetchall()
        conn.close()
        if len(history) < 5:
            return {'error': 'Insufficient historical data', 'days_available': len(history)}
        history.reverse()
        X = np.array(range(len(history))).reshape(-1, 1)
        y = np.array([h[1] for h in history])
        model = LinearRegression()
        model.fit(X, y)
        future_X = np.array(range(len(history), len(history) + days_ahead)).reshape(-1, 1)
        predictions = model.predict(future_X)
        r_squared = model.score(X, y)
        return {
            'product_id': product_id,
            'forecast_days': days_ahead,
            'historical_avg': float(np.mean(y)),
            'trend': float(model.coef_[0]),
            'predictions': [max(0, int(p)) for p in predictions],
            'confidence': round(r_squared, 3),
            'recommendation': 'Increase stock' if model.coef_[0] > 0 else 'Stock stable'
        }


class AnomalyDetector:
    def __init__(self):
        self.weight_variance_threshold = 1.0
        self.price_threshold_factor = 2.0

    def detect_weight_anomalies(self, days=30):
        conn = sqlite3.connect('smartretail.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.bill_id, wr.expected_weight, wr.actual_weight, wr.variance, b.created_at
            FROM weight_readings wr
            JOIN bills b ON wr.bill_id = b.bill_id
            WHERE DATE(b.created_at) >= DATE('now', '-{} days')
            ORDER BY b.created_at DESC
        '''.format(days))
        readings = cursor.fetchall()
        anomalies = []
        for reading in readings:
            if reading[3] > self.weight_variance_threshold:
                anomalies.append({
                    'bill_id': reading[0],
                    'expected_weight': reading[1],
                    'actual_weight': reading[2],
                    'variance': reading[3],
                    'timestamp': reading[4],
                    'severity': 'high' if reading[3] > 2.0 else 'medium'
                })
        conn.close()
        return anomalies

    def detect_price_anomalies(self):
        conn = sqlite3.connect('smartretail.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_id, AVG(unit_price) as avg_price, MAX(unit_price) as max_price, MIN(unit_price) as min_price
            FROM cart_items
            GROUP BY product_id
        ''')
        products = cursor.fetchall()
        conn.close()
        anomalies = []
        for product in products:
            price_range = product[2] - product[3]
            avg_price = product[1]
            if price_range > avg_price * 0.1:
                anomalies.append({
                    'product_id': product[0],
                    'average_price': avg_price,
                    'max_price': product[2],
                    'min_price': product[3],
                    'variation_percent': round((price_range / avg_price) * 100, 2)
                })
        return anomalies


recommender = RecommendationEngine()
forecaster = DemandForecaster()
detector = AnomalyDetector()


@app.route('/api/ml/recommendations/fbt', methods=['GET'])
def get_fbt_recommendations():
    product_id = request.args.get('product_id')
    limit = request.args.get('limit', 5, type=int)
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    recs = recommender.get_fbt_recommendations(product_id, limit)
    return jsonify({'product_id': product_id, 'type': 'frequently_bought_together', 'recommendations': recs})


@app.route('/api/ml/recommendations/category', methods=['GET'])
def get_category_recommendations():
    category = request.args.get('category')
    limit = request.args.get('limit', 5, type=int)
    if not category:
        return jsonify({'error': 'category required'}), 400
    recs = recommender.get_category_recommendations(category, limit)
    return jsonify({'category': category, 'type': 'category_popular', 'recommendations': recs})


@app.route('/api/ml/forecast/product', methods=['GET'])
def forecast_product():
    product_id = request.args.get('product_id')
    days = request.args.get('days', 7, type=int)
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    forecast = forecaster.forecast_product(product_id, days)
    return jsonify({'forecast': forecast})


@app.route('/api/ml/anomalies/weight', methods=['GET'])
def get_weight_anomalies():
    days = request.args.get('days', 30, type=int)
    anomalies = detector.detect_weight_anomalies(days)
    return jsonify({'type': 'weight_anomalies', 'period_days': days, 'total_anomalies': len(anomalies), 'anomalies': anomalies})


@app.route('/api/ml/anomalies/price', methods=['GET'])
def get_price_anomalies():
    anomalies = detector.detect_price_anomalies()
    return jsonify({'type': 'price_anomalies', 'total_anomalies': len(anomalies), 'anomalies': anomalies})


@app.route('/api/ml/health', methods=['GET'])
def ml_health():
    return jsonify({'status': 'healthy', 'services': {'recommendations': 'active', 'forecasting': 'active', 'anomaly_detection': 'active'}})


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════╗
    ║   SmartRetailX ML Services         ║
    ║   Running on http://0.0.0.0:5003  ║
    ╚════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5003)
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