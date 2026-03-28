import os
import psycopg2
from psycopg2 import sql

def get_connection(db_url=None):
    """Create and return a new psycopg2 connection.
    If db_url is None, reads from the TARGET_DB environment variable.
    """
    if db_url is None:
        db_url = os.getenv('TARGET_DB')
    if not db_url:
        raise ValueError('Database URL not provided via argument or TARGET_DB env var')
    return psycopg2.connect(db_url)

def run_query(query, params=None, db_url=None):
    """Execute a SELECT query and return a single scalar result.
    Useful for queries like ``SELECT COUNT(*) FROM customer``.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return result[0] if result else None
    finally:
        conn.close()

def execute_sql(sql_statement, params=None, db_url=None):
    """Execute an arbitrary SQL statement (INSERT, UPDATE, etc.).
    Commits the transaction before closing.
    """
    conn = get_connection(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(sql_statement, params)
        conn.commit()
    finally:
        conn.close()
