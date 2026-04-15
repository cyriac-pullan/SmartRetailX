import csv
import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    psycopg2 = None

# Configuration & Paths
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = BASE_DIR / "smartretail.db"
NEON_DSN = os.getenv(
    "NEON_DB_DSN", 
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Search locations for products CSV
CSV_SEARCH_LOCATIONS = [
    BASE_DIR.parent / "database" / "products_unique_remapped.csv",
    BASE_DIR / "products_unique_remapped.csv",
    BASE_DIR.parent / "database" / "products_complete.csv",
    BASE_DIR / "products_complete.csv",
]

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ProductImporter:
    """Senior-level data pipeline for importing product catalogs into SmartRetailX."""
    
    def __init__(self, sqlite_path: Path, pg_dsn: str):
        self.sqlite_path = sqlite_path
        self.pg_dsn = pg_dsn
        self.csv_path: Optional[Path] = None
        self.batch_size = 100
        self.stats = {"inserted": 0, "errors": 0}

    def find_csv(self) -> Path:
        """Locate the best available CSV file for import."""
        for path in CSV_SEARCH_LOCATIONS:
            if path.exists():
                self.csv_path = path
                return path
        raise FileNotFoundError("Could not locate a valid products CSV in search paths.")

    def _ensure_sqlite_schema(self, conn: sqlite3.Connection):
        """Ensure local SQLite table exists with correct schema."""
        cursor = conn.cursor()
        cursor.execute("""
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
            )
        """)
        conn.commit()

    def _ensure_neon_schema(self, pg_conn):
        """Ensure cloud PostgreSQL table exists with correct schema."""
        with pg_conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    barcode TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
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
            """)
            pg_conn.commit()

    def _parse_row(self, row: Dict[str, str]) -> Optional[tuple]:
        """Validate and parse a single CSV row into a payload tuple."""
        try:
            return (
                row["Product_ID"].strip(),
                row["Barcode"].strip(),
                row["Product_Name"].strip(),
                float(row["Price"]),
                float(row["Weight_kg"]),
                row["Category"].strip(),
                row.get("Sub_Category", "").strip() or None,
                int(row.get("Aisle_No", 0)),
                int(row.get("Partition_No", 0)),
                row.get("Shelf_No", "").strip(),
                row.get("Position_Tag", "").strip(),
                row.get("Side", "Left").strip() or "Left",
                int(row.get("Stock_Quantity", 100)),
                int(row.get("Reorder_Level", 5)),
            )
        except Exception as e:
            logger.warning(f"Skipping invalid row {row.get('Product_ID', 'Unknown')}: {e}")
            self.stats["errors"] += 1
            return None

    def run(self):
        """Execute the full import pipeline."""
        start_time = datetime.now()
        self.find_csv()
        logger.info(f"Source: {self.csv_path.name}")
        
        # Connect to DBs
        sl_conn = sqlite3.connect(self.sqlite_path)
        self._ensure_sqlite_schema(sl_conn)
        
        pg_conn = None
        if psycopg2:
            try:
                pg_conn = psycopg2.connect(self.pg_dsn)
                self._ensure_neon_schema(pg_conn)
                logger.info("Connected to Neon DB")
            except Exception as e:
                logger.error(f"Neon connection failed: {e}")
        else:
            logger.warning("psycopg2 NOT installed. Skipping cloud sync.")

        # Processing loop
        batch = []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                payload = self._parse_row(row)
                if payload:
                    batch.append(payload)
                
                if len(batch) >= self.batch_size:
                    self._flush_batch(sl_conn, pg_conn, batch)
                    batch = []
            
            if batch:
                self._flush_batch(sl_conn, pg_conn, batch)

        sl_conn.close()
        if pg_conn: pg_conn.close()

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Pipeline finished in {duration:.2f}s")
        logger.info(f"Summary: {self.stats['inserted']} records imported, {self.stats['errors']} errors.")

    def _flush_batch(self, sl_conn, pg_conn, batch: List[tuple]):
        """Persist a batch of records to both databases with high-performance logic."""
        
        # 1. SQLite: INSERT OR REPLACE
        sl_conn.executemany("""
            INSERT OR REPLACE INTO products (
                product_id, barcode, name, price, weight_kg, category, sub_category,
                aisle, partition_no, shelf_no, position_tag, side,
                stock_quantity, reorder_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        sl_conn.commit()

        # 2. Neon (PostgreSQL): ON CONFLICT UPDATE
        if pg_conn:
            with pg_conn.cursor() as cur:
                # Use execute_values for high-speed multi-row insert on remote DB
                execute_values(cur, """
                    INSERT INTO products (
                        product_id, barcode, name, price, weight_kg, category, sub_category,
                        aisle, partition_no, shelf_no, position_tag, side,
                        stock_quantity, reorder_level
                    ) VALUES %s
                    ON CONFLICT (product_id) DO UPDATE SET
                        barcode = EXCLUDED.barcode,
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        weight_kg = EXCLUDED.weight_kg,
                        category = EXCLUDED.category,
                        sub_category = EXCLUDED.sub_category,
                        aisle = EXCLUDED.aisle,
                        partition_no = EXCLUDED.partition_no,
                        shelf_no = EXCLUDED.shelf_no,
                        position_tag = EXCLUDED.position_tag,
                        side = EXCLUDED.side,
                        stock_quantity = EXCLUDED.stock_quantity,
                        reorder_level = EXCLUDED.reorder_level
                """, batch)
                pg_conn.commit()
        
        self.stats["inserted"] += len(batch)

if __name__ == "__main__":
    importer = ProductImporter(DEFAULT_SQLITE_PATH, NEON_DSN)
    importer.run()
