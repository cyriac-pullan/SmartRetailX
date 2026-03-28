#!/usr/bin/env python3
"""
remap_layout.py
---------------
Reads products_complete.csv + products_part2.csv (1000 products total),
then reassigns every product to the new 3-aisle layout:

  Aisle  : 1, 2, 3
  Partition per aisle : 101 – 112  (12 partitions)
      Left side  : partitions 101–106  (6 partitions)
      Right side : partitions 107–112  (6 partitions)
  Shelves per partition : 101.1 – 101.7  (7 shelves)
  Products per shelf    : 3 – 5  (evenly distributed to cover all 1000)

Total capacity: 3 × 12 × 7 = 252 shelves
Target: 1000 products → 252 × 4 = 1008 slots → most shelves get 4, last few get 3

Output: database/products_combined_remapped.csv
"""

import csv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_DIR   = BASE_DIR.parent / "database"

CSV_IN_1 = DB_DIR / "products_unique.csv"
CSV_IN_2 = None   # single source file now
CSV_OUT  = DB_DIR / "products_unique_remapped.csv"

FIELDNAMES = [
    "Product_ID", "Barcode", "Product_Name", "Price", "Weight_kg",
    "Category", "Sub_Category", "Aisle_No", "Partition_No", "Shelf_No",
    "Position_Tag", "Side", "Stock_Quantity", "Reorder_Level"
]

# ── Layout constants ──────────────────────────────────────────────────────────
NUM_AISLES           = 3
PARTITIONS_PER_AISLE = 12        # 12 per aisle, globally unique
SHELVES_PER_PARTITION = 7        # .1 – .7

# Globally unique partition numbers per aisle
# Aisle 1: 101-112  (left: 101-106, right: 107-112)
# Aisle 2: 113-124  (left: 113-118, right: 119-124)
# Aisle 3: 125-136  (left: 125-130, right: 131-136)
AISLE_PARTITION_RANGES = {
    1: (101, 112),
    2: (113, 124),
    3: (125, 136),
}

def get_partition_range(aisle: int):
    start, end = AISLE_PARTITION_RANGES[aisle]
    all_parts = list(range(start, end + 1))
    left  = all_parts[:6]   # first 6  → Left side
    right = all_parts[6:]   # last  6  → Right side
    return left, right


def build_slot_sequence():
    """
    Returns an ordered list of (aisle, partition, shelf_num, side, position_tag)
    covering all 252 slots in reading order.

    Aisle 1: P101-P112  |  Aisle 2: P113-P124  |  Aisle 3: P125-P136
    Each aisle: left-col (6 partitions, 7 shelves each) then right-col.
    """
    slots = []
    for aisle in range(1, NUM_AISLES + 1):
        left_parts, right_parts = get_partition_range(aisle)
        for partition in left_parts + right_parts:
            side    = "Left" if partition in left_parts else "Right"
            pos_tag = f"P{partition}"
            for shelf_num in range(1, SHELVES_PER_PARTITION + 1):
                shelf_label = f"{partition}.{shelf_num}"
                slots.append((aisle, partition, shelf_label, side, pos_tag))
    return slots          # 3 × 12 × 7 = 252 slots


def load_all_products():
    """Read source CSVs and return a combined list sorted by Product_ID."""
    products = []
    sources = [p for p in [CSV_IN_1, CSV_IN_2] if p is not None]
    for csv_path in sources:
        if not csv_path.exists():
            print(f"  WARNING: {csv_path.name} not found – skipping")
            continue
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Product_ID") and row.get("Barcode"):
                    products.append(row)
        print(f"  Loaded {csv_path.name}  ->  running total: {len(products)}")

    # Sort by Category, Sub_Category, and Product_Name for better grouping on shelves
    products.sort(key=lambda r: (r.get("Category", ""), r.get("Sub_Category", ""), r.get("Product_Name", "")))
    return products


