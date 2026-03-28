import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)

# Neon DB connections
NEON_ANALYTICS_DSN = os.getenv(
    "NEON_ANALYTICS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
NEON_PRODUCTS_DSN = os.getenv(
    "NEON_PRODUCTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
NEON_CARTS_DSN = os.getenv(
    "NEON_CARTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def get_pg_conn(dsn):
    return psycopg2.connect(dsn, sslmode="require")

def pg_query_all(dsn, sql, params):
    with get_pg_conn(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def get_frequently_bought_together(product_id, limit=5):
    """Recommendation based on co-occurrence from Neon DBs"""
    # Get product barcode first
    product = pg_query_all(
        NEON_PRODUCTS_DSN,
        "SELECT barcode FROM products WHERE product_id = %s",
        (product_id,),
    )
    if not product:
        return []
    
    barcode = product[0]['barcode']
    
    # Get co-occurrence recommendations from analytics DB
    recs = pg_query_all(
        NEON_ANALYTICS_DSN,
        """
        SELECT recommended_product_barcode, co_occurrence_count
        FROM recommendations
        WHERE product_barcode = %s
        ORDER BY co_occurrence_count DESC
        LIMIT %s
        """,
        (barcode, limit),
    )
    
    if not recs:
        return []
    
    # Get product details
    barcodes = [r['recommended_product_barcode'] for r in recs]
    placeholders = ','.join(['%s'] * len(barcodes))
    products = pg_query_all(
        NEON_PRODUCTS_DSN,
        f"SELECT product_id, barcode, name, price FROM products WHERE barcode IN ({placeholders})",
        tuple(barcodes),
    )
    
    # Join data
    barcode_to_count = {r['recommended_product_barcode']: r['co_occurrence_count'] for r in recs}
    result = []
    for prod in products:
        result.append({
            'product_id': prod['product_id'],
            'name': prod['name'],
            'price': prod['price'],
            'frequency': barcode_to_count.get(prod['barcode'], 0)
        })
    
    return result

@app.route('/api/recommendations/fbt', methods=['GET'])
def get_fbt():
    """Get frequently bought together"""
    product_id = request.args.get('product_id')
    limit = request.args.get('limit', 5, type=int)
    
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400
    
    recs = get_frequently_bought_together(product_id, limit)
    
    return jsonify({
        'product_id': product_id,
        'recommendations': [
            {'product_id': r[0], 'name': r[1], 'price': r[2], 'frequency': r[3]}
            for r in recs
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

