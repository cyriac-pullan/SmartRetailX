# SmartRetailX - Complete Setup Guide

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Web browser (for frontend)

## 🚀 Step-by-Step Setup

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Create Database

```bash
# Create database schema
python create_db.py

# Import products (36 products)
python import_products.py
```

Expected output:
```
✓ Database schema created successfully!
✓ Products imported: 36 rows
```

### Step 3: Start Backend Server

```bash
python app.py
```

Expected output:
```
╔════════════════════════════════════════╗
║  SmartRetailX Backend Server Starting  ║
║  API: http://localhost:5000             ║
╚════════════════════════════════════════╝
```

### (Optional) Start Advanced Services

In separate terminals:
```bash
# Mock weight service (port 5001)
python weight_mock.py

# ML services (port 5003)
python ml_complete.py

# BLE navigation (port 5002) - requires BLE adapter
python ble_complete.py
```

### Step 4: Test Backend

Open a new terminal:

```bash
cd backend
python test_api.py
```

All tests should pass.

### Step 5: Update Frontend Configuration

Open `index.html` and update:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    USE_MOCK_DATA: false,  // Change to false
    WS_URL: 'ws://localhost:5000'
};
```

### Step 6: Open Frontend

Simply open `index.html` in your web browser, or use a local server:

```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000
```

## ✅ Verification Checklist

- [ ] Backend server running on port 5000
- [ ] Database created with 36 products
- [ ] API health check returns success
- [ ] Frontend loads without errors
- [ ] Barcode scanning works (try: 890000001)
- [ ] Products appear in cart
- [ ] Billing calculates correctly

## 🧪 Test Barcodes

Use these barcodes for testing:

- `890000001` - AJMI MATTA VADI RICE 10KG (₹450)
- `890000006` - AJWA MATTA VADI RICE 10KG (₹500)
- `890000013` - 916 COCONUT OIL 1LTR POUCH (₹280)
- `890000021` - AASHIRVAAD SUPERIOR MP ATTA 1KG (₹75)
- `890000025` - BINGO MAD ANGLES ACHAARI MASTI (₹30)

## 🆘 Troubleshooting

### Backend won't start
- Check if port 5000 is already in use
- Verify Python version: `python --version`
- Check dependencies: `pip list`

### Database errors
- Delete `smartretail.db` and run `create_db.py` again
- Verify CSV file path in `import_products.py`

### Frontend can't connect
- Ensure backend is running
- Check browser console for errors
- Verify CORS is enabled in `app.py`

### Product not found
- Verify barcode exists in database
- Check database: `sqlite3 smartretail.db "SELECT * FROM products WHERE barcode='890000001';"`

## 📚 Next Steps

1. Test all features
2. Add hardware integration (optional)
3. Deploy to production
4. Add ML components (optional)

## 🎯 Project Structure

```
smartretailx-project/
├── backend/
│   ├── app.py              # Main API server
│   ├── create_db.py        # Database setup
│   ├── import_products.py  # Data import
│   └── ...
├── database/
│   └── products_complete.csv
├── frontend/
│   └── index.html
└── docs/
    └── SETUP_GUIDE.md
```

