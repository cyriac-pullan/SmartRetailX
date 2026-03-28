import os
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import psycopg2
import psycopg2.extras

# Neon DB connections
NEON_PRODUCTS_DSN = os.getenv(
    "NEON_PRODUCTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
NEON_HISTORY_DSN = os.getenv(
    "NEON_HISTORY_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
NEON_CARTS_DSN = os.getenv(
    "NEON_CARTS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)
NEON_ANALYTICS_DSN = os.getenv(
    "NEON_ANALYTICS_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

def get_pg_conn(dsn):
    return psycopg2.connect(dsn, sslmode="require")

def pg_query_all(dsn, sql, params):
    with get_pg_conn(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()

def forecast_demand(product_id, days_ahead=7):
    """Simple linear regression forecasting using Neon DB"""
    # Get product barcode first
    product = pg_query_all(
        NEON_PRODUCTS_DSN,
        "SELECT barcode FROM products WHERE product_id = %s",
        (product_id,),
    )
    if not product:
        return None
    
    barcode = product[0]['barcode']
    
    # Get historical sales from purchase history
    history = pg_query_all(
        NEON_HISTORY_DSN,
        """
        SELECT DATE(purchased_at) as date, SUM(quantity) as quantity
        FROM purchase_history
        WHERE barcode = %s
        GROUP BY DATE(purchased_at)
        ORDER BY date DESC
        LIMIT 30
        """,
        (barcode,),
    )
    
    # Fallback to bills if not enough history
    if len(history) < 5:
        # Try getting from bills via transactions
        history = pg_query_all(
            NEON_CARTS_DSN,
            """
            SELECT DATE(created_at) as date, COUNT(*) as quantity
            FROM bills
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 30
            """,
            (),
        )
    
    if len(history) < 5:
        return None  # Not enough data
    
    # Prepare data
    X = np.array(range(len(history))).reshape(-1, 1)
    y = np.array([float(h['quantity']) for h in history])
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Forecast
    future_X = np.array(range(len(history), len(history) + days_ahead)).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    # Store forecast in analytics DB
    try:
        with get_pg_conn(NEON_ANALYTICS_DSN) as conn:
            with conn.cursor() as cur:
                for i, pred in enumerate(predictions):
                    forecast_date = (datetime.now() + timedelta(days=i+1)).date()
                    cur.execute("""
                        INSERT INTO demand_forecast (product_id, forecast_date, predicted_quantity)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (product_id, forecast_date, int(max(0, pred))))
            conn.commit()
    except Exception as e:
        print(f"Warning: Could not save forecast: {e}")
    
    return {
        'product_id': product_id,
        'forecast_days': days_ahead,
        'predictions': [max(0, int(p)) for p in predictions.tolist()],
        'confidence': float(model.score(X, y))
    }

if __name__ == '__main__':
    # Example forecast
    forecast = forecast_demand('PROD00001', 7)
    if forecast:
        print(f"Forecast for {forecast['product_id']}:")
        print(f"Predictions: {forecast['predictions']}")
        print(f"Confidence: {forecast['confidence']:.2%}")
    else:
        print("Not enough historical data for forecasting")