def distribute_products(products, slots):
    """
    Distribute `products` across `slots` with 3–5 products per shelf.
    Strategy:
      - 252 shelves, 1000 products
      - Base 3 products per shelf × 252 = 756 → 244 extra products
        to spread as +1 (4 products) across 244 shelves, then
        remaining 8 shelves with 4+1=5 if needed.
      We use: fill shelves sequentially, assigning 4 products to the
      first 244 shelves and 3 to the remaining 8, which sums to exactly
      244×4 + 8×3 = 976 + 24 = 1000. ✓
    """
    total_products = len(products)
    total_slots    = len(slots)

    # Calculate per-shelf allocation
    # We want to distribute `total_products` across `total_slots` shelves
    # with each shelf getting floor or ceil products.
    base  = total_products // total_slots          # 3
    extra = total_products  % total_slots          # 244  (shelves that get base+1)

    allocations = []
    for i in range(total_slots):
        count = base + (1 if i < extra else 0)
        allocations.append(count)

    # Sanity check
    assert sum(allocations) == total_products, \
        f"Allocation mismatch: {sum(allocations)} ≠ {total_products}"

    assigned = []
    prod_idx = 0
    for slot_idx, (aisle, partition, shelf_label, side, pos_tag) in enumerate(slots):
        n = allocations[slot_idx]
        for _ in range(n):
            if prod_idx >= total_products:
                break
            row = dict(products[prod_idx])
            row["Aisle_No"]     = aisle
            row["Partition_No"] = partition
            row["Shelf_No"]     = shelf_label
            row["Side"]         = side
            row["Position_Tag"] = pos_tag
            assigned.append(row)
            prod_idx += 1

    return assigned


def write_output(assigned, csv_out):
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in assigned:
            writer.writerow({k: row.get(k, "") for k in FIELDNAMES})
    print(f"\n  Written: {csv_out}")


def print_summary(assigned):
    from collections import defaultdict

    aisle_counts = defaultdict(int)
    partition_counts = defaultdict(int)
    shelf_product_counts = defaultdict(int)

    for row in assigned:
        a  = row["Aisle_No"]
        p  = row["Partition_No"]
        sh = row["Shelf_No"]
        aisle_counts[a] += 1
        partition_counts[(a, p)] += 1
        shelf_product_counts[(a, p, sh)] += 1

    print("\n" + "=" * 60)
    print("LAYOUT SUMMARY")
    print("=" * 60)

    for aisle in sorted(set(r["Aisle_No"] for r in assigned)):
        print(f"\nAisle {aisle}  ({aisle_counts[aisle]} products)")
        for part in range(101, 113):
            side = "Left" if part <= 106 else "Right"
            count = partition_counts.get((aisle, part), 0)
            shelves_info = []
            for sh_num in range(1, SHELVES_PER_PARTITION + 1):
                sh_label = f"{part}.{sh_num}"
                c = shelf_product_counts.get((aisle, part, sh_label), 0)
                shelves_info.append(str(c))
            print(f"  P{part} ({side:5s}): {count:3d} products  "
                  f"shelves=[{', '.join(shelves_info)}]")

    all_shelf_counts = list(shelf_product_counts.values())
    print(f"\nShelves with 3 products : {all_shelf_counts.count(3)}")
    print(f"Shelves with 4 products : {all_shelf_counts.count(4)}")
    print(f"Shelves with 5 products : {all_shelf_counts.count(5)}")
    print(f"Total products assigned : {len(assigned)}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("STORE LAYOUT REMAPPER")
    print("3 Aisles × 12 Partitions × 7 Shelves → 252 Shelves")
    print("=" * 60)

    print("\n[1] Loading products...")
    products = load_all_products()
    print(f"    Total loaded: {len(products)}")

    if len(products) == 0:
        print("ERROR: No products found. Check CSV paths.")
        return

    print("\n[2] Building slot sequence (252 slots)...")
    slots = build_slot_sequence()
    print(f"    Total slots : {len(slots)}")

    print("\n[3] Distributing products...")
    assigned = distribute_products(products, slots)

    print("\n[4] Writing output CSV...")
    write_output(assigned, CSV_OUT)

    print_summary(assigned)
    print(f"\n✓ Output saved to: {CSV_OUT}")
    print("  → Now run: python import_to_neon.py")


if __name__ == "__main__":
    main()
