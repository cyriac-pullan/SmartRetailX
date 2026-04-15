import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import time
from datetime import datetime
import uuid
from functools import wraps
import os
import hashlib
import psycopg2
import psycopg2.extras
import logging
import concurrent.futures
from typing import List, Tuple, Dict, Any

from backend_service import SmartCartService
from voice_assistant import SmartRetailXVoice
from typing import List, Tuple, Optional
from flask import make_response
from psycopg2 import pool
from contextlib import contextmanager
from functools import lru_cache
import concurrent.futures
import asyncio
from bleak import BleakScanner
try:
    from integration_utils import DBGraphBuilder, DBMarketBasket
    from path_planner import PathFinder
except ImportError:
    DBGraphBuilder = None
    DBMarketBasket = None
    PathFinder = None

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ===== CHATBOT RECIPE FINDER =====
RECIPE_DB = {
    # ── Indian Mains ──────────────────────────────────────
    "biryani": ["Fresho Chicken Breast", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Cardamom Green", "Black Pepper Whole", "Annapurna Salt"],
    "chicken biryani": ["Fresho Chicken Breast", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Cardamom Green", "Annapurna Salt"],
    "mutton biryani": ["MDH Mutton Masala", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Annapurna Salt"],
    "veg biryani": ["Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Annapurna Salt"],
    "butter chicken": ["Fresho Chicken Breast", "Amul Salted Butter", "Amul Fresh Cream", "Amul Taaza Toned Milk", "Garlic", "Fresh Ginger", "Kissan Tomato Ketchup", "Annapurna Salt"],
    "chicken curry": ["Fresho Chicken Breast", "Garlic", "Fresh Ginger", "Amul Pure Ghee", "Annapurna Salt", "Epigamia Greek Yogurt"],
    "chicken tikka masala": ["Fresho Chicken Breast", "Epigamia Greek Yogurt", "Amul Fresh Cream", "Amul Salted Butter", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "dal makhani": ["Bb Royal Masoor Dal", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "dal tadka": ["Chana Dal", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "palak paneer": ["Amul Fresh Paneer", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "paneer butter masala": ["Amul Fresh Paneer", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "paneer tikka": ["Amul Fresh Paneer", "Epigamia Greek Yogurt", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "shahi paneer": ["Amul Fresh Paneer", "Amul Fresh Cream", "Amul Salted Butter", "Nutraj Cashews", "Cardamom Green", "Annapurna Salt"],
    "chole": ["Chana Dal", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "rajma": ["Black Eyed Peas Lobia", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "aloo gobi": ["Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fish curry": ["Catla Fish Fillet", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fish fry": ["Catla Fish Fillet", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "prawn curry": ["Prawns Medium", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "korma": ["Fresho Chicken Breast", "Epigamia Greek Yogurt", "Amul Fresh Cream", "Nutraj Cashews", "Amul Pure Ghee", "Cardamom Green", "Annapurna Salt"],
    "keema": ["Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "sambar": ["Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "rasam": ["Garlic", "Black Pepper Whole", "Annapurna Salt", "Fortune Refined Soyabean Oil"],
    # ── Breads & Breakfast ─────────────────────────────────
    "dosa": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "masala dosa": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Fresh Ginger"],
    "idli": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Annapurna Salt"],
    "pav bhaji": ["Bonn Multigrain Bread", "Amul Salted Butter", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "vada pav": ["Bonn Multigrain Bread", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Fresh Ginger"],
    "poha": ["Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "upma": ["Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "paratha": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Annapurna Salt"],
    "aloo paratha": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Garlic", "Annapurna Salt"],
    "roti": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Annapurna Salt"],
    "naan": ["Aashirvaad Multigrain Atta", "Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Amul Salted Butter", "Garlic", "Annapurna Salt"],
    "puri": ["Aashirvaad Multigrain Atta", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "samosa": ["Aashirvaad Multigrain Atta", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "pakora": ["Fortune Rice Flour", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    # ── Rice Dishes ────────────────────────────────────────
    "pulao": ["Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Annapurna Salt"],
    "khichdi": ["Daawat Rozana Basmati Rice", "Bb Royal Masoor Dal", "Amul Pure Ghee", "Annapurna Salt"],
    "curd rice": ["Daawat Rozana Basmati Rice", "Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Annapurna Salt"],
    "lemon rice": ["Daawat Rozana Basmati Rice", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fried rice": ["Daawat Rozana Basmati Rice", "Country Eggs", "Kikkoman Soy Sauce", "Fortune Refined Soyabean Oil", "Garlic", "Annapurna Salt"],
    # ── Sweets ─────────────────────────────────────────────
    "halwa": ["Amul Pure Ghee", "Amul Taaza Toned Milk", "Nutraj Cashews", "Nutraj Raisins", "Cardamom Green", "Madhur Pure Sugar"],
    "kheer": ["Daawat Rozana Basmati Rice", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Cardamom Green", "Nutraj Cashews", "Nutraj Raisins"],
    "gulab jamun": ["Amul Taaza Toned Milk", "Aashirvaad Multigrain Atta", "Madhur Pure Sugar", "Amul Pure Ghee", "Cardamom Green"],
    "rasgulla": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "payasam": ["Amul Taaza Toned Milk", "Daawat Rozana Basmati Rice", "Madhur Pure Sugar", "Nutraj Cashews", "Nutraj Raisins", "Amul Pure Ghee", "Cardamom Green"],
    "gajar ka halwa": ["Amul Taaza Toned Milk", "Madhur Pure Sugar", "Amul Pure Ghee", "Nutraj Cashews", "Cardamom Green"],
    # ── International ──────────────────────────────────────
    "pasta": ["Barilla Penne Pasta", "Amul Cheese Slices", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "sandwich": ["Bonn Multigrain Bread", "Amul Cheese Slices", "Amul Salted Butter", "Hellmanns Real Mayonnaise", "Kissan Tomato Ketchup"],
    "omelette": ["Country Eggs", "Amul Taaza Toned Milk", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "pancakes": ["Aashirvaad Multigrain Atta", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Amul Salted Butter", "Dabur Honey", "Country Eggs"],
    "french fries": ["Fortune Refined Soyabean Oil", "Annapurna Salt", "Kissan Tomato Ketchup"],
    "burger": ["Bonn Multigrain Bread", "Fresho Chicken Breast", "Amul Cheese Slices", "Hellmanns Real Mayonnaise", "Kissan Tomato Ketchup", "Amul Salted Butter"],
    "pizza": ["Aashirvaad Multigrain Atta", "Amul Mozzarella Cheese", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "noodles": ["Chings Secret Hakka Noodles", "Kikkoman Soy Sauce", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Country Eggs"],
    "fried chicken": ["Fresho Chicken Breast", "Country Eggs", "Aashirvaad Multigrain Atta", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "scrambled eggs": ["Country Eggs", "Amul Salted Butter", "Amul Taaza Toned Milk", "Annapurna Salt", "Black Pepper Whole"],
    "salad": ["Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    # ── Drinks ─────────────────────────────────────────────
    "tea": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "coffee": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "lassi": ["Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Annapurna Salt", "Cardamom Green"],
    "milkshake": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "lemonade": ["Madhur Pure Sugar", "Annapurna Salt"],
    "chaas": ["Epigamia Greek Yogurt", "Annapurna Salt"],
    # ── Snacks ─────────────────────────────────────────────
    "bread omelette": ["Bonn Multigrain Bread", "Country Eggs", "Amul Salted Butter", "Annapurna Salt", "Black Pepper Whole"],
    "fruit salad": ["Madhur Pure Sugar", "Amul Taaza Toned Milk"],
    "curry": ["Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Garlic", "Fresh Ginger", "Annapurna Salt"],
}



@app.route('/api/chat/ping', methods=['GET', 'POST'])
def chat_ping_test():
    return jsonify({"status": "ok", "method": request.method, "got": request.get_json()})

@app.route('/api/chat/recipe', methods=['GET', 'POST', 'OPTIONS'])
def chat_recipe_finder():
    if request.method == 'OPTIONS':
        return make_response()
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').lower().strip()
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
        
    dish_match = None
    for dish in RECIPE_DB.keys():
        if dish in message:
            dish_match = dish
            break
            
    if not dish_match:
        return jsonify({
            'reply': "I'm not sure about that specific recipe, but I can help you find products! What are you looking to make?",
            'products': []
        })
        
    ingredients = RECIPE_DB[dish_match]
    matched_products = []
    
    try:
        for ing in ingredients:
            sql = """
                SELECT product_id, barcode, name, price, category, aisle, partition_no, shelf_no, stock_quantity, position_tag 
                FROM products WHERE LOWER(name) LIKE LOWER(%s) LIMIT 1
            """
            pattern = f'%{ing}%'
            row = pg_query_one(NEON_DB_DSN, sql, (pattern,))
            if not row:
                row = pg_query_one(NEON_DB_DSN, sql.replace('FROM products', 'FROM products2'), (pattern,))
                
            if row:
                matched_products.append(dict(row))
    except Exception as e:
        logging.error(f"Recipe DB Error: {e}")
            
    if matched_products:
        reply_msg = f"Here is what you need to make {dish_match.title()}:"
    else:
        reply_msg = f"I couldn't find the necessary ingredients for {dish_match.title()} in our store."
        
    return jsonify({
        'reply': reply_msg,
        'dish': dish_match.title(),
        'products': matched_products
    })

print(f"--- INIT FLASK ROUTES ---")
for rule in app.url_map.iter_rules():
    print(f"ROUTE: {rule} - {rule.methods}")
print(f"-------------------------")


# ===== DATABASE HELPERS =====
# Single consolidated database — all tables live here
NEON_DB_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
# Aliases kept for any code that still references the old per-purpose DSN names
NEON_PRODUCTS_DSN   = NEON_DB_DSN
NEON_PRODUCTS_2_DSN = NEON_DB_DSN
NEON_AUTH_DSN       = NEON_DB_DSN
NEON_HISTORY_DSN    = NEON_DB_DSN
NEON_CARTS_DSN      = NEON_DB_DSN
NEON_ANALYTICS_DSN  = NEON_DB_DSN


# ===== CONNECTION POOLING =====
POOLS = {}
EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=10)

# ===== SMART CART SERVICE & VOICE SERVICE =====
smart_cart_service = SmartCartService()
voice_assistant_service = SmartRetailXVoice()

def init_pools():
    # Single DB — one pool is sufficient
    try:
        POOLS[NEON_DB_DSN] = psycopg2.pool.ThreadedConnectionPool(1, 10, NEON_DB_DSN, sslmode="require")
        logging.info("Initialized connection pool for NEON_DB")
    except Exception as e:
        logging.error(f"Failed to init pool: {e}")
        POOLS[NEON_DB_DSN] = None

# Initialize pools on startup
init_pools()

def get_db():
    conn = sqlite3.connect('smartretail.db')
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_pg_conn(dsn):
    if dsn not in POOLS or POOLS[dsn] is None:
        # Fallback (should be rare if init_pools worked)
        logging.warning(f"No active pool found for DSN, attempting new connection")
        try:
            conn = psycopg2.connect(dsn, sslmode="require", connect_timeout=3)
            yield conn
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    else:
        conn = POOLS[dsn].getconn()
        try:
            yield conn
        finally:
            POOLS[dsn].putconn(conn)


def pg_query_one(dsn, sql, params):
    try:
        with get_pg_conn(dsn) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchone()
    except Exception as e:
        logging.warning(f"Neon DB error, falling back to SQLite for query_one: {e}")
        try:
            sql_sqlite = sql.replace('%s', '?')
            conn = get_db()
            cur = conn.cursor()
            cur.execute(sql_sqlite, params)
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as sqle:
            logging.error(f"SQLite fallback failed: {sqle}")
            return None


# ===== CHATBOT RECIPE FINDER =====


def pg_query_all(dsn, sql, params):
    try:
        with get_pg_conn(dsn) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
    except Exception as e:
        logging.warning(f"Neon DB error, falling back to SQLite for query_all")
        try:
            sql_sqlite = sql.replace('%s', '?')
            conn = get_db()
            cur = conn.cursor()
            cur.execute(sql_sqlite, params)
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as sqle:
            logging.error(f"SQLite fallback failed: {sqle}")
            return []


def pg_execute(dsn, sql, params):
    try:
        with get_pg_conn(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.rowcount
    except Exception as e:
        logging.warning(f"Neon DB error, falling back to SQLite for execute")
        try:
            sql_sqlite = sql.replace('%s', '?').replace('TRUE', '1').replace('FALSE', '0')
            conn = get_db()
            cur = conn.cursor()
            cur.execute(sql_sqlite, params)
            conn.commit()
            rc = cur.rowcount
            conn.close()
            return rc
        except Exception as sqle:
            logging.error(f"SQLite fallback failed: {sqle}")
            return 0


def pg_execute_many(dsn, sql, params_list: List[Tuple]):
    try:
        with get_pg_conn(dsn) as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, params_list)
                conn.commit()
    except Exception as e:
        logging.warning(f"Neon DB error, falling back to SQLite for execute_many")
        try:
            sql_sqlite = sql.replace('%s', '?').replace('TRUE', '1').replace('FALSE', '0')
            conn = get_db()
            cur = conn.cursor()
            cur.executemany(sql_sqlite, params_list)
            conn.commit()
            conn.close()
        except Exception as sqle:
            logging.error(f"SQLite fallback failed: {sqle}")


def query_products_parallel(sql, params_tuple):
    """Query both products (store1) and products2 (store2) tables and merge results using ThreadPool."""
    sql2 = sql.replace('FROM products ', 'FROM products2 ').replace('FROM products\n', 'FROM products2\n')
    
    # Execute both queries concurrently
    future1 = EXECUTOR.submit(pg_query_all, NEON_DB_DSN, sql, params_tuple)
    future2 = EXECUTOR.submit(pg_query_all, NEON_DB_DSN, sql2, params_tuple)
    
    # Wait for both to complete
    try:
        res1 = future1.result() or []
    except Exception as e:
        logging.error(f"Error querying products: {e}")
        res1 = []
        
    try:
        res2 = future2.result() or []
    except Exception as e:
        logging.error(f"Error querying products2: {e}")
        res2 = []
        
    # Deduplicate by barcode preference from store1
    seen = {r['barcode'] for r in res1 if r and 'barcode' in r}
    unique_res2 = [r for r in res2 if r and r.get('barcode') not in seen]
    return res1 + unique_res2


def ensure_neon_tables():
    """Create tables in Neon if they do not exist."""
    # Products
    with get_pg_conn(NEON_PRODUCTS_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    barcode TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    weight_kg REAL NOT NULL,
                    category TEXT NOT NULL,
                    sub_category TEXT,
                    aisle INT,
                    partition_no INT,
                    shelf_no TEXT,
                    position_tag TEXT,
                    side TEXT,
                    stock_quantity INT DEFAULT 100,
                    reorder_level INT DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
                CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
                """
            )
            conn.commit()
    # Carts / Bills (new DSN)
    with get_pg_conn(NEON_CARTS_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS carts (
                    cart_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                );
                CREATE TABLE IF NOT EXISTS cart_items (
                    id SERIAL PRIMARY KEY,
                    cart_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    barcode TEXT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS bills (
                    bill_id TEXT PRIMARY KEY,
                    cart_id TEXT,
                    customer_id TEXT,
                    items_count INT,
                    subtotal REAL,
                    tax REAL,
                    discount REAL,
                    total_amount REAL NOT NULL,
                    expected_weight_kg REAL,
                    actual_weight_kg REAL,
                    weight_variance_kg REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS weight_readings (
                    id SERIAL PRIMARY KEY,
                    bill_id TEXT NOT NULL,
                    expected_weight REAL,
                    actual_weight REAL,
                    variance REAL,
                    tolerance_threshold REAL DEFAULT 0.5,
                    status TEXT DEFAULT 'pending',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_cartitems_cart ON cart_items(cart_id);
                CREATE INDEX IF NOT EXISTS idx_bills_cart ON bills(cart_id);
                CREATE INDEX IF NOT EXISTS idx_bills_customer ON bills(customer_id);
                """
            )
            conn.commit()
    # Auth
    with get_pg_conn(NEON_AUTH_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    barcode TEXT UNIQUE,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT,
                    email TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            # Add is_admin column if it doesn't exist (PostgreSQL way)
            cur.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='customers' AND column_name='is_admin'
                    ) THEN
                        ALTER TABLE customers ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_barcode ON customers(barcode);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_username ON customers(username);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_admin ON customers(is_admin);")
            conn.commit()
    # History
    with get_pg_conn(NEON_HISTORY_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS purchase_history (
                    id SERIAL PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    barcode TEXT NOT NULL,
                    quantity INT NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_history_customer ON purchase_history(customer_id);
                CREATE INDEX IF NOT EXISTS idx_history_barcode ON purchase_history(barcode);
                CREATE TABLE IF NOT EXISTS billings (
                    transaction_id TEXT PRIMARY KEY,
                    bill_id TEXT NOT NULL,
                    customer_id TEXT,
                    payment_method TEXT,
                    amount REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
    # Analytics / Recommendations
    with get_pg_conn(NEON_ANALYTICS_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendations (
                    id SERIAL PRIMARY KEY,
                    product_barcode TEXT NOT NULL,
                    recommended_product_barcode TEXT NOT NULL,
                    co_occurrence_count INT DEFAULT 1,
                    confidence REAL DEFAULT 0.0
                );
                CREATE TABLE IF NOT EXISTS demand_forecast (
                    id SERIAL PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    forecast_date DATE,
                    predicted_quantity INT,
                    actual_quantity INT,
                    forecast_accuracy REAL
                );
                """
            )
            conn.commit()


try:
    ensure_neon_tables()
except Exception as e:
    logging.warning(f"ensure_neon_tables failed (non-fatal): {e}")

# Ensure first customer is admin
def ensure_admin_user():
    """Mark the first customer row as admin, rest as customers"""
    # First, reset all admins to False
    pg_execute(
        NEON_AUTH_DSN,
        "UPDATE customers SET is_admin = FALSE",
        (),
    )
    
    # Get the first customer (by created_at or customer_id)
    first_customer = pg_query_one(
        NEON_AUTH_DSN,
        """
        SELECT customer_id, barcode, username 
        FROM customers 
        ORDER BY created_at ASC, customer_id ASC 
        LIMIT 1
        """,
        (),
    )
    
    if first_customer:
        # Mark first customer as admin
        pg_execute(
            NEON_AUTH_DSN,
            "UPDATE customers SET is_admin = TRUE WHERE customer_id = %s",
            (first_customer['customer_id'],),
        )
        logging.info(f"Admin set to first customer: {first_customer.get('barcode') or first_customer.get('username') or first_customer['customer_id']}")
    else:
        logging.info("No customers found in database")

try:
    ensure_admin_user()
except Exception as e:
    logging.warning(f"ensure_admin_user failed (non-fatal): {e}")

# Error handler
def db_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            logging.exception("SQLite error")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logging.exception("Unhandled error")
            return jsonify({'error': str(e)}), 400
    return decorated_function

# ===== AUTH HELPERS =====


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_customer_by_barcode_or_username(identifier: str):
    return pg_query_one(
        NEON_AUTH_DSN,
        """
        SELECT customer_id, barcode, username, password_hash, name, email, is_admin
        FROM customers
        WHERE barcode = %s OR username = %s
        """,
        (identifier, identifier),
    )


def ensure_customer(customer_id: str):
    return pg_query_one(
        NEON_AUTH_DSN,
        """
        SELECT customer_id, barcode, username, name, email, is_admin
        FROM customers
        WHERE customer_id = %s
        """,
        (customer_id,),
    )


def is_admin_customer(customer_id: str) -> bool:
    """Check if customer is admin (first row in customers table)"""
    customer = ensure_customer(customer_id)
    if not customer:
        return False
    
    # Check if they're marked as admin
    if customer.get('is_admin'):
        return True
    
    # Fallback: check if they're the first customer
    first_customer = pg_query_one(
        NEON_AUTH_DSN,
        """
        SELECT customer_id FROM customers 
        ORDER BY created_at ASC, customer_id ASC 
        LIMIT 1
        """,
        (),
    )
    
    return first_customer and first_customer['customer_id'] == customer_id

def record_purchase_history(customer_id: str, items: List[dict]):
    """Store purchases into Neon history DB."""
    if not customer_id or not items:
        return
    payload = []
    for item in items:
        bc = item.get("barcode")
        qty = int(item.get("quantity", 1))
        if not bc:
            continue
        payload.append((customer_id, bc, qty))
    if not payload:
        return
    pg_execute_many(
        NEON_HISTORY_DSN,
        "INSERT INTO purchase_history (customer_id, barcode, quantity) VALUES (%s, %s, %s)",
        payload,
    )


def record_transaction(bill_id: str, customer_id: str, amount: float, payment_method: str = "cash"):
    """Record transaction in analytics DB."""
    transaction_id = f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    pg_execute(
        NEON_HISTORY_DSN,
        """
        INSERT INTO billings (transaction_id, bill_id, customer_id, payment_method, amount)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (transaction_id, bill_id, customer_id, payment_method, amount),
    )
    return transaction_id


def update_recommendation_cooccurrence(barcodes: List[str]):
    """Update recommendation co-occurrence counts when items are purchased together."""
    if len(barcodes) < 2:
        return
    for i, barcode1 in enumerate(barcodes):
        for barcode2 in barcodes[i + 1:]:
            if barcode1 == barcode2:
                continue
            # Upsert co-occurrence
            existing = pg_query_one(
                NEON_ANALYTICS_DSN,
                """
                SELECT id, co_occurrence_count FROM recommendations
                WHERE product_barcode = %s AND recommended_product_barcode = %s
                """,
                (barcode1, barcode2),
            )
            if existing:
                pg_execute(
                    NEON_ANALYTICS_DSN,
                    """
                    UPDATE recommendations SET co_occurrence_count = co_occurrence_count + 1
                    WHERE id = %s
                    """,
                    (existing['id'],),
                )
            else:
                pg_execute(
                    NEON_ANALYTICS_DSN,
                    """
                    INSERT INTO recommendations (product_barcode, recommended_product_barcode, co_occurrence_count)
                    VALUES (%s, %s, 1)
                    """,
                    (barcode1, barcode2),
                )
            # Also record reverse (bidirectional)
            existing_rev = pg_query_one(
                NEON_ANALYTICS_DSN,
                """
                SELECT id, co_occurrence_count FROM recommendations
                WHERE product_barcode = %s AND recommended_product_barcode = %s
                """,
                (barcode2, barcode1),
            )
            if existing_rev:
                pg_execute(
                    NEON_ANALYTICS_DSN,
                    """
                    UPDATE recommendations SET co_occurrence_count = co_occurrence_count + 1
                    WHERE id = %s
                    """,
                    (existing_rev['id'],),
                )
            else:
                pg_execute(
                    NEON_ANALYTICS_DSN,
                    """
                    INSERT INTO recommendations (product_barcode, recommended_product_barcode, co_occurrence_count)
                    VALUES (%s, %s, 1)
                    """,
                    (barcode2, barcode1),
                )


# ===== APRIORI ALGORITHM FOR RECOMMENDATIONS =====

_APRIORI_CACHE = {
    'transactions': {'data': None, 'timestamp': 0},
    'rules': {'data': None, 'timestamp': 0}
}
CACHE_TTL_SECONDS = 300  # 5 minutes

def get_transactions_from_history(min_support=0.01, min_confidence=0.3):
    """Get transaction data for Apriori algorithm from purchase history and bills."""
    now = time.time()
    if _APRIORI_CACHE['transactions']['data'] and (now - _APRIORI_CACHE['transactions']['timestamp']) < CACHE_TTL_SECONDS:
        return _APRIORI_CACHE['transactions']['data']
        
    # Get transactions from purchase history (grouped by customer and date)
    history_data = pg_query_all(
        NEON_HISTORY_DSN,
        """
        SELECT customer_id, barcode, purchased_at::date as purchase_date
        FROM purchase_history
        WHERE customer_id IS NOT NULL
        ORDER BY customer_id, purchased_at
        """,
        (),
    )
    
    # Group by customer and date to form transactions
    transaction_dict = {}
    for t in history_data:
        key = f"{t['customer_id']}_{t['purchase_date']}"
        if key not in transaction_dict:
            transaction_dict[key] = []
        transaction_dict[key].append(t['barcode'])
    
    # Also get from bills (cart_items) for more complete data
    bill_items = pg_query_all(
        NEON_CARTS_DSN,
        """
        SELECT DISTINCT b.customer_id, ci.barcode, DATE(b.created_at) as purchase_date
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.cart_id
        JOIN bills b ON b.cart_id = c.cart_id
        WHERE b.customer_id IS NOT NULL AND b.status = 'completed'
        ORDER BY b.customer_id, purchase_date
        """,
        (),
    )
    
    # Merge bill data
    for item in bill_items:
        key = f"{item['customer_id']}_{item['purchase_date']}"
        if key not in transaction_dict:
            transaction_dict[key] = []
        if item['barcode'] not in transaction_dict[key]:
            transaction_dict[key].append(item['barcode'])
    
    
    result = list(transaction_dict.values())
    _APRIORI_CACHE['transactions']['data'] = result
    _APRIORI_CACHE['transactions']['timestamp'] = time.time()
    return result


def apriori_algorithm(transactions, min_support=0.01, max_length=2):
    """Apriori algorithm to find frequent itemsets."""
    if not transactions:
        return {}
    
    # Calculate support for single items
    item_counts = {}
    total_transactions = len(transactions)
    
    for transaction in transactions:
        unique_items = set(transaction)
        for item in unique_items:
            item_counts[item] = item_counts.get(item, 0) + 1
    
    # Filter by min_support
    min_count = max(1, int(min_support * total_transactions))
    frequent_items = {item: count for item, count in item_counts.items() if count >= min_count}
    
    # Generate pairs (2-itemsets)
    frequent_pairs = {}
    items_list = list(frequent_items.keys())
    
    for i, item1 in enumerate(items_list):
        for item2 in items_list[i + 1:]:
            pair = tuple(sorted([item1, item2]))
            count = 0
            for transaction in transactions:
                if item1 in transaction and item2 in transaction:
                    count += 1
            if count >= min_count:
                support = count / total_transactions
                frequent_pairs[pair] = {
                    'support': support,
                    'count': count
                }
    
    return {
        'items': frequent_items,
        'pairs': frequent_pairs,
        'total_transactions': total_transactions
    }


def get_apriori_recommendations(barcode, limit=5):
    """Get recommendations using Apriori algorithm."""
    transactions = get_transactions_from_history(min_support=0.01)
    
    if len(transactions) < 10:
        return []  # Not enough data
    
    # Run Apriori
    result = apriori_algorithm(transactions, min_support=0.01)
    
    # Find recommendations for the given barcode
    recommendations = []
    for pair, data in result['pairs'].items():
        if barcode in pair:
            # Get the other item in the pair
            other_item = pair[1] if pair[0] == barcode else pair[0]
            # Calculate confidence
            item_support = result['items'].get(barcode, 0) / result['total_transactions']
            if item_support > 0:
                confidence = data['support'] / item_support
                recommendations.append({
                    'barcode': other_item,
                    'support': data['support'],
                    'confidence': confidence,
                    'count': data['count']
                })
    
    # Sort by confidence and return top N
    recommendations.sort(key=lambda x: x['confidence'], reverse=True)
    return recommendations[:limit]


# ===== PRODUCT ENDPOINTS =====

@lru_cache(maxsize=1000)
def _get_product_by_barcode(barcode):
    barcode = barcode.strip()
    sql = """
        SELECT product_id, barcode, name, price, weight_kg, category, sub_category,
               aisle, partition_no, shelf_no, stock_quantity, position_tag
        FROM products WHERE barcode = %s
    """
    product = pg_query_one(NEON_DB_DSN, sql, (barcode,))
    if product:
        return product
    # Fallback: check store2 catalog (products2)
    sql2 = sql.replace('FROM products', 'FROM products2')
    return pg_query_one(NEON_DB_DSN, sql2, (barcode,))


@lru_cache(maxsize=1000)
def _get_product_by_id(product_id):
    sql = """
        SELECT product_id, barcode, name, price, weight_kg, category, sub_category,
               aisle, partition_no, shelf_no, stock_quantity, position_tag
        FROM products WHERE product_id = %s
    """
    product = pg_query_one(NEON_DB_DSN, sql, (product_id,))
    if product:
        return product
    # Fallback: check store2 catalog (products2)
    sql2 = sql.replace('FROM products', 'FROM products2')
    return pg_query_one(NEON_DB_DSN, sql2, (product_id,))


@app.route('/api/products/barcode', methods=['POST'])
@db_error
def lookup_product():
    """Lookup product by barcode - matches frontend API"""
    data = request.get_json() or {}
    barcode = data.get('barcode', '').strip()
    
    if not barcode:
        return jsonify({'error': 'Barcode required'}), 400
    
    product = _get_product_by_barcode(barcode)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'id': product['product_id'],
        'barcode': product['barcode'],
        'name': product['name'],
        'price': product['price'],
        'weight_kg': product['weight_kg'],
        'category': product['category'],
        'aisle': str(product['aisle']),
        'partition': str(product['partition_no']),
        'shelf': product['shelf_no'],
        'stock': product['stock_quantity']
    })

# ===== RESTOCK REMINDER LOGIC =====

def _bulk_enrich_barcodes(barcodes):
    """Fetch product details for a list of barcodes in a single query using ThreadPool.
    Returns dict: barcode -> product dict."""
    if not barcodes:
        return {}
    placeholders = ','.join(['%s'] * len(barcodes))
    sql = f"SELECT barcode, name, price, category FROM products WHERE barcode IN ({placeholders})"
    sql2 = f"SELECT barcode, name, price, category FROM products2 WHERE barcode IN ({placeholders})"
    
    # Execute both concurrently
    future1 = EXECUTOR.submit(pg_query_all, NEON_DB_DSN, sql, tuple(barcodes))
    future2 = EXECUTOR.submit(pg_query_all, NEON_DB_DSN, sql2, tuple(barcodes))
    
    try:
        rows1 = future1.result() or []
    except Exception:
        rows1 = []
    try:
        rows2 = future2.result() or []
    except Exception:
        rows2 = []
        
    result = {}
    for r in rows1 + rows2:
        if r and r.get('barcode') and r['barcode'] not in result:
            result[r['barcode']] = dict(r)
    return result

def _global_top_products(limit=6):
    """Return globally top-selling products from bill_items as fallback frequent list."""
    try:
        sql = """
            SELECT p.barcode, p.name, p.price, p.category,
                   SUM(bi.quantity) AS qty
            FROM bill_items bi
            JOIN products p ON p.barcode = bi.barcode
            GROUP BY p.barcode, p.name, p.price, p.category
            ORDER BY qty DESC
            LIMIT %s
        """
        rows = pg_query_all(NEON_DB_DSN, sql, (limit,)) or []
        result = []
        for r in rows:
            try:
                result.append({
                    'barcode': r['barcode'], 'name': r['name'],
                    'price': float(r['price']), 'category': r.get('category',''),
                    'qty': int(r.get('qty', 0)), 'last_purchased': None
                })
            except Exception:
                pass
        return result
    except Exception:
        return []

def get_restock_suggestions(customer_id):
    """Analyze purchase history to find restock candidates and frequent items.
    Always returns non-empty data by falling back to global top-sellers."""
    try:
        history = pg_query_all(
            NEON_HISTORY_DSN,
            """
            SELECT barcode, quantity, purchased_at
            FROM purchase_history
            WHERE customer_id = %s
            ORDER BY purchased_at ASC
            """,
            (customer_id,),
        ) or []
    except Exception:
        history = []
    
    if not history:
        # No personal history — return globally popular items so section always has content
        return {'restock': [], 'frequent': _global_top_products(6)}

    # Process history
    product_stats = {}
    today = datetime.now().date()

    for record in history:
        try:
            bc     = record['barcode']
            p_date = record['purchased_at'].date() if isinstance(record['purchased_at'], datetime) else record['purchased_at']
            if bc not in product_stats:
                product_stats[bc] = {'dates': [], 'total_qty': 0, 'last_date': None}
            product_stats[bc]['dates'].append(p_date)
            product_stats[bc]['total_qty'] += record.get('quantity', 1)
            product_stats[bc]['last_date'] = p_date
        except Exception:
            continue

    restock_candidates = []
    frequent_candidates = []

    for bc, stats in product_stats.items():
        try:
            dates = sorted(set(stats['dates']))
            days_since_last = (today - stats['last_date']).days

            if len(dates) > 1:
                intervals    = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_interval = sum(intervals) / len(intervals)
                if avg_interval > 0 and days_since_last >= (avg_interval * 1.1):
                    prob = min(1.0, days_since_last / (avg_interval * 2))
                    restock_candidates.append({
                        'barcode':      bc,
                        'reason':       'Overdue',
                        'days_since':   days_since_last,
                        'avg_interval': round(avg_interval, 1),
                        'score':        prob
                    })

            frequent_candidates.append({
                'barcode':         bc,
                'qty':             stats['total_qty'],
                'last_purchased':  stats['last_date'].isoformat() if stats['last_date'] else None
            })
        except Exception:
            continue

    restock_candidates.sort(key=lambda x: x['score'], reverse=True)
    frequent_candidates.sort(key=lambda x: x['qty'], reverse=True)

    # Bulk enrich — single DB round-trip for all barcodes
    all_barcodes = list({c['barcode'] for c in restock_candidates[:8]} |
                        {c['barcode'] for c in frequent_candidates[:8]})
    product_map  = _bulk_enrich_barcodes(all_barcodes)

    def enrich_list(items, limit=5):
        result = []
        for item in items:
            p = product_map.get(item['barcode'])
            if not p:
                # fallback individual lookup
                try:
                    p = _get_product_by_barcode(item['barcode'])
                except Exception:
                    pass
            if p:
                item['name']     = p['name']
                item['price']    = float(p.get('price', 0))
                item['category'] = p.get('category', '')
                result.append(item)
            if len(result) >= limit:
                break
        return result

    final_restock  = enrich_list(restock_candidates,  5)
    final_frequent = enrich_list(frequent_candidates, 5)

    # Pad frequent from global top-sellers so section always has ≥ 3 items
    if len(final_frequent) < 3:
        existing = {i['barcode'] for i in final_frequent}
        for g in _global_top_products(6):
            if g['barcode'] not in existing:
                final_frequent.append(g)
                existing.add(g['barcode'])
            if len(final_frequent) >= 5:
                break

    return {
        'restock':  final_restock,
        'frequent': final_frequent
    }

@app.route('/api/recommendations/restock/<customer_id>', methods=['GET'])
@db_error
def get_user_restock_reminders(customer_id):
    """Get personalized restock reminders and frequent purchases"""
    suggestions = get_restock_suggestions(customer_id)
    return jsonify(suggestions)


# ===== MARKET BASKET ANALYSIS — FREQUENTLY BOUGHT TOGETHER =====

# Load associations mapping (category/keyword → companion product names)
_ASSOC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'associations.json')
try:
    with open(_ASSOC_PATH, 'r', encoding='utf-8') as _af:
        _ASSOCIATIONS = json.load(_af)
except Exception as _e:
    logging.warning(f"Could not load associations.json: {_e}")
    _ASSOCIATIONS = {}


def _get_fbt_from_associations(product_name: str, product_category: str, limit: int = 5):
    """Get companion product names via category/keyword MBA rules from associations.json."""
    text = ((product_name or '') + ' ' + (product_category or '')).lower()
    companions = []
    matched_keys = []
    # Find all matching keys
    for key in _ASSOCIATIONS:
        if key.lower() in text:
            matched_keys.append(key)
    # De-duplicate companion names preserving order
    seen = set()
    for key in matched_keys:
        for c in _ASSOCIATIONS[key]:
            if c.lower() not in seen:
                seen.add(c.lower())
                companions.append(c)
    return companions[:limit * 3]  # return extra so DB lookup can trim


def _enrich_companion_names(name_hints: list, exclude_barcodes: set, limit: int = 5):
    """Resolve companion product name hints to real product records from the DB."""
    if not name_hints:
        return []
    results = []
    seen_barcodes = set(exclude_barcodes or [])
    for hint in name_hints:
        if len(results) >= limit:
            break
        try:
            sql = """
                SELECT product_id, barcode, name, price, category, aisle, position_tag
                FROM products WHERE name ILIKE %s LIMIT 1
            """
            row = pg_query_one(NEON_DB_DSN, sql, (f'%{hint}%',))
            if not row:
                sql2 = sql.replace('FROM products', 'FROM products2')
                row = pg_query_one(NEON_DB_DSN, sql2, (f'%{hint}%',))
            if row and row.get('barcode') and row['barcode'] not in seen_barcodes:
                seen_barcodes.add(row['barcode'])
                results.append(dict(row))
        except Exception:
            continue
    return results


def _get_fbt_for_barcode(barcode: str, exclude_barcodes: set, limit: int = 5):
    """
    Market Basket Analysis for a single barcode.
    1. Try real co-occurrence data from the `recommendations` table.
    2. Fall back to category-based association rules.
    Returns list of enriched product dicts.
    """
    results = []
    seen = set(exclude_barcodes or [])
    seen.add(barcode)

    # --- Step 1: Real co-occurrence from recommendations table ---
    try:
        recs = pg_query_all(
            NEON_ANALYTICS_DSN,
            """
            SELECT r.recommended_product_barcode, r.co_occurrence_count, r.confidence
            FROM recommendations r
            WHERE r.product_barcode = %s
            ORDER BY r.co_occurrence_count DESC, r.confidence DESC
            LIMIT %s
            """,
            (barcode, limit * 2),
        ) or []
        co_barcodes = [r['recommended_product_barcode'] for r in recs if r['recommended_product_barcode'] not in seen]
        if co_barcodes:
            enriched = _bulk_enrich_barcodes(co_barcodes)
            for bc in co_barcodes:
                if bc in enriched and bc not in seen:
                    seen.add(bc)
                    results.append(enriched[bc])
                if len(results) >= limit:
                    break
    except Exception as e:
        logging.warning(f"MBA co-occurrence lookup failed: {e}")

    # --- Step 2: Category-based fallback if not enough ---
    if len(results) < limit:
        try:
            product = _get_product_by_barcode(barcode)
            if product:
                name_hints = _get_fbt_from_associations(product.get('name', ''), product.get('category', ''), limit)
                fallback = _enrich_companion_names(name_hints, seen, limit - len(results))
                results.extend(fallback)
        except Exception as e:
            logging.warning(f"MBA association fallback failed: {e}")

    return results[:limit]


@app.route('/api/recommendations/fbt', methods=['POST', 'GET'])
@db_error
def get_fbt_recommendations():
    """
    Frequently Bought Together for a single product.
    POST body: { barcode, product_id, limit }
    GET params: ?barcode=...&product_id=...&limit=5
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args

    barcode = (data.get('barcode') or '').strip()
    product_id = (data.get('product_id') or '').strip()
    limit = int(data.get('limit', 5))

    if not barcode and not product_id:
        return jsonify({'error': 'barcode or product_id required'}), 400

    # Resolve barcode from product_id if needed
    if not barcode and product_id:
        p = _get_product_by_id(product_id)
        if p:
            barcode = p.get('barcode', '')

    if not barcode:
        return jsonify({'product_barcode': barcode, 'recommendations': []})

    recs = _get_fbt_for_barcode(barcode, set(), limit)
    return jsonify({
        'product_barcode': barcode,
        'recommendations': [{
            'barcode': r.get('barcode', ''),
            'name': r.get('name', ''),
            'price': float(r.get('price', 0)),
            'category': r.get('category', ''),
            'aisle': r.get('aisle'),
            'position_tag': r.get('position_tag'),
        } for r in recs]
    })


@app.route('/api/recommendations/context', methods=['POST'])
@db_error
def get_context_recommendations():
    """
    Cart-aware Market Basket Analysis.
    POST body: { cart_barcodes: [...], customer_id, limit, last_added_barcode }
    Returns FBT suggestions for all items in the cart, ranked by co-occurrence score,
    excluding items already in the cart.
    """
    data = request.get_json() or {}
    cart_barcodes = data.get('cart_barcodes', [])
    limit = int(data.get('limit', 5))
    last_added = (data.get('last_added_barcode') or '').strip()

    if not cart_barcodes:
        return jsonify({'recommendations': [], 'triggered_by': None})

    cart_set = set(str(b) for b in cart_barcodes if b)

    # Prioritise last-added item — get its FBT first
    scored = {}

    def _add_recs(barcode, weight=1.0):
        recs = _get_fbt_for_barcode(barcode, cart_set, limit * 2)
        for rec in recs:
            bc = rec.get('barcode', '')
            if bc and bc not in cart_set:
                if bc not in scored:
                    scored[bc] = {'product': rec, 'score': 0.0}
                scored[bc]['score'] += weight

    if last_added and last_added in cart_set:
        _add_recs(last_added, weight=2.0)  # boost last-added

    for bc in cart_barcodes:
        if bc != last_added:
            _add_recs(str(bc), weight=1.0)

    # Sort by score descending
    ranked = sorted(scored.values(), key=lambda x: x['score'], reverse=True)
    top = [item['product'] for item in ranked[:limit]]

    # Resolve trigger product name
    trigger_name = None
    if last_added:
        try:
            p = _get_product_by_barcode(last_added)
            if p:
                trigger_name = p.get('name')
        except Exception:
            pass

    return jsonify({
        'recommendations': [{
            'barcode': r.get('barcode', ''),
            'name': r.get('name', ''),
            'price': float(r.get('price', 0)),
            'category': r.get('category', ''),
            'aisle': r.get('aisle'),
            'position_tag': r.get('position_tag'),
        } for r in top],
        'triggered_by': trigger_name,
        'triggered_by_barcode': last_added or None,
    })


@app.route('/api/recommendations/general', methods=['GET'])
@db_error
def get_general_recommendations():
    """Get general (non-personalised) top product recommendations."""
    limit = int(request.args.get('limit', 5))
    try:
        rows = pg_query_all(
            NEON_ANALYTICS_DSN,
            """
            SELECT recommended_product_barcode as barcode, SUM(co_occurrence_count) as score
            FROM recommendations
            GROUP BY recommended_product_barcode
            ORDER BY score DESC
            LIMIT %s
            """,
            (limit * 2,),
        ) or []
        barcodes = [r['barcode'] for r in rows]
        enriched = _bulk_enrich_barcodes(barcodes)
        result = []
        for bc in barcodes:
            if bc in enriched and len(result) < limit:
                result.append(enriched[bc])
        if len(result) < limit:
            # Pad with random products
            padded = pg_query_all(
                NEON_DB_DSN,
                "SELECT barcode, name, price, category FROM products ORDER BY RANDOM() LIMIT %s",
                (limit - len(result),),
            ) or []
            existing_bcs = {r.get('barcode') for r in result}
            for r in padded:
                if r.get('barcode') not in existing_bcs:
                    result.append(dict(r))
        return jsonify({'recommendations': result[:limit]})
    except Exception as e:
        logging.warning(f"General recommendations failed: {e}")
        return jsonify({'recommendations': []})

@app.route('/api/products/similar/<barcode>', methods=['GET'])
@db_error
def get_similar_options(barcode):
    """Get similar products from the same category/sub-category"""
    product = _get_product_by_barcode(barcode)
    if not product:
        return jsonify([])
    
    # Find items in same sub-category (or category) excluding current item
    query = """
    SELECT * FROM products 
    WHERE category = %s AND barcode != %s
    """
    params = [product['category'], barcode]
    
    if product['sub_category']:
        query += " AND sub_category = %s"
        params.append(product['sub_category'])
        
    query += " ORDER BY price ASC LIMIT 5"
    
    similar_products = query_products_parallel(query, tuple(params))
    
    return jsonify([dict(p) for p in similar_products])


@app.route('/api/product/lookup', methods=['POST'])
@db_error
def lookup_product_alt():
    """Alternative endpoint for product lookup"""
    return lookup_product()

@app.route('/api/products/search', methods=['GET'])
@db_error
def search_products():
    """Search products by name or category"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    params = []
    where = "WHERE 1=1"
    if query:
        where += " AND name ILIKE %s"
        params.append(f"%{query}%")
    if category:
        where += " AND category = %s"
        params.append(category)
        
    sql = f"SELECT * FROM products {where} LIMIT 50"
    params_tuple = tuple(params)
    products = query_products_parallel(sql, params_tuple)
    return jsonify([dict(p) for p in products])

@app.route('/api/nav/status', methods=['GET'])
def get_nav_status():
    """Return current cart location and active ad."""
    if not smart_cart_service:
        return jsonify({"error": "Service not initialized"}), 500
    return jsonify(smart_cart_service.get_status())

@app.route('/api/nav/esp-status', methods=['GET'])
def get_esp_status_endpoint():
    """Detailed ESP tracking info for the Live Navigation Modal."""
    if not smart_cart_service:
        return jsonify({"position": "Service Offline"})
    
    loc = getattr(smart_cart_service, 'current_location', None)
    if loc and loc.get("partition"):
        partition = loc.get("partition")
        corridor_id = loc.get("corridor", "")
        
        # Friendly labels for AISLE mapping
        labels = {"L": "Left Corridor", "12": "Aisle 1-2", "23": "Aisle 2-3", "R": "Right Corridor"}
        lbl = labels.get(corridor_id, corridor_id)
        
        return jsonify({
            "position": f"{partition} ({lbl})",
            "partition": partition,
            "corridor": corridor_id,
            "esp": loc.get("esp", "Searching..."),
            "distance": loc.get("distance_m", 0),
            "rssi": loc.get("raw_rssi", 0)
        })
    
    return jsonify({"position": "Scanning for beacons...", "partition": None})


# ===== AUTH ENDPOINTS =====


@app.route('/api/auth/register', methods=['POST'])
@db_error
def register():
    data = request.get_json() or {}
    barcode = (data.get('barcode') or '').strip() or None
    username = (data.get('username') or '').strip() or None
    password = data.get('password') or ''
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()

    if not barcode and not username:
        return jsonify({'error': 'barcode or username required'}), 400

    if username and len(password) < 4:
        return jsonify({'error': 'password required for username login'}), 400

    existing = None
    if barcode:
        existing = get_customer_by_barcode_or_username(barcode)
    if username and not existing:
        existing = get_customer_by_barcode_or_username(username)
    if existing:
        return jsonify({'error': 'account already exists for this barcode/username'}), 409

    customer_id = f"CUST_{uuid.uuid4().hex}"
    password_hash = hash_password(password) if username else None

    pg_execute(
        NEON_AUTH_DSN,
        """
        INSERT INTO customers (customer_id, barcode, username, password_hash, name, email, is_admin)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
        """,
        (customer_id, barcode, username, password_hash, name, email),
    )

    return jsonify({
        'customer_id': customer_id,
        'barcode': barcode,
        'username': username,
        'name': name,
        'email': email,
        'is_admin': False,
    })


@app.route('/api/auth/login', methods=['POST'])
@db_error
def login():
    data = request.get_json() or {}
    identifier = (data.get('identifier') or '').strip()
    password = data.get('password') or ''

    if not identifier:
        return jsonify({'error': 'identifier required'}), 400

    customer = get_customer_by_barcode_or_username(identifier)
    if not customer:
        return jsonify({'error': 'account not found'}), 404

    # Barcode-only login allowed when identifier matches barcode and no password supplied
    if password:
        if not customer.get('password_hash') or customer['password_hash'] != hash_password(password):
            return jsonify({'error': 'invalid credentials'}), 401
    else:
        if identifier != customer.get('barcode'):
            return jsonify({'error': 'password required for username login'}), 401

    # Check if this customer is the first row (admin) OR has ID 00000001
    first_customer = pg_query_one(
        NEON_AUTH_DSN,
        """
        SELECT customer_id FROM customers 
        ORDER BY created_at ASC, customer_id ASC 
        LIMIT 1
        """,
        (),
    )
    
    is_admin = False
    
    # Check specific ID (handle int/str)
    cid = str(customer['customer_id'])
    barcode = str(customer.get('barcode', ''))
    
    # Logic: First user OR ID 1 OR Barcode 00000001
    if (first_customer and first_customer['customer_id'] == customer['customer_id']) or \
       (cid == '1') or (cid.zfill(8) == '00000001') or (barcode == '00000001'):
        is_admin = True
        
    if is_admin:
        # Ensure is_admin flag is set in database
        pg_execute(
            NEON_AUTH_DSN,
            "UPDATE customers SET is_admin = TRUE WHERE customer_id = %s",
            (customer['customer_id'],),
        )
    else:
        # Ensure is_admin flag is False for non-admin customers
        pg_execute(
            NEON_AUTH_DSN,
            "UPDATE customers SET is_admin = FALSE WHERE customer_id = %s",
            (customer['customer_id'],),
        )

    return jsonify({
        'customer_id': customer['customer_id'],
        'barcode': customer.get('barcode'),
        'username': customer.get('username'),
        'name': customer.get('name'),
        'email': customer.get('email'),
        'is_admin': is_admin,
    })

# ===== CART ENDPOINTS =====

@app.route('/api/cart/create', methods=['POST'])
@db_error
def create_cart():
    """Create new cart"""
    data = request.get_json() or {}
    cart_id = f"CART_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    customer_id = data.get('customer_id', None)
    
    pg_execute(
        NEON_CARTS_DSN,
        "INSERT INTO carts (cart_id, customer_id, status) VALUES (%s, %s, 'active')",
        (cart_id, customer_id),
    )
    
    return jsonify({'cart_id': cart_id, 'status': 'created'})

@app.route('/api/cart/<cart_id>/add', methods=['POST'])
@db_error
def add_to_cart(cart_id):
    """Add item to cart"""
    data = request.get_json() or {}
    barcode = str(data.get('barcode', '')).strip()
    quantity = int(data.get('quantity', 1)) or 1
    
    product = _get_product_by_barcode(barcode)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    existing_cart = pg_query_one(
        NEON_CARTS_DSN,
        "SELECT cart_id FROM carts WHERE cart_id = %s",
        (cart_id,),
    )
    if not existing_cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    existing = pg_query_one(
        NEON_CARTS_DSN,
        "SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s",
        (cart_id, product['product_id']),
    )
    
    if existing:
        new_quantity = existing['quantity'] + quantity
        pg_execute(
            NEON_CARTS_DSN,
            "UPDATE cart_items SET quantity = %s WHERE id = %s",
            (new_quantity, existing['id']),
        )
    else:
        pg_execute(
            NEON_CARTS_DSN,
            "INSERT INTO cart_items (cart_id, product_id, barcode, quantity, unit_price) VALUES (%s, %s, %s, %s, %s)",
            (cart_id, product['product_id'], barcode, quantity, product['price']),
        )
    
    return jsonify({'status': 'added', 'quantity': quantity})

@app.route('/api/cart/<cart_id>', methods=['GET'])
@db_error
def get_cart(cart_id):
    """Get cart contents"""
    cart_items = pg_query_all(
        NEON_CARTS_DSN,
        "SELECT id, product_id, barcode, quantity, unit_price FROM cart_items WHERE cart_id = %s",
        (cart_id,),
    )
    
    if not cart_items:
        return jsonify({
            'cart_id': cart_id,
            'items': [],
            'subtotal': 0,
            'expected_weight_kg': 0,
            'item_count': 0
        })
    
    # Fetch product details from products DB (both)
    product_ids = [item['product_id'] for item in cart_items]
    placeholders = ','.join(['%s'] * len(product_ids))
    sql = f"SELECT product_id, name, weight_kg FROM products WHERE product_id IN ({placeholders})"
    
    products = query_products_parallel(sql, tuple(product_ids))
    product_map = {p['product_id']: p for p in products}
    
    # Join data
    items = []
    for ci in cart_items:
        prod = product_map.get(ci['product_id'], {})
        items.append({
            'id': ci['id'],
            'product_id': ci['product_id'],
            'barcode': ci['barcode'],
            'quantity': ci['quantity'],
            'unit_price': ci['unit_price'],
            'name': prod.get('name', 'Unknown'),
            'weight_kg': prod.get('weight_kg', 0)
        })
    
    total_weight = sum(item['weight_kg'] * item['quantity'] for item in items)
    subtotal = sum(item['unit_price'] * item['quantity'] for item in items)
    
    return jsonify({
        'cart_id': cart_id,
        'items': items,
        'subtotal': subtotal,
        'expected_weight_kg': total_weight,
        'item_count': len(items)
    })

@app.route('/api/cart/<cart_id>/remove', methods=['POST'])
@db_error
def remove_from_cart(cart_id):
    """Remove item from cart"""
    data = request.get_json()
    product_id = data.get('product_id')
    
    pg_execute(
        NEON_CARTS_DSN,
        "DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s",
        (cart_id, product_id),
    )
    
    return jsonify({'status': 'removed'})

# ===== BILLING ENDPOINTS =====

@app.route('/api/bills', methods=['POST'])
@db_error
def generate_bill():
    """Generate bill from cart items - matches frontend API"""
    data = request.get_json() or {}
    customer_id = data.get('customer_id')
    
    # Require login for checkout
    if not customer_id:
        return jsonify({'error': 'Login required to proceed with payment'}), 401
    
    # Frontend sends items directly
    if 'items' in data:
        items_data = data.get('items') or []
        if not items_data:
            return jsonify({'error': 'items required'}), 400
        subtotal = float(data.get('subtotal', 0))
        tax = float(data.get('tax', 0))
        total = float(data.get('total', 0))
        
        # Calculate expected weight
        expected_weight = 0
        enriched_items = []
        for item in items_data:
            product_id = item.get('productId')
            qty = int(item.get('quantity', 1))
            prod = _get_product_by_id(product_id)
            if prod:
                expected_weight += prod['weight_kg'] * qty
                enriched_items.append({'product_id': product_id, 'barcode': prod['barcode'], 'quantity': qty})
        
        # Create bill
        bill_id = f"BILL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        pg_execute(
            NEON_CARTS_DSN,
            """
            INSERT INTO bills 
            (bill_id, customer_id, items_count, subtotal, tax, total_amount, expected_weight_kg, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed')
            """,
            (bill_id, customer_id, len(items_data), subtotal, tax, total, expected_weight),
        )

        # Insert bill_items for analytics
        for item in items_data:
            product_id = item.get('productId')
            qty = int(item.get('quantity', 1))
            prod = _get_product_by_id(product_id)
            if prod:
                pg_execute(
                    NEON_CARTS_DSN,
                    """
                    INSERT INTO bill_items 
                    (bill_id, product_id, product_name, barcode, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (bill_id, product_id, prod['name'], prod['barcode'], qty, prod['price'], prod['price'] * qty),
                )

        # Record history for recommendations
        record_purchase_history(customer_id, enriched_items)
        
        # Record transaction
        record_transaction(bill_id, customer_id, total, "cash")
        
        # Update recommendation co-occurrence in background
        barcodes = [item['barcode'] for item in enriched_items]
        EXECUTOR.submit(update_recommendation_cooccurrence, barcodes)
        
        return jsonify({
            'success': True,
            'billId': bill_id,
            'bill_id': bill_id,
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
            'expected_weight_kg': expected_weight
        })
    
    # Backend cart-based flow
    cart_id = data.get('cart_id')
    if not cart_id:
        return jsonify({'error': 'Cart ID or items required'}), 400
    
    cart_items = pg_query_all(
        NEON_CARTS_DSN,
        "SELECT product_id, barcode, quantity, unit_price FROM cart_items WHERE cart_id = %s",
        (cart_id,),
    )
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Fetch product details (both DBs)
    product_ids = [item['product_id'] for item in cart_items]
    placeholders = ','.join(['%s'] * len(product_ids))
    sql = f"SELECT product_id, weight_kg, barcode FROM products WHERE product_id IN ({placeholders})"
    
    products = query_products_parallel(sql, tuple(product_ids))
    product_map = {p['product_id']: p for p in products}
    
    # Join data
    items = []
    for ci in cart_items:
        prod = product_map.get(ci['product_id'], {})
        items.append({
            'product_id': ci['product_id'],
            'barcode': ci.get('barcode') or prod.get('barcode', ''),
            'quantity': ci['quantity'],
            'unit_price': ci['unit_price'],
            'weight_kg': prod.get('weight_kg', 0)
        })
    
    # Calculate totals
    subtotal = sum(item['unit_price'] * item['quantity'] for item in items)
    tax = subtotal * 0.05  # 5% tax
    total = subtotal + tax
    expected_weight = sum(item['weight_kg'] * item['quantity'] for item in items)
    
    # Create bill
    bill_id = f"BILL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    pg_execute(
        NEON_CARTS_DSN,
        """
        INSERT INTO bills 
        (bill_id, cart_id, customer_id, items_count, subtotal, tax, total_amount, expected_weight_kg, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
        """,
        (bill_id, cart_id, customer_id, len(items), subtotal, tax, total, expected_weight),
    )
    
    pg_execute(
        NEON_CARTS_DSN,
        "UPDATE carts SET status = 'billed' WHERE cart_id = %s",
        (cart_id,),
    )

    # Record history
    record_purchase_history(
        customer_id,
        [{'barcode': item['barcode'], 'quantity': item['quantity']} for item in items],
    )
    
    # Record transaction
    record_transaction(bill_id, customer_id, total, "cash")
    
    # Update recommendation co-occurrence in the background
    barcodes = [item['barcode'] for item in items]
    EXECUTOR.submit(update_recommendation_cooccurrence, barcodes)
    
    return jsonify({
        'bill_id': bill_id,
        'cart_id': cart_id,
        'items': len(items),
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'expected_weight_kg': expected_weight,
        'status': 'pending'
    })

@app.route('/api/bill/generate', methods=['POST'])
@db_error
def generate_bill_alt():
    """Alternative endpoint for bill generation"""
    return generate_bill()

@app.route('/api/bill/<bill_id>', methods=['GET'])
@db_error
def get_bill(bill_id):
    """Get bill details"""
    bill = pg_query_one(
        NEON_CARTS_DSN,
        "SELECT * FROM bills WHERE bill_id = %s",
        (bill_id,),
    )
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    return jsonify(dict(bill))

# ===== CUSTOMER HISTORY =====

@app.route('/api/customer/history', methods=['GET'])
@db_error
def get_customer_history():
    customer_id = request.args.get('customer_id')
    limit = request.args.get('limit', 50, type=int)
    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400
    rows = pg_query_all(
        NEON_HISTORY_DSN,
        """
        SELECT barcode, quantity, purchased_at
        FROM purchase_history
        WHERE customer_id = %s
        ORDER BY purchased_at DESC
        LIMIT %s
        """,
        (customer_id, limit),
    )
    return jsonify(rows)

@app.route('/api/customer/transactions', methods=['GET'])
@db_error
def get_customer_transactions():
    """Get transaction history for a customer."""
    customer_id = request.args.get('customer_id')
    limit = request.args.get('limit', 50, type=int)
    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400
    rows = pg_query_all(
        NEON_HISTORY_DSN,
        """
        SELECT transaction_id, bill_id, payment_method, amount, timestamp
        FROM transactions
        WHERE customer_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """,
        (customer_id, limit),
    )
    return jsonify(rows)

@app.route('/api/forecast/<product_id>', methods=['GET'])
@db_error
def get_demand_forecast(product_id):
    """Get demand forecast for a product."""
    limit = request.args.get('limit', 30, type=int)
    rows = pg_query_all(
        NEON_ANALYTICS_DSN,
        """
        SELECT forecast_date, predicted_quantity, actual_quantity, forecast_accuracy
        FROM demand_forecast
        WHERE product_id = %s
        ORDER BY forecast_date DESC
        LIMIT %s
        """,
        (product_id, limit),
    )
    return jsonify(rows)

# ===== RECOMMENDATIONS ENDPOINTS =====

RECOMMENDATION_RULES = {
    "Bakery": ["Dairy", "Beverages"],
    "Dairy": ["Bakery", "Snacks"],
    "Snacks": ["Beverages", "Dairy"],
    "Beverages": ["Snacks", "Bakery"],
    "Grains": ["Dairy", "Household"],
    "Personal Care": ["Personal Care", "Household"],
    "Household": ["Personal Care", "Snacks"],
}

COMPLEMENTARY_KEYWORDS = {
    "milk": ["bread", "biscuit", "cookie", "eggs", "butter", "cereal", "choco"],
    "bread": ["jam", "butter", "cheese", "eggs", "milk", "sauce", "mayo"],
    "biscuit": ["tea", "coffee", "milk"],
    "cookie": ["tea", "coffee", "milk"],
    "tea": ["biscuit", "sugar", "milk", "cookie"],
    "coffee": ["biscuit", "sugar", "milk", "cookie"],
    "rice": ["dal", "oil", "spice", "bean", "chana"],
    "dal": ["rice", "spice", "oil", "ghee"],
    "atta": ["oil", "ghee", "rice", "spice"],
    "flour": ["oil", "ghee", "rice"],
    "oil": ["rice", "dal", "atta", "flour", "spice"],
    "ghee": ["rice", "dal", "atta"],
    "pasta": ["sauce", "cheese", "mayo"],
    "noodle": ["sauce", "eggs", "ketchup"],
    "sauce": ["pasta", "noodle", "bread", "snack"],
    "chips": ["cola", "pepsi", "juice", "drink"],
    "snack": ["cola", "pepsi", "juice", "drink"],
    "cola": ["chips", "snack", "pizza", "burger"],
    "pepsi": ["chips", "snack", "pizza", "burger"],
    "drink": ["chips", "snack", "biscuit"],
    "juice": ["chips", "snack", "biscuit"],
    "soap": ["shampoo", "conditioner", "wash", "paste"],
    "shampoo": ["conditioner", "soap", "oil", "wash"],
    "paste": ["brush", "wash", "soap"],
    "brush": ["paste", "wash"],
    "detergent": ["cleaner", "liquid", "wash"],
    "cleaner": ["detergent", "scrub", "liquid", "wash"],
    "diaper": ["wipes", "powder", "lotion", "baby"],
    "baby": ["diaper", "wipes", "powder", "lotion"],
}

def fetch_products_by_category(categories: List[str], exclude_barcodes: List[str], limit: int):
    if not categories:
        return []
    placeholders = ','.join(['%s'] * len(categories))
    exclude_placeholders = ','.join(['%s'] * len(exclude_barcodes)) if exclude_barcodes else None
    sql = f"""
        SELECT product_id, barcode, name, price, category, position_tag, aisle
        FROM products
        WHERE category IN ({placeholders})
    """
    params = categories
    if exclude_barcodes:
        sql += f" AND barcode NOT IN ({exclude_placeholders})"
        params += exclude_barcodes
    sql += " LIMIT %s"
    params.append(limit)
    
    products = query_products_parallel(sql, tuple(params))
    # Add id field for frontend compatibility
    return [{**p, 'id': p['product_id']} for p in products]


def fetch_history_recs(customer_id: str, exclude_barcodes: List[str], limit: int):
    if not customer_id:
        return []
    # Fetch purchase history
    history = pg_query_all(
        NEON_HISTORY_DSN,
        """
        SELECT barcode, SUM(quantity) as freq
        FROM purchase_history
        WHERE customer_id = %s
        GROUP BY barcode
        ORDER BY freq DESC
        LIMIT %s
        """,
        (customer_id, limit),
    )
    
    if not history:
        return []
    
    # Fetch product details
    barcodes = [h['barcode'] for h in history if h['barcode'] not in exclude_barcodes]
    if not barcodes:
        return []
    
    placeholders = ','.join(['%s'] * len(barcodes))
    products = query_products_parallel(
        f"SELECT product_id, barcode, name, price, category, position_tag, aisle FROM products WHERE barcode IN ({placeholders})",
        tuple(barcodes),
    )
    
    # Join with frequencies
    barcode_to_freq = {h['barcode']: h['freq'] for h in history}
    result = []
    for prod in products:
        result.append({
            **prod,
            'id': prod['product_id'],  # Add id field for frontend compatibility
            'freq': barcode_to_freq.get(prod['barcode'], 0)
        })
    return result


def fetch_products_by_barcodes(barcodes: List[str]):
    if not barcodes:
        return []
    placeholders = ','.join(['%s'] * len(barcodes))
    products = pg_query_all(
        NEON_PRODUCTS_DSN,
        f"SELECT product_id, barcode, name, price, category, position_tag, aisle FROM products WHERE barcode IN ({placeholders})",
        tuple(barcodes),
    )
    # Add id field for frontend compatibility
    return [{**p, 'id': p['product_id']} for p in products]


def fetch_cooccurrence_recs(barcodes: List[str], exclude_barcodes: List[str], limit: int):
    """Get recommendations based on co-occurrence data."""
    if not barcodes:
        return []
    placeholders = ','.join(['%s'] * len(barcodes))
    exclude_placeholders = ','.join(['%s'] * len(exclude_barcodes)) if exclude_barcodes else None
    sql = f"""
        SELECT recommended_product_barcode, SUM(co_occurrence_count) as total_count
        FROM recommendations
        WHERE product_barcode IN ({placeholders})
    """
    params = barcodes
    if exclude_barcodes:
        sql += f" AND recommended_product_barcode NOT IN ({exclude_placeholders})"
        params += exclude_barcodes
    sql += " GROUP BY recommended_product_barcode ORDER BY total_count DESC LIMIT %s"
    params.append(limit)
    rec_barcodes = pg_query_all(NEON_ANALYTICS_DSN, sql, tuple(params))
    
    if not rec_barcodes:
        return []
    
    # Fetch product details
    barcode_list = [r['recommended_product_barcode'] for r in rec_barcodes]
    placeholders_prod = ','.join(['%s'] * len(barcode_list))
    sql = f"SELECT product_id, barcode, name, price, category FROM products WHERE barcode IN ({placeholders_prod})"
    products = query_products_parallel(sql, tuple(barcode_list))
    
    # Join with counts
    barcode_to_count = {r['recommended_product_barcode']: r['total_count'] for r in rec_barcodes}
    result = []
    for prod in products:
        result.append({
            **prod,
            'id': prod['product_id'],  # Add id field for frontend compatibility
            'co_occurrence_count': barcode_to_count.get(prod['barcode'], 0)
        })
    return result


@app.route('/api/recommendations/<category>', methods=['GET'])
@db_error
def get_recommendations_by_category(category):
    """Get product recommendations by category - matches frontend API"""
    limit = request.args.get('limit', 5, type=int)
    recs = fetch_products_by_category([category], [], limit)
    return jsonify([dict(r) for r in recs])


@app.route('/api/recommendations', methods=['GET'])
@db_error
def get_recommendations():
    """Get product recommendations by barcode (same-category)"""
    barcode = request.args.get('barcode')
    limit = request.args.get('limit', 5, type=int)
    
    if not barcode:
        return jsonify({'error': 'Barcode required'}), 400
    
    # Check Primary DB
    product = pg_query_one(NEON_PRODUCTS_DSN, "SELECT category FROM products WHERE barcode = %s", (barcode,))
    # Check Secondary DB
    if not product:
        product = pg_query_one(NEON_PRODUCTS_2_DSN, "SELECT category FROM products WHERE barcode = %s", (barcode,))
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    sql = """
        SELECT barcode, name, price
        FROM products
        WHERE category = %s AND barcode != %s
        LIMIT %s
    """
    recommendations = query_products_parallel(sql, (product['category'], barcode, limit))
    
    return jsonify({
        'barcode': barcode,
        'recommendations': [dict(r) for r in recommendations]
    })


@app.route('/api/recommendations/context_old', methods=['POST'])
@db_error
def get_context_recommendations_old():
    """Contextual recommendations based on cart items + customer history."""
    data = request.get_json() or {}
    cart_barcodes = data.get('cart_barcodes') or []
    customer_id = data.get('customer_id')
    limit = int(data.get('limit', 6))

    cart_barcodes = [str(bc).strip() for bc in cart_barcodes if bc]

    categories = []
    if cart_barcodes:
        placeholders = ','.join(['%s'] * len(cart_barcodes))
        sql = f"SELECT barcode, category FROM products WHERE barcode IN ({placeholders})"
        rows = query_products_parallel(sql, tuple(cart_barcodes))
        categories = list({r['category'] for r in rows})

    # Rule-based categories
    rule_categories = []
    for cat in categories:
        rule_categories.extend(RECOMMENDATION_RULES.get(cat, []))

    # Apriori algorithm recommendations (highest priority)
    recs_apriori = []
    if cart_barcodes:
        for barcode in cart_barcodes[:3]:  # Limit to first 3 items to avoid too many calls
            apriori_recs = get_apriori_recommendations(barcode, limit=3)
            recs_apriori.extend(apriori_recs)
    
    # Get product details for Apriori recommendations
    if recs_apriori:
        apriori_barcodes = [r['barcode'] for r in recs_apriori]
        apriori_products = fetch_products_by_barcodes(apriori_barcodes)
        # Merge confidence scores
        barcode_to_confidence = {r['barcode']: r['confidence'] for r in recs_apriori}
        recs_apriori_final = []
        for prod in apriori_products:
            if prod['barcode'] in barcode_to_confidence:
                prod['confidence'] = barcode_to_confidence[prod['barcode']]
                recs_apriori_final.append(prod)
        recs_apriori = recs_apriori_final
    
    recs_rule = fetch_products_by_category(rule_categories, cart_barcodes, limit // 4) if rule_categories else []
    hist_rows = fetch_history_recs(customer_id, cart_barcodes, limit // 4)
    hist_barcodes = [r['barcode'] for r in hist_rows]
    recs_history = fetch_products_by_barcodes(hist_barcodes)
    
    # Co-occurrence recommendations from analytics DB
    recs_cooccur = fetch_cooccurrence_recs(cart_barcodes, cart_barcodes, limit // 4)

    # Keyword-Based Complementary Recommendations (Highest Priority)
    recs_complementary = []
    if cart_barcodes:
        cart_products = fetch_products_by_barcodes(cart_barcodes)
        target_keywords = set()
        for p in cart_products:
            name_lower = str(p.get('name', '')).lower()
            for key, matches in COMPLEMENTARY_KEYWORDS.items():
                if key in name_lower:
                    target_keywords.update(matches)
        
        if target_keywords:
            kw_conditions = " OR ".join([f"LOWER(name) LIKE %s" for _ in target_keywords])
            kw_params = [f"%{kw}%" for kw in target_keywords]
            sql = f"SELECT barcode, name, price, category, position_tag FROM products WHERE ({kw_conditions})"
            if cart_barcodes:
                sql += f" AND barcode NOT IN ({','.join(['%s']*len(cart_barcodes))})"
                kw_params.extend(cart_barcodes)
            sql += f" LIMIT {limit}"
            
            comp_rows = pg_query_all(NEON_PRODUCTS_DSN, sql, tuple(kw_params)) or []
            for r in comp_rows:
                recs_complementary.append({
                    'barcode': r.get('barcode'),
                    'name': r.get('name'),
                    'price': r.get('price'),
                    'category': r.get('category'),
                    'position_tag': r.get('position_tag')
                })

    combined = []
    seen = set(cart_barcodes)
    # Prioritize: Complementary > Apriori > co-occurrence > history > rules
    for r in recs_complementary + recs_apriori + recs_cooccur + recs_history + recs_rule:
        bc = r['barcode']
        if bc in seen:
            continue
        seen.add(bc)
        combined.append(r)
        if len(combined) >= limit:
            break

    return jsonify({'recommendations': combined})

# ===== WEIGHT VERIFICATION ENDPOINTS =====

@app.route('/api/weight/verify', methods=['POST'])
@db_error
def verify_weight():
    """Verify weight at exit scale"""
    data = request.get_json()
    bill_id = data.get('bill_id')
    actual_weight = data.get('actual_weight')
    tolerance = data.get('tolerance', 0.5)  # 500 grams default
    
    bill = pg_query_one(
        NEON_CARTS_DSN,
        "SELECT expected_weight_kg FROM bills WHERE bill_id = %s",
        (bill_id,),
    )
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    expected_weight = bill['expected_weight_kg']
    variance = abs(actual_weight - expected_weight)
    status = 'verified' if variance <= tolerance else 'suspect'
    
    pg_execute(
        NEON_CARTS_DSN,
        "UPDATE bills SET actual_weight_kg = %s, weight_variance_kg = %s, status = %s WHERE bill_id = %s",
        (actual_weight, variance, status, bill_id),
    )
    pg_execute(
        NEON_CARTS_DSN,
        """
        INSERT INTO weight_readings 
        (bill_id, expected_weight, actual_weight, variance, tolerance_threshold, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (bill_id, expected_weight, actual_weight, variance, tolerance, status),
    )
    
    return jsonify({
        'bill_id': bill_id,
        'expected_weight_kg': expected_weight,
        'actual_weight_kg': actual_weight,
        'variance_kg': variance,
        'tolerance_kg': tolerance,
        'status': status,
        'message': 'Weight verified' if status == 'verified' else 'Weight mismatch - staff intervention needed'
    })

# ===== ANALYTICS ENDPOINTS =====

@app.route('/api/analytics/sales', methods=['GET'])
@db_error
def get_sales_analytics():
    """Get sales analytics with optional month/year filtering"""
    month = request.args.get('month', type=int)  # 1-12
    year = request.args.get('year', type=int)
    
    # If month and year provided, return daily data for that entire month
    if month and year:
        analytics = pg_query_all(
            NEON_CARTS_DSN,
            """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as transactions,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_bill
            FROM bills
            WHERE EXTRACT(YEAR FROM created_at) = %s
              AND EXTRACT(MONTH FROM created_at) = %s
              AND status != 'cancelled'
            GROUP BY DATE(created_at)
            ORDER BY date ASC
            """,
            (year, month),
        )
    else:
        # Default: last 30 days, daily breakdown
        analytics = pg_query_all(
            NEON_CARTS_DSN,
            """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as transactions,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_bill
            FROM bills
            WHERE status != 'cancelled'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
            """,
            (),
        )
    
    result = []
    for row in analytics:
        item = dict(row)
        # Convert date to string for JSON serialization
        if 'date' in item and item['date']:
            item['date'] = item['date'].isoformat()
        result.append(item)
    
    return jsonify(result)

@app.route('/api/analytics/inventory', methods=['GET'])
@db_error
def get_inventory_status():
    """Get inventory status"""
    sql = """
        SELECT product_id, name, category, stock_quantity, reorder_level,
               CASE 
                   WHEN stock_quantity <= reorder_level THEN 'reorder_needed'
                   WHEN stock_quantity <= reorder_level * 2 THEN 'low'
                   ELSE 'ok'
               END as status
        FROM products
        ORDER BY stock_quantity ASC
    """
    inventory = query_products_parallel(sql, ())
    return jsonify([dict(i) for i in inventory])

@app.route('/api/analytics/customers', methods=['GET'])
@db_error
def get_customer_count():
    """Get total customer count"""
    count = pg_query_one(
        NEON_AUTH_DSN,
        "SELECT COUNT(*) as count FROM customers",
        (),
    )
    return jsonify({'count': count['count'] if count else 0})

@app.route('/api/analytics/highest-sales', methods=['GET'])
@db_error
def get_highest_sales():
    """Get highest selling products"""
    products = pg_query_all(
        NEON_PRODUCTS_DSN,
        """
        SELECT 
            p.product_id, 
            p.name, 
            p.category, 
            p.stock_quantity,
            COALESCE(SUM(bi.quantity), 0) as total_sold
        FROM products p
        LEFT JOIN bill_items bi ON p.barcode = bi.barcode
        GROUP BY p.product_id, p.name, p.category, p.stock_quantity
        ORDER BY total_sold DESC, p.stock_quantity DESC
        LIMIT 10
        """,
        (),
    )
    return jsonify([dict(p) for p in products])

@app.route('/api/analytics/lowest-sales', methods=['GET'])
@db_error
def get_lowest_sales():
    """Get lowest selling products (need restock)"""
    products = pg_query_all(
        NEON_PRODUCTS_DSN,
        """
        SELECT product_id, name, category, stock_quantity, reorder_level,
               CASE 
                   WHEN stock_quantity <= reorder_level THEN 'reorder_needed'
                   WHEN stock_quantity <= reorder_level * 2 THEN 'low'
                   ELSE 'ok'
               END as status
        FROM products
        WHERE stock_quantity <= reorder_level * 2
        ORDER BY stock_quantity ASC
        LIMIT 10
        """,
        (),
    )
    return jsonify([dict(p) for p in products])

@app.route('/api/analytics/products/performance', methods=['GET'])
@db_error
def get_product_performance():
    """Get best and worst selling products based on bill items"""
    limit = request.args.get('limit', 5, type=int)

    # Primary query: from bill_items (direct-items checkout flow)
    best_sellers_sql = """
        SELECT
            bi.product_id,
            bi.product_name AS name,
            p.category,
            SUM(bi.quantity) AS total_sold,
            SUM(bi.total_price) AS revenue
        FROM bill_items bi
        LEFT JOIN products p ON p.product_id = bi.product_id
        WHERE bi.product_id IS NOT NULL
        GROUP BY bi.product_id, bi.product_name, p.category
        ORDER BY total_sold DESC, revenue DESC
        LIMIT %s
    """

    worst_sellers_sql = """
        SELECT
            bi.product_id,
            bi.product_name AS name,
            p.category,
            SUM(bi.quantity) AS total_sold,
            SUM(bi.total_price) AS revenue
        FROM bill_items bi
        LEFT JOIN products p ON p.product_id = bi.product_id
        WHERE bi.product_id IS NOT NULL
        GROUP BY bi.product_id, bi.product_name, p.category
        ORDER BY total_sold ASC, revenue ASC
        LIMIT %s
    """

    try:
        best_sellers  = pg_query_all(NEON_CARTS_DSN, best_sellers_sql,  (limit,))
        worst_sellers = pg_query_all(NEON_CARTS_DSN, worst_sellers_sql, (limit,))

        def serialize(rows):
            out = []
            for p in rows:
                d = dict(p)
                # normalise field names for frontend renderMiniTable
                d['total_sold'] = int(d.get('total_sold') or 0)
                d['revenue']    = float(d.get('revenue') or 0)
                d['category']   = d.get('category') or 'General'
                out.append(d)
            return out

        return jsonify({
            'best_sellers':  serialize(best_sellers),
            'worst_sellers': serialize(worst_sellers)
        })
    except Exception as e:
        logging.error(f"Error fetching product performance: {e}")
        return jsonify({'best_sellers': [], 'worst_sellers': []})


# ===== HEALTH CHECK =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'service': 'SmartRetailX Backend API'
    })

@app.route('/api/products/count', methods=['GET'])
@db_error
def product_count():
    """Quick count to verify imports across Neon and SQLite."""
    neon = pg_query_one(NEON_PRODUCTS_DSN, "SELECT COUNT(*) AS count FROM products", ())
    carts_bills = pg_query_one(NEON_CARTS_DSN, "SELECT COUNT(*) AS count FROM bills", ())
    return jsonify({
        'products_neon': neon['count'] if neon else 0,
        'bills_neon': carts_bills['count'] if carts_bills else 0
    })

# ===== ESP NAVIGATION & CALIBRATION INTEGRATION =====

# Configuration — 4 corridor-based ESP32 beacons (using existing device names)
ESP_NAMES = ["ESP32_AISLE_1", "ESP32_AISLE_2", "ESP32_AISLE_3", "ESP32_AISLE_4"]
CALIBRATION_FILE = "calibration_config.json"
SCAN_DURATION_INITIAL = 5
RSSI_THRESHOLD = -90

# Corridor → Partition mapping
# Each corridor provides access to specific partition ranges
CORRIDOR_PARTITIONS = {
    "L":  list(range(101, 107)),   # P101-P106: A1 left side
    "12": list(range(107, 119)),   # P107-P118: A1 right + A2 left
    "23": list(range(119, 131)),   # P119-P130: A2 right + A3 left
    "R":  list(range(131, 137)),   # P131-P136: A3 right side
}

# ESP name → corridor ID mapping
# ESP32_AISLE_1 placed in Left corridor, _2 in Corr-12, _3 in Corr-23, _4 in Corr-R
ESP_TO_CORRIDOR = {
    "ESP32_AISLE_1": "L",
    "ESP32_AISLE_2": "12",
    "ESP32_AISLE_3": "23",
    "ESP32_AISLE_4": "R",
}

# Global State for Nav
nav_state = {
    "graph_builder": None,
    "market_basket": None,
    "path_finder": None,
    "calibration_config": {}
}

def init_nav_system():
    """Initialize DB Graph and Market Basket for Path Finding"""
    try:
        if DBGraphBuilder is None:
            logging.warning("?? Navigation modules not found. Navigation features disabled.")
            return

        # Use local SQLite DB
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "smartretail.db")
        
        if DBGraphBuilder:
            from path_planner import MarketBasket as JsonMarketBasket
            gb = DBGraphBuilder(db_path)
            mb = DBMarketBasket(db_path)
            pf = PathFinder(gb, mb)
            # JSON-based market basket for richer nav recommendations
            assoc_path = os.path.join(base_dir, 'associations.json')
            json_mb = JsonMarketBasket(assoc_path) if os.path.exists(assoc_path) else mb

            nav_state["graph_builder"] = gb
            nav_state["market_basket"] = mb
            nav_state["json_basket"]    = json_mb
            nav_state["path_finder"] = pf
            logging.info("? Navigation System Initialized (Graph & MarketBasket)")
        else:
            logging.warning("?? Navigation classes missing. Features disabled.")
        
        # Load calibration
        if os.path.exists(CALIBRATION_FILE):
            try:
                with open(CALIBRATION_FILE, 'r') as f:
                    nav_state["calibration_config"] = json.load(f)
                logging.info("? Loaded Calibration Data")
            except Exception as e:
                logging.error(f"Failed to load calibration: {e}")
    except Exception as e:
        logging.error(f"? Failed to init Navigation System: {e}")

# Trigger init on import/start
init_nav_system()


# --- BLE HELPER ---
async def scan_ble_devices(duration=5.0):
    """Scan for BLE devices and return {name: median_rssi}"""
    try:
        rssi_data = {name: [] for name in ESP_NAMES}
        
        def callback(device, advertisement_data):
            if device.name in ESP_NAMES:
                if advertisement_data.rssi > RSSI_THRESHOLD:
                    rssi_data[device.name].append(advertisement_data.rssi)

        scanner = BleakScanner(callback)
        await scanner.start()
        await asyncio.sleep(duration)
        await scanner.stop()
        
        medians = {}
        for name, values in rssi_data.items():
            if values:
                medians[name] = sorted(values)[len(values) // 2]
        return medians
    except Exception as e:
        logging.warning(f"BLE Scan failed (ESP32 tracking unavailable): {e}")
        return {}


def estimate_partition(rssi_map, corridor_id=None):
    """
    Corridor-based fingerprint location estimation.
    rssi_map: dict of {esp_name: rssi_value} for current scan.
    corridor_id: strongest corridor detected (L, 12, 23, R).
    Returns partition tag (e.g. 'P119') of best-matching position.
    """
    config = nav_state.get("calibration_config", {})
    corridors_data = config.get("corridors", config.get("aisles", {}))
    
    if not corridors_data or not corridor_id:
        # Fallback: no calibration loaded, use corridor midpoint
        if corridor_id is None: return None
        parts = CORRIDOR_PARTITIONS.get(corridor_id, [])
        if not parts: return None
        # Find the ESP that maps to this corridor

        esp_name = next((n for n, c in ESP_TO_CORRIDOR.items() if c == corridor_id), None)

        rssi = rssi_map.get(esp_name) if esp_name else None

        if rssi is None: return f"P{parts[len(parts) // 2]}"
        # Linear mapping: stronger signal = closer to ESP (placed at start of corridor)
        old_cfg = {"max_rssi": -30, "min_rssi": -90}
        normalized = min(max(rssi, old_cfg["min_rssi"]), old_cfg["max_rssi"])
        strength = (normalized - old_cfg["min_rssi"]) / (old_cfg["max_rssi"] - old_cfg["min_rssi"])
        index = min(int(strength * len(parts)), len(parts) - 1)
        return f"P{parts[index]}"

    # --- Fingerprint nearest-neighbor ---
    POSITION_TO_FRACTION = {"start": 0, "middle": 0.5, "end": 1.0}

    best_dist = float('inf')
    best_partition = None

    for corr_id_str, positions in corridors_data.items():
        # Only check the matching corridor if we received one
        if corridor_id and corr_id_str != corridor_id:
            continue
            
        parts = CORRIDOR_PARTITIONS.get(corr_id_str, [])
        if not parts: continue
        
        for pos_name, fingerprint in positions.items():
            # Euclidean distance in RSSI space
            sq_dist = 0.0
            count = 0
            for esp, cal_rssi in fingerprint.items():
                cur_rssi = rssi_map.get(esp)
                if cur_rssi is not None and cal_rssi is not None:
                    sq_dist += (cur_rssi - cal_rssi) ** 2
                    count += 1
                elif cal_rssi is not None:
                    sq_dist += 60 ** 2  # penalty for missing ESP
                    count += 1
            
            dist = (sq_dist / count) ** 0.5 if count else float('inf')
            
            if dist < best_dist:
                best_dist = dist
                # Map position name to a partition index within this corridor
                frac = POSITION_TO_FRACTION.get(pos_name, 0.5)
                idx = min(int(frac * (len(parts) - 1) + 0.5), len(parts) - 1)
                best_partition = f"P{parts[max(0, idx)]}"

    return best_partition




# --- NAV ENDPOINTS ---
@app.route('/api/nav/esp-status', methods=['GET'])

def get_esp_status():

    """Return live position from background BLE scanner."""

    # Read from background service (avoids BLE adapter conflict)

    if smart_cart_service:

        loc = getattr(smart_cart_service, 'current_location', None)

        if loc and loc.get("partition"):

            corridor_id = loc.get("corridor", "")

            partition = loc.get("partition", "")

            corridor_labels = {"L": "Corr-L", "12": "Corr-A1A2", "23": "Corr-A2A3", "R": "Corr-R"}

            label = corridor_labels.get(corridor_id, "")

            return jsonify({

                "position": f"{partition} ({label})" if label else partition,

                "corridor": corridor_id,

                "partition": partition,

                "esp": loc.get("esp", ""),

                "rssi": loc.get("raw_rssi", 0),
                "smoothed_rssi": loc.get("smoothed_rssi", 0),

            })

    return jsonify({"position": "Scanning..."})





@app.route('/api/nav/locate', methods=['POST'])
def nav_locate():
    """Return high-accuracy filtered location using corridor-based ESP32s from tracker engine."""
    try:
        if smart_cart_service:
            loc = getattr(smart_cart_service, 'current_location', None)
            if loc and loc.get("partition"):
                corridor_to_aisle = {"L": 1, "12": 1, "23": 2, "R": 3}
                return jsonify({
                    "status": "located",
                    "corridor": loc.get("corridor"),
                    "aisle": corridor_to_aisle.get(loc.get("corridor"), 0),
                    "esp_name": loc.get("esp"),
                    "rssi": loc.get("raw_rssi", 0),
                    "smoothed_rssi": loc.get("smoothed_rssi", 0),
                    "partition": loc.get("partition"),
                    "all_signals": loc.get("all_smoothed", {})
                })
        return jsonify({"status": "wandering", "message": "Location unknown"}), 200
        
    except Exception as e:
        logging.error(f"Locate Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/nav/path-suggestions', methods=['GET'])
def nav_path_suggestions():
    customer_id = request.args.get('customer_id')
    target_partition = request.args.get('target', type=int)
    
    if not customer_id or not target_partition:
        return jsonify([])

    # 1. Fetch barcodes from user's history
    try:
        history_rows = pg_query_all(
            NEON_HISTORY_DSN,
            "SELECT barcode FROM purchase_history WHERE customer_id = %s ORDER BY purchased_at DESC LIMIT 100",
            (customer_id,)
        )
    except Exception as e:
        logging.error(f"Path suggestions DB error: {e}")
        return jsonify([])

    if not history_rows:
        return jsonify([])
        
    barcodes = list(set([str(r['barcode']) for r in history_rows if r.get('barcode')]))
    if not barcodes:
        return jsonify([])

    # 2. Fetch product details from local DB
    placeholders = ','.join(['?'] * len(barcodes))
    query = f"SELECT barcode, name, price, aisle, partition_no, shelf_no, side, position_tag FROM products WHERE barcode IN ({placeholders})"
    
    try:
        products = query_db(query, tuple(barcodes))
    except Exception as e:
        logging.error(f"Path suggestions local DB error: {e}")
        return jsonify([])

    # 3. Filter to find items "On The Path"
    # Helper to determine which corridor accesses a partition
    def get_corridor(p):
        if p >= 101 and p <= 106: return 'L'
        if p >= 107 and p <= 118: return '12'
        if p >= 119 and p <= 130: return '23'
        return 'R'
        
    def get_index(p):
        res = (p - 100) % 12
        if res == 0: res = 12
        return (res - 1) % 6  # 0 to 5

    try:
        target_corr = get_corridor(target_partition)
        target_idx  = get_index(target_partition)
    except:
        return jsonify([])

    suggestions = []
    seen = set()
    
    for prod in products:
        pno = prod.get('partition_no')
        if not pno: continue
        try:
            pno = int(pno)
        except:
            continue
            
        # Don't suggest the target item itself
        if pno == target_partition:
            continue

        prod_corr = get_corridor(pno)
        prod_idx  = get_index(pno)

        # "On the path" means same corridor, and index >= target_index 
        # (since entrance is below index 5, you walk from 5 down to target_idx)
        if prod_corr == target_corr and prod_idx >= target_idx:
            # Add if not seen
            bc = prod['barcode']
            if bc not in seen:
                seen.add(bc)
                suggestions.append(dict(prod))
                if len(suggestions) >= 3:
                    break
                    
    return jsonify(suggestions)


@app.route('/api/nav/path', methods=['GET'])
def nav_path():
    start_node = request.args.get('start_node', 'Entry')
    target_product = request.args.get('target_product')
    if not target_product:
        return jsonify({'success': False, 'message': 'Missing target'}), 400

    # Use path_finder directly (fast SQLite lookup) — no BLE wait.
    pf = nav_state.get("path_finder")
    gb = nav_state.get("graph_builder")
    if not pf or not gb:
        return jsonify({'success': False, 'message': 'PathFinder not initialized'}), 500

    # ── Resolve start node ──────────────────────────────────────────────
    # 'Entry' is a virtual node that doesn't exist in the graph.
    # Substitute with the lowest-numbered partition as starting position.
    effective_start = start_node
    if start_node not in gb.graph:
        partitions_map = gb.get_partitions_by_aisle()
        sorted_aisles  = sorted(partitions_map.keys())
        if sorted_aisles:
            first_parts    = sorted(partitions_map[sorted_aisles[0]])
            effective_start = first_parts[0] if first_parts else None
    try:
        # ── Look up product location (always from SQLite) ────────────────
        target_info = gb.get_product_location(target_product)
        if not target_info:
            return jsonify({'success': False, 'message': f'Product "{target_product}" not found in store'}), 400

        target_node  = target_info.get('position')
        target_aisle = target_info.get('aisle')

        # ── AI Recommendations: pick products at different nodes along route ──
        # Strategy: get unique position tags (≠ target) from SQLite, ordered by
        # their graph distance from effective_start → target; take 2 stops.
        recommendation_stops = []
        try:
            import networkx as nx
            seen_nodes = {target_node}
            
            # Fetch all unique positions from Neon DB to leverage full catalog
            neon_candidates = pg_query_all(
                NEON_PRODUCTS_DSN,
                """
                SELECT position_tag, aisle, name, barcode
                FROM products
                WHERE position_tag != %s
                AND position_tag IS NOT NULL
                """,
                (target_node,)
            )
            
            if neon_candidates:
                # Convert to DataFrame-like structure for easy scoring
                import pandas as pd
                candidates_df = pd.DataFrame(neon_candidates, columns=['position_tag', 'aisle', 'name', 'barcode'])
                
                # Extract meaningful keywords from target product
                ignore_words = {'and', 'the', 'with', 'for', 'pack', 'size', 'attr'}
                target_words = {w.lower() for w in target_product.replace('-', ' ').split() 
                                if len(w) > 3 and w.lower() not in ignore_words}
                
                def calculate_rec_score_neon(row):
                    name = str(row['name']).lower()
                    pos_tag = row['position_tag']
                    
                    # Only consider positions that exist in our graph
                    if pos_tag not in gb.graph:
                        return -9999
                        
                    # 1. Semantic match (+100 per keyword)
                    kw_score = sum(100 for w in target_words if w in name)
                    
                    # 2. Same Aisle (+50)
                    aisle_score = 50 if str(row['aisle']) == str(target_aisle) else 0
                    
                    # 3. Distance penalty (-distance)
                    try:
                        dist = len(nx.shortest_path(gb.graph, effective_start, pos_tag)) if effective_start else 999
                    except:
                        dist = 999
                        
                    return kw_score + aisle_score - dist

                candidates_df['score'] = candidates_df.apply(calculate_rec_score_neon, axis=1)
                
                # Debug logging to see why candidates are failing
                top_scores = candidates_df.sort_values('score', ascending=False).head(5)
                logging.info(f"Top 5 raw recommendation scores for {target_product}:\n{top_scores[['name', 'position_tag', 'score']]}")
                
                # Filter out ones without valid routes (-9999)
                candidates_df = candidates_df[candidates_df['score'] > -5000]
                
                # Sort by highest score first
                on_route = candidates_df.sort_values('score', ascending=False)
                
                for _, row in on_route.iterrows():
                    if len(recommendation_stops) >= 2:
                        break
                    pos = row['position_tag']
                    if pos in seen_nodes:
                        continue
                        
                    seen_nodes.add(pos)
                    recommendation_stops.append({
                        'name': row['name'],
                        'barcode': row['barcode'] or '',
                        'node': pos,
                        'aisle': int(row['aisle']),
                        'confidence': 0.75
                    })
        except Exception as rec_err:
            logging.warning(f"Nav recommendation error (non-fatal): {rec_err}")



        # ── Build multi-stop route ────────────────────────────────────────
        route     = []
        rec_node  = recommendation_stops[0]['node'] if recommendation_stops else None
        rec_name  = recommendation_stops[0]['name'] if recommendation_stops else None

        if effective_start:
            try:
                import networkx as nx
                prev = effective_start
                full_route = []
                # Route through each recommendation stop
                stops_to_visit = [s['node'] for s in recommendation_stops] + [target_node]
                for stop_node in stops_to_visit:
                    if stop_node not in gb.graph:
                        continue
                    try:
                        seg = nx.shortest_path(gb.graph, prev, stop_node)
                        full_route.extend(seg[:-1])
                        prev = stop_node
                    except Exception:
                        pass
                full_route.append(prev)  # append the final node
                route = full_route
            except Exception as pe:
                logging.warning(f"Multi-stop pathfinding error: {pe}")

        return jsonify({
            'success': True,
            'target': target_info.get('name', target_product),
            'target_node': target_node,
            'target_aisle': target_aisle,
            'recommendation': rec_name,
            'recommendation_node': rec_node,
            'recommendation_stops': recommendation_stops,
            'route': route
        })
    except Exception as e:
        logging.error(f"nav_path error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/api/voice_search', methods=['POST'])
def voice_search_api():
    try:
        if not voice_assistant_service:
            return jsonify({"success": False, "message": "VoiceAssistantService not initialized"}), 500
        result = voice_assistant_service.api_voice_search()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/nav/ads/dual', methods=['GET'])
def nav_ads_dual():
    """Get two featured products for the advertisement boxes"""
    aisle = request.args.get('aisle', type=int)
    partition = request.args.get('partition')

    # Fetch 2 random products from the database to serve as deals
    sql = "SELECT product_id, barcode, name, price, category, position_tag, aisle FROM products ORDER BY RANDOM() LIMIT 2"
    products = pg_query_all(NEON_PRODUCTS_DSN, sql, ())
    
    if not products or len(products) < 1:
        return jsonify({"message": "No ads available"}), 404

    ad1 = products[0]
    ad2 = products[1] if len(products) > 1 else products[0]

    return jsonify({
        "box1": {
            "title": ad1['name'],
            "description": f"Grab this top pick from {ad1.get('category', 'our store')}!",
            "product_id": ad1['barcode'],
            "image_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=300&h=120",
            "product_data": ad1
        },
        "box2": {
            "title": ad2['name'],
            "description": f"Special Offer! Get {ad2['name']} today.",
            "product_id": ad2['barcode'],
            "image_url": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&q=80&w=300&h=120",
            "product_data": ad2
        }
    })


# --- CALIBRATION ENDPOINTS ---

@app.route('/api/admin/calibration/status', methods=['GET'])
def calibration_status():
    """Check if a valid calibration exists"""
    config = nav_state.get("calibration_config", {})
    has_calibration = bool(config.get("corridors", config.get("aisles")))
    calibrated_at = config.get("calibrated_at", None)
    corridor_count = len(config.get("corridors", config.get("aisles", {})))
    return jsonify({
        "calibrated": has_calibration,
        "calibrated_at": calibrated_at,
        "corridor_count": corridor_count,
        "esp_names": ESP_NAMES
    })


@app.route('/api/admin/calibration/capture', methods=['POST'])
def calibration_capture():
    """
    Scan all ESPs for `duration` seconds and return RSSI medians per ESP.
    Called once per (aisle, position) step in the wizard.
    """
    data = request.get_json() or {}
    duration = int(data.get('duration', 7))

    async def scan_all():
        rssi_buckets = {name: [] for name in ESP_NAMES}
        def cb(dev, adv):
            if dev.name in rssi_buckets:
                rssi_buckets[dev.name].append(adv.rssi)
        scanner = BleakScanner(cb)
        await scanner.start()
        await asyncio.sleep(duration)
        await scanner.stop()
        return rssi_buckets

    try:
        buckets = asyncio.run(scan_all())
        results = {}
        for esp, vals in buckets.items():
            if vals:
                vals_sorted = sorted(vals)
                mid = len(vals_sorted) // 2
                results[esp] = vals_sorted[mid]   # median RSSI
            else:
                results[esp] = None               # ESP not detected
        return jsonify({"success": True, "rssi": results, "samples": {k: len(v) for k, v in buckets.items()}})
    except Exception as e:
        logging.error(f"Calibration capture error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/calibration/save', methods=['POST'])
def calibrate_save():
    """
    Save the full fingerprint map to file.
    Expects body: { "corridors": { "L": { "start": {esp: rssi, ...}, "middle": {...}, "end": {...} }, ... } }
    """
    data = request.get_json() or {}
    corridors = data.get("corridors", data.get("aisles"))
    if not corridors:
        return jsonify({"error": "No corridor fingerprints provided"}), 400

    config = {
        "calibrated_at": datetime.utcnow().isoformat() + "Z",
        "corridors": corridors
    }
    try:
        nav_state["calibration_config"] = config
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logging.info(f"✅ Calibration saved for {len(corridors)} corridors")
        return jsonify({"success": True, "calibrated_at": config["calibrated_at"], "corridor_count": len(corridors)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ===== ADVERTISEMENT SYSTEM =====

@app.route('/api/admin/ads/setup', methods=['POST'])
def ads_setup():
    """Create advertisements and ad_impressions tables if they don't exist."""
    try:
        with get_pg_conn(NEON_PRODUCTS_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS advertisements (
                        ad_id SERIAL PRIMARY KEY,
                        product_id VARCHAR,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        image_url VARCHAR(500),
                        position_tag VARCHAR(20),
                        aisle INT,
                        is_compulsory BOOLEAN DEFAULT FALSE,
                        priority INT DEFAULT 0,
                        revenue_per_impression NUMERIC(10,2) DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                    CREATE TABLE IF NOT EXISTS ad_impressions (
                        id SERIAL PRIMARY KEY,
                        ad_id INT REFERENCES advertisements(ad_id) ON DELETE CASCADE,
                        customer_id VARCHAR,
                        position_tag VARCHAR(20),
                        aisle INT,
                        shown_at TIMESTAMP DEFAULT NOW(),
                        revenue_earned NUMERIC(10,2) DEFAULT 0
                    );
                """)
                conn.commit()
        return jsonify({"success": True, "message": "Ad tables ready"})
    except Exception as e:
        logging.error(f"Ad setup error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/nav/ads', methods=['GET'])
def nav_get_ads():
    """
    Returns 1 ad per partition for the customer's detected aisle.
    Query params: aisle, customer_id
    Returns list of {ad_id, position_tag, title, description, image_url, product_id}
    """
    aisle = request.args.get('aisle', type=int)
    customer_id = request.args.get('customer_id', '')

    if not aisle:
        return jsonify({"ads": []}), 200

    try:
        # Get all partitions in this aisle from the graph builder
        partitions = []
        if nav_state.get("graph_builder"):
            partitions_map = nav_state["graph_builder"].get_partitions_by_aisle()
            partitions = partitions_map.get(aisle, [])

        if not partitions:
            # Fallback: derive from CSV dataframe
            df = nav_state["graph_builder"].df if nav_state.get("graph_builder") else None
            if df is not None:
                aisle_df = df[df['Aisle_No'] == aisle]
                partitions = sorted(aisle_df['Position_Tag'].dropna().unique().tolist())

        # Get ads already shown to this customer today (to avoid repeating)
        shown_today = set()
        if customer_id:
            rows = pg_query_all(
                NEON_PRODUCTS_DSN,
                """SELECT ad_id FROM ad_impressions 
                   WHERE customer_id=%s AND shown_at > NOW() - INTERVAL '24 hours'""",
                (customer_id,)
            )
            if rows:
                shown_today = {r[0] for r in rows}

        # Fetch all active ads for this aisle
        all_ads = pg_query_all(
            NEON_PRODUCTS_DSN,
            """SELECT ad_id, position_tag, title, description, image_url, product_id,
                      is_compulsory, priority, revenue_per_impression
               FROM advertisements
               WHERE is_active=TRUE AND (aisle=%s OR aisle IS NULL)
               ORDER BY is_compulsory DESC, priority DESC, RANDOM()""",
            (aisle,)
        ) or []

        # Separate compulsory from regular
        compulsory = [r for r in all_ads if r[6]]
        regular    = [r for r in all_ads if not r[6] and r[0] not in shown_today]
        fallback   = [r for r in all_ads if not r[6] and r[0] in shown_today]

        ordered_pool = compulsory + regular + fallback

        # Map: 1 ad per partition
        result = []
        pool_idx = 0
        used_ads = set()
        for pt in partitions:
            # Find the best ad specifically for this partition, or fallback to pool
            pt_specific = [r for r in ordered_pool
                           if r[1] == pt and r[0] not in used_ads]
            candidate = pt_specific[0] if pt_specific else None
            if not candidate:
                while pool_idx < len(ordered_pool):
                    c = ordered_pool[pool_idx]
                    pool_idx += 1
                    if c[0] not in used_ads:
                        candidate = c
                        break

            if candidate:
                used_ads.add(candidate[0])
                result.append({
                    "ad_id":        candidate[0],
                    "position_tag": pt,
                    "title":        candidate[2],
                    "description":  candidate[3] or "",
                    "image_url":    candidate[4] or "",
                    "product_id":   candidate[5] or "",
                    "revenue_per_impression": float(candidate[8] or 0)
                })
        # No more ads — placeholder
                result.append({
                    "ad_id": None,
                    "position_tag": pt,
                    "title": f"Explore Aisle {aisle}",
                    "description": "Check out great deals here!",
                    "image_url": "",
                    "product_id": "",
                    "revenue_per_impression": 0
                })

        return jsonify({"ads": result, "aisle": aisle, "partitions": partitions})

    except Exception as e:
        logging.error(f"Nav ads error: {e}")
        return jsonify({"ads": [], "error": str(e)}), 200


@app.route('/api/nav/ads/dual', methods=['GET'])
def nav_get_dual_ads():
    """
    Returns exactly two distinct ads for persistent dashboard boxes:
    - box2 (Compulsory/Priority): Global compulsory ad or highest global priority.
    - box1 (Location/Dynamic): Ad matching aisle/partition, falling back to next highest global priority.
    """
    aisle = request.args.get('aisle', type=int)
    partition = request.args.get('partition', '')

    try:
        # Fetch all active ads
        all_ads = pg_query_all(
            NEON_PRODUCTS_DSN,
            """SELECT ad_id, position_tag, title, description, image_url, product_id,
                      is_compulsory, priority, revenue_per_impression, aisle
               FROM advertisements
               WHERE is_active=TRUE
               ORDER BY is_compulsory DESC, priority DESC, RANDOM()""",
            ()
        ) or []

        box1 = None
        box2 = None

        if not all_ads:
            return jsonify({"box1": None, "box2": None}), 200

        # --- Box 2 (Compulsory / Highest Global Priority) ---
        # First ad is mathematically guaranteed by the ORDER BY clause to be either Compulsory or highest priority
        b2_row = all_ads[0]
        box2 = {
            "ad_id": b2_row['ad_id'],
            "position_tag": b2_row['position_tag'],
            "title": b2_row['title'],
            "description": b2_row['description'] or "",
            "image_url": b2_row['image_url'] or "",
            "product_id": b2_row['product_id'] or "",
            "revenue": float(b2_row['revenue_per_impression'] or 0)
        }
        
        # --- Box 1 (Location / Dynamic Fallback) ---
        remaining_ads = [r for r in all_ads if r['ad_id'] != b2_row['ad_id']]
        b1_row = None

        if aisle:
            # Try to find an exact aisle/partition match
            if partition:
                exact_matches = [r for r in remaining_ads if r['aisle'] == aisle and r['position_tag'] == partition]
                if exact_matches: b1_row = exact_matches[0]
            
            # Try to find any aisle match
            if not b1_row:
                aisle_matches = [r for r in remaining_ads if r['aisle'] == aisle]
                if aisle_matches: b1_row = aisle_matches[0]
        
        # Fallback: Just take the next best ad
        if not b1_row and remaining_ads:
            b1_row = remaining_ads[0]
            
        if b1_row:
            box1 = {
                "ad_id": b1_row['ad_id'],
                "position_tag": b1_row['position_tag'],
                "title": b1_row['title'],
                "description": b1_row['description'] or "",
                "image_url": b1_row['image_url'] or "",
                "product_id": b1_row['product_id'] or "",
                "revenue": float(b1_row['revenue_per_impression'] or 0)
            }
            
        return jsonify({"box1": box1, "box2": box2}), 200

    except Exception as e:
        logging.error(f"Dual Ads error: {e}")
        return jsonify({"box1": None, "box2": None, "error": str(e)}), 200


@app.route('/api/nav/ads/impression', methods=['POST'])
def log_ad_impression():
    """Log an ad impression when shown to customer."""
    data = request.get_json() or {}
    ad_id = data.get('ad_id')
    customer_id = data.get('customer_id', '')
    position_tag = data.get('position_tag', '')
    aisle = data.get('aisle', 0)
    revenue = data.get('revenue_per_impression', 0)

    if not ad_id:
        return jsonify({"success": False}), 400
    try:
        pg_query_all(
            NEON_PRODUCTS_DSN,
            """INSERT INTO ad_impressions (ad_id, customer_id, position_tag, aisle, revenue_earned)
               VALUES (%s, %s, %s, %s, %s)""",
            (ad_id, customer_id, position_tag, aisle, revenue)
        )
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Ad impression log error: {e}")
        return jsonify({"error": str(e)}), 500


# --- ADMIN AD CRUD ---

@app.route('/api/admin/ads', methods=['GET'])
def admin_list_ads():
    """List all advertisements."""
    try:
        rows = pg_query_all(
            NEON_PRODUCTS_DSN,
            """SELECT ad_id, title, description, image_url, position_tag, aisle,
                      is_compulsory, priority, revenue_per_impression, is_active, created_at, product_id
               FROM advertisements ORDER BY is_compulsory DESC, priority DESC, ad_id DESC""",
            ()
        ) or []
        ads = []
        for r in rows:
            ads.append({
                "ad_id": r['ad_id'], "title": r['title'], "description": r['description'],
                "image_url": r['image_url'], "position_tag": r['position_tag'], "aisle": r['aisle'],
                "is_compulsory": r['is_compulsory'], "priority": r['priority'],
                "revenue_per_impression": float(r['revenue_per_impression'] or 0),
                "is_active": r['is_active'],
                "created_at": r['created_at'].isoformat() if r['created_at'] else None,
                "product_id": r['product_id']
            })
        return jsonify({"ads": ads})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/ads', methods=['POST'])
def admin_create_ad():
    """Create a new advertisement."""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({"error": "Title required"}), 400
    try:
        row = pg_query_one(
            NEON_PRODUCTS_DSN,
            """INSERT INTO advertisements (title, description, image_url, position_tag, aisle,
                   is_compulsory, priority, revenue_per_impression, product_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ad_id""",
            (
                title,
                data.get('description', ''),
                data.get('image_url', ''),
                data.get('position_tag') or None,
                data.get('aisle') or None,
                bool(data.get('is_compulsory', False)),
                int(data.get('priority', 0)),
                float(data.get('revenue_per_impression', 0)),
                data.get('product_id') or None
            )
        )
        return jsonify({"success": True, "ad_id": row['ad_id'] if row else None})
    except Exception as e:
        logging.error(f"Create ad error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/ads/<int:ad_id>', methods=['PATCH'])
def admin_update_ad(ad_id):
    """Update an advertisement's fields."""
    data = request.get_json() or {}
    allowed = ['title', 'description', 'image_url', 'position_tag', 'aisle',
               'is_compulsory', 'priority', 'revenue_per_impression', 'is_active']
    sets, vals = [], []
    for field in allowed:
        if field in data:
            sets.append(f"{field}=%s")
            vals.append(data[field])
    if not sets:
        return jsonify({"error": "Nothing to update"}), 400
    vals.append(ad_id)
    try:
        pg_query_all(NEON_PRODUCTS_DSN,
                     f"UPDATE advertisements SET {', '.join(sets)} WHERE ad_id=%s", tuple(vals))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/ads/<int:ad_id>', methods=['DELETE'])
def admin_delete_ad(ad_id):
    """Delete an advertisement."""
    try:
        pg_query_all(NEON_PRODUCTS_DSN,
                     "DELETE FROM advertisements WHERE ad_id=%s", (ad_id,))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/ads/dashboard', methods=['GET'])
def admin_ads_dashboard():
    """Ad monitoring: total impressions, revenue, top ads, recent impressions."""
    try:
        summary = pg_query_one(NEON_PRODUCTS_DSN,
            "SELECT COUNT(*) as total_imp, COALESCE(SUM(revenue_earned),0) as total_rev FROM ad_impressions", ())
        top_ads = pg_query_all(NEON_PRODUCTS_DSN,
            """SELECT a.ad_id, a.title, COUNT(i.id) as impressions,
                      COALESCE(SUM(i.revenue_earned),0) as revenue
               FROM advertisements a
               LEFT JOIN ad_impressions i ON a.ad_id=i.ad_id
               GROUP BY a.ad_id, a.title
               ORDER BY impressions DESC LIMIT 10""", ()) or []
        recent = pg_query_all(NEON_PRODUCTS_DSN,
            """SELECT a.title, i.customer_id, i.position_tag, i.aisle, i.shown_at, i.revenue_earned
               FROM ad_impressions i JOIN advertisements a ON i.ad_id=a.ad_id
               ORDER BY i.shown_at DESC LIMIT 50""", ()) or []

        return jsonify({
            "total_impressions": summary['total_imp'] if summary else 0,
            "total_revenue":     float(summary['total_rev']) if summary else 0,
            "top_ads": [{"ad_id": r['ad_id'], "title": r['title'],
                         "impressions": r['impressions'], "revenue": float(r['revenue'])} for r in top_ads],
            "recent_impressions": [{"title": r['title'], "customer_id": r['customer_id'],
                                    "position_tag": r['position_tag'], "aisle": r['aisle'],
                                    "shown_at": r['shown_at'].isoformat() if r['shown_at'] else None,
                                    "revenue": float(r['revenue_earned'])} for r in recent]
        })
    except Exception as e:
        logging.error(f"Ads dashboard error: {e}")
        return jsonify({"error": str(e)}), 500


# ===== AI FEATURE ENDPOINTS =====

@app.route('/api/ai/cart-analysis', methods=['POST'])
@db_error
def ai_cart_analysis():
    """
    Analyse a list of barcodes (the customer's current cart) and return:
      - spend breakdown by category
      - cart health score (0-100)
      - an AI-generated personalised tip
    """
    data   = request.get_json() or {}
    barcodes = data.get('barcodes', [])
    prices   = data.get('prices', {})          # optional barcode->price map from frontend
    quantities = data.get('quantities', {})    # optional barcode->qty map

    if not barcodes:
        return jsonify({'score': 0, 'breakdown': {}, 'tip': 'Add items to your cart to see insights.', 'label': 'Empty Cart'})

    # Fetch product details
    enriched = _bulk_enrich_barcodes(barcodes)

    # Build breakdown
    breakdown = {}
    total_spend = 0.0
    for bc in barcodes:
        p = enriched.get(bc, {})
        cat = (p.get('category') or 'Other').strip()
        unit_price = float(p.get('price') or prices.get(bc, 0))
        qty  = int(quantities.get(bc, 1))
        line = unit_price * qty
        breakdown[cat] = breakdown.get(cat, 0.0) + line
        total_spend += line

    # Score heuristic
    #   - Balanced cart (>=3 categories) = high base score
    #   - Penalise if >60% spend in single category
    num_cats = len(breakdown)
    score = min(40 + num_cats * 12, 80)
    dominant_pct = (max(breakdown.values()) / total_spend * 100) if total_spend > 0 else 0
    if dominant_pct > 60:
        score -= int((dominant_pct - 60) / 4)
    score = max(10, min(100, score))

    # Label
    if score >= 80:
        label = 'Excellent'
    elif score >= 60:
        label = 'Well Balanced'
    elif score >= 40:
        label = 'Moderate'
    else:
        label = 'Needs Variety'

    # Tip
    dominant_cat = max(breakdown, key=breakdown.get) if breakdown else 'items'
    deficit_cats  = [c for c in ['Grains', 'Pulses', 'Beverages', 'Snacks', 'Oils'] if c not in breakdown]
    if num_cats < 2:
        tip = f'Your cart is mostly {dominant_cat}. Add other categories for a balanced shop.'
    elif dominant_pct > 60:
        tip = f'{int(dominant_pct)}% of your spend is on {dominant_cat}. Consider balancing with {deficit_cats[0] if deficit_cats else "other"} items.'
    elif score >= 80:
        tip = 'Great cart diversity! You\'re shopping smartly across multiple categories.'
    else:
        tip = f'Good variety! Adding {deficit_cats[0] if deficit_cats else "more essentials"} could improve your score.'

    return jsonify({
        'score': score,
        'label': label,
        'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
        'total_spend': round(total_spend, 2),
        'tip': tip,
        'num_categories': num_cats
    })


@app.route('/api/ai/price-sensitivity', methods=['POST'])
@db_error
def ai_price_sensitivity():
    """
    Given a category, returns average price, min, max, and a trend label
    derived from products in that category.
    """
    data     = request.get_json() or {}
    category = data.get('category', '').strip()

    if not category:
        return jsonify({'error': 'category required'}), 400

    sql = """
        SELECT price FROM products WHERE LOWER(category) = LOWER(%s)
    """
    rows  = pg_query_all(NEON_DB_DSN, sql, (category,)) or []
    rows2 = pg_query_all(NEON_DB_DSN, sql.replace('FROM products', 'FROM products2'), (category,)) or []
    all_rows = rows + rows2

    if not all_rows:
        return jsonify({'category': category, 'avg_price': 0, 'min': 0, 'max': 0, 'trend': 'stable', 'insight': 'No data available for this category.'})

    prices_list = [float(r['price']) for r in all_rows if r.get('price')]
    avg_p = sum(prices_list) / len(prices_list)
    min_p = min(prices_list)
    max_p = max(prices_list)

    # Simulated trend from spread
    spread = max_p - min_p
    if spread / avg_p > 0.5:
        trend   = 'volatile'
        insight = f'{category} prices vary widely (₹{min_p:.0f}–₹{max_p:.0f}). Compare before buying.'
    elif avg_p > 200:
        trend   = 'premium'
        insight = f'{category} is a premium segment with avg ₹{avg_p:.0f}. Look for deals.'
    else:
        trend   = 'stable'
        insight = f'{category} is competitively priced at avg ₹{avg_p:.0f}. Good value.'

    return jsonify({
        'category':  category,
        'avg_price': round(avg_p, 2),
        'min':       round(min_p, 2),
        'max':       round(max_p, 2),
        'count':     len(prices_list),
        'trend':     trend,
        'insight':   insight
    })


@app.route('/api/ai/smart-suggestions', methods=['GET'])
@db_error
def ai_smart_suggestions():
    """
    Autocomplete / smart suggestion engine.
    Returns up to 8 matching product names / categories for a partial query.
    """
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'suggestions': []})

    sql = """
        SELECT DISTINCT name, category FROM products
        WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(category) LIKE LOWER(%s)
        LIMIT 8
    """
    pattern = f'%{q}%'
    rows    = pg_query_all(NEON_DB_DSN, sql, (pattern, pattern)) or []
    rows2   = pg_query_all(NEON_DB_DSN, sql.replace('FROM products', 'FROM products2'), (pattern, pattern)) or []

    seen  = set()
    suggs = []
    for r in rows + rows2:
        name = r.get('name', '')
        cat  = r.get('category', '')
        if name and name not in seen:
            suggs.append({'label': name, 'type': 'product', 'category': cat})
            seen.add(name)
        if cat and cat not in seen and len(suggs) < 8:
            suggs.append({'label': cat, 'type': 'category', 'category': cat})
            seen.add(cat)

    # Sort: exact prefix matches first
    suggs.sort(key=lambda x: (0 if x['label'].lower().startswith(q.lower()) else 1, x['label']))

    return jsonify({'suggestions': suggs[:8], 'query': q})


@app.route('/api/analytics/category-breakdown', methods=['GET'])
@db_error
def analytics_category_breakdown():
    """
    Returns purchase count and revenue per product category.
    Used for the admin dashboard donut chart.
    """
    sql = """
        SELECT p.category,
               COUNT(ph.id)       AS purchases,
               COALESCE(SUM(ph.quantity * p.price), 0) AS revenue
        FROM   purchase_history ph
        JOIN   products p ON p.barcode = ph.barcode
        GROUP  BY p.category
        ORDER  BY revenue DESC
    """
    rows  = pg_query_all(NEON_HISTORY_DSN, sql, ()) or []

    # Also try products2
    sql2  = sql.replace('JOIN   products', 'JOIN   products2')
    rows2 = pg_query_all(NEON_HISTORY_DSN, sql2, ()) or []

    combined = {}
    for r in rows + rows2:
        cat = r.get('category') or 'Other'
        combined[cat] = {
            'category': cat,
            'purchases': combined.get(cat, {}).get('purchases', 0) + int(r.get('purchases', 0)),
            'revenue':   combined.get(cat, {}).get('revenue', 0.0) + float(r.get('revenue', 0))
        }

    # Fallback: if no history data, pull from product catalog counts
    if not combined:
        fallback_sql = """
            SELECT category, COUNT(*) as purchases, SUM(price) as revenue
            FROM products GROUP BY category ORDER BY purchases DESC
        """
        fallback = pg_query_all(NEON_DB_DSN, fallback_sql, ()) or []
        for r in fallback:
            cat = r.get('category') or 'Other'
            combined[cat] = {
                'category': cat,
                'purchases': int(r.get('purchases', 0)),
                'revenue':   float(r.get('revenue', 0))
            }

    result = sorted(combined.values(), key=lambda x: x['revenue'], reverse=True)
    return jsonify(result)


@app.route('/api/analytics/heatmap', methods=['GET'])
@db_error
def analytics_heatmap():
    """
    Returns aisle-level purchase density data for the admin heatmap visualisation.
    Each entry has aisle number and a density score (0-100).
    """
    sql = """
        SELECT p.aisle, COUNT(ph.id) AS hits
        FROM   purchase_history ph
        JOIN   products p ON p.barcode = ph.barcode
        WHERE  p.aisle IS NOT NULL
        GROUP  BY p.aisle
        ORDER  BY p.aisle
    """
    rows    = pg_query_all(NEON_HISTORY_DSN, sql, ()) or []
    sql2    = sql.replace('JOIN   products', 'JOIN   products2')
    rows2   = pg_query_all(NEON_HISTORY_DSN, sql2, ()) or []

    aisle_hits = {}
    for r in rows + rows2:
        a    = int(r.get('aisle') or 0)
        if a:
            aisle_hits[a] = aisle_hits.get(a, 0) + int(r.get('hits', 0))

    # Fallback: use product distribution
    if not aisle_hits:
        fallback_sql = "SELECT aisle, COUNT(*) as hits FROM products WHERE aisle IS NOT NULL GROUP BY aisle"
        for r in (pg_query_all(NEON_DB_DSN, fallback_sql, ()) or []):
            a = int(r.get('aisle') or 0)
            if a:
                aisle_hits[a] = aisle_hits.get(a, 0) + int(r.get('hits', 0))

    max_hits = max(aisle_hits.values(), default=1)
    result = [
        {
            'aisle':   a,
            'hits':    h,
            'density': round(h / max_hits * 100)
        }
        for a, h in sorted(aisle_hits.items())
    ]
    return jsonify(result)





# ===== INVENTORY API =====

@app.route('/api/inventory/all', methods=['GET'])
@db_error
def get_inventory_all():
    sql = "SELECT product_id, barcode, name, price, weight_kg, category, sub_category, aisle, partition_no, shelf_no, position_tag, side, stock_quantity, reorder_level FROM products ORDER BY name"
    rows = pg_query_all(NEON_DB_DSN, sql, ()) or []
    sql2 = sql.replace("FROM products", "FROM products2")
    rows2 = pg_query_all(NEON_DB_DSN, sql2, ()) or []
    
    seen = set()
    unique_rows = []
    for r in rows + rows2:
        if r['barcode'] not in seen:
            seen.add(r['barcode'])
            unique_rows.append(r)
            
    return jsonify(unique_rows)

@app.route('/api/inventory/update', methods=['POST'])
@db_error
def post_inventory_update():
    data = request.get_json() or {}
    barcode = data.get('barcode')
    qty = data.get('quantity')
    if barcode and qty is not None:
        rc1 = pg_execute(NEON_DB_DSN, "UPDATE products SET stock_quantity = %s WHERE barcode = %s", (qty, barcode))
        rc2 = pg_execute(NEON_DB_DSN, "UPDATE products2 SET stock_quantity = %s WHERE barcode = %s", (qty, barcode))
        if rc1 or rc2:
            return jsonify({"status": "success"})
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"error": "Invalid data"}), 400

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# ===== RUN SERVER =====

if __name__ == '__main__':
    init_pools()
    app.run(host='0.0.0.0', port=5000)

