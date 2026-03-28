#!/usr/bin/env python3
"""
update_partitions.py
--------------------
Reassigns position_tag, partition_no, and shelf_no for Aisle 2 and Aisle 3
products in the Neon DB to use globally unique partition numbers:

  Aisle 1: P101–P112  (partition_no 101–112,  left: 101-106, right: 107-112)
  Aisle 2: P113–P124  (partition_no 113–124,  left: 113-118, right: 119-124)
  Aisle 3: P125–P136  (partition_no 125–136,  left: 125-130, right: 131-136)

Shelf labels become: <partition_no>.<shelf_index>
  e.g. partition 113 → shelves 113.1 … 113.7
"""

import os, sys, re
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# ── Load env (same pattern as app.py) ─────────────────────────────────────────
load_dotenv()
NEON_DB_DSN = os.getenv("NEON_DB_DSN") or os.getenv("DATABASE_URL")
if not NEON_DB_DSN:
    sys.exit("ERROR: NEON_DB_DSN / DATABASE_URL not set in environment.")

# ── Old → New partition mapping per aisle ─────────────────────────────────────
# Aisle 1 unchanged (P101-P112).
# For aisles 2 and 3, old DB may have P101-P112 OR the correct new numbers
# already (from a previous run). We handle both cases.

def partition_offset(aisle: int) -> int:
    """Return the base offset for this aisle's partition numbering."""
    return {1: 0, 2: 12, 3: 24}.get(aisle, 0)

def new_partition_no(old_partition_no: int, aisle: int) -> int:
    """Convert old per-aisle partition number (101-112) to global number."""
    relative = old_partition_no - 100          # 1-12
    return 100 + partition_offset(aisle) + relative   # e.g. aisle2,rel6 → 118

def new_position_tag(np: int) -> str:
    return f"P{np}"

def new_shelf_no(old_shelf_no: str, np: int) -> str:
    """Re-label shelf: e.g. '101.3' → '113.3'"""
    m = re.match(r'^\d+\.(\d+)$', str(old_shelf_no))
    if m:
        return f"{np}.{m.group(1)}"
    return f"{np}.1"   # fallback

def new_side(np: int, aisle: int) -> str:
    """Left partitions are first 6, right are last 6 within the aisle block."""
    offset = partition_offset(aisle)
    left_range = range(101 + offset, 107 + offset)   # first 6
    return "Left" if np in left_range else "Right"

# ──────────────────────────────────────────────────────────────────────────────
def run():
    print("Connecting to Neon DB…")
    conn = psycopg2.connect(NEON_DB_DSN)
    conn.autocommit = False
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Fetch all products from both product tables in one go
    tables = []
    for tbl in ("products", "products2"):
        try:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {tbl}")
            row = cur.fetchone()
            if row and row["cnt"] > 0:
                tables.append(tbl)
        except Exception:
            conn.rollback()

    if not tables:
        print("No product tables found. Exiting.")
        conn.close(); return

    total_updated = 0
    for tbl in tables:
        print(f"\nProcessing table: {tbl}")
        cur.execute(f"""
            SELECT product_id, aisle, partition_no, shelf_no
            FROM {tbl}
            WHERE aisle IN (1, 2, 3)
            ORDER BY aisle, partition_no
        """)
        rows = cur.fetchall()
        print(f"  Found {len(rows)} rows")

        batch = []
        for r in rows:
            aisle    = int(r["aisle"])
            old_pno  = int(r["partition_no"]) if r["partition_no"] else None
            old_shelf = str(r["shelf_no"]) if r["shelf_no"] else ""

            # Determine old relative partition (1-12) for this aisle
            if old_pno is None:
                continue

            # If already in the global range, recalculate just to be safe
            if old_pno > 100:
                # strip to relative
                relative = old_pno - 100 - partition_offset(aisle)
                if relative < 1 or relative > 12:
                    # Might already be in new global form — recalculate
                    relative = old_pno - 100  # treat as absolute
                    if relative < 1: continue
                new_pno = 100 + partition_offset(aisle) + relative
            else:
                new_pno = 100 + partition_offset(aisle) + old_pno

            if new_pno == old_pno:
                continue   # aisle 1 unchanged

            new_ptag  = new_position_tag(new_pno)
            new_shelf = new_shelf_no(old_shelf, new_pno)
            new_s     = new_side(new_pno, aisle)

            batch.append((new_pno, new_ptag, new_shelf, new_s, r["product_id"]))

        if batch:
            psycopg2.extras.execute_batch(cur, f"""
                UPDATE {tbl}
                SET partition_no = %s,
                    position_tag = %s,
                    shelf_no     = %s,
                    side         = %s
                WHERE product_id = %s
            """, batch)
            print(f"  Updated {len(batch)} rows in {tbl}")
            total_updated += len(batch)
        else:
            print(f"  All rows already up-to-date in {tbl}")

    conn.commit()
    cur.close(); conn.close()
    print(f"\n✅ Done — {total_updated} product rows updated.")
    print("Run the backend (app.py) to reload the nav graph from the updated DB.")

if __name__ == "__main__":
    run()
