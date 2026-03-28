import sys, sqlite3
sys.path.append('d:/MAJ FIN LAT/MAJ FIN/backend')
from app import pg_query_all, NEON_HISTORY_DSN

customer_id = '22RA237'
target_partition = 104

history_rows = pg_query_all(
    NEON_HISTORY_DSN,
    "SELECT barcode FROM purchase_history WHERE customer_id = %s ORDER BY purchased_at DESC LIMIT 100",
    (customer_id,)
)
print('History rows:', len(history_rows))

barcodes = list(set([str(r['barcode']) for r in history_rows if r.get('barcode')]))
print('Barcodes:', len(barcodes))

def query_db(query, args=(), one=False):
    db = sqlite3.connect('d:/MAJ FIN LAT/MAJ FIN/backend/smartretail.db')
    db.row_factory = sqlite3.Row
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

placeholders = ','.join(['?'] * len(barcodes))
query = f"SELECT barcode, name, price, aisle, partition_no, shelf_no, side, position_tag FROM products WHERE barcode IN ({placeholders})"

products = query_db(query, tuple(barcodes))
print('Products found in SQLite:', len(products))

def get_corridor(p):
    if p >= 101 and p <= 106: return 'L'
    if p >= 107 and p <= 118: return '12'
    if p >= 119 and p <= 130: return '23'
    return 'R'
    
def get_index(p):
    res = (p - 100) % 12
    if res == 0: res = 12
    return (res - 1) % 6

target_corr = get_corridor(target_partition)
target_idx  = get_index(target_partition)
print('Target:', target_partition, 'Corr:', target_corr, 'Idx:', target_idx)

suggestions = []
for prod in products:
    pno = prod.get('partition_no')
    if not pno: continue
    
    # We must convert pno to int!
    # SQLite returns numeric values as ints usually, but let's be safe.
    try:
        pno = int(pno)
    except:
        continue
    
    if pno == target_partition: continue
    
    prod_corr = get_corridor(pno)
    prod_idx  = get_index(pno)
    
    print(f"{prod['name']}: P{pno} -> Corr {prod_corr}, Idx {prod_idx}")
    if prod_corr == target_corr and prod_idx >= target_idx:
        suggestions.append(dict(prod))

print('Suggestions:', len(suggestions))
