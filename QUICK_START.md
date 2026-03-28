# SmartRetailX - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 minute)
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Setup Database (1 minute)
```bash
python create_db.py
python import_products.py
```

### Step 3: Start Backend (1 minute)
```bash
python app.py
```

You should see:
```
╔════════════════════════════════════════╗
║  SmartRetailX Backend Server Starting  ║
║  API: http://localhost:5000             ║
╚════════════════════════════════════════╝
```

### Step 4: Open Frontend (1 minute)
Simply open `frontend/index.html` in your browser!

Or use a local server:
```bash
python -m http.server 8000
# Then open: http://localhost:8000
```

### Step 5: Test It! (1 minute)
1. Type barcode: `890000001`
2. Press Enter
3. Product should appear in cart!

### (Optional) Start advanced services
```bash
# Mock weight service (port 5001)
python weight_mock.py

# ML services (port 5003)
python ml_complete.py

# BLE navigation (port 5002) - requires BLE adapter
python ble_complete.py
```

## ✅ Verification

Test these endpoints:
```bash
# Health check
curl http://localhost:5000/api/health

# Product lookup
curl -X POST http://localhost:5000/api/products/barcode \
  -H "Content-Type: application/json" \
  -d '{"barcode": "890000001"}'
```

## 🧪 Test Barcodes

- `890000001` - AJMI MATTA VADI RICE 10KG (₹450)
- `890000006` - AJWA MATTA VADI RICE 10KG (₹500)
- `890000013` - 916 COCONUT OIL 1LTR POUCH (₹280)
- `890000021` - AASHIRVAAD SUPERIOR MP ATTA 1KG (₹75)
- `890000025` - BINGO MAD ANGLES ACHAARI MASTI (₹30)

## 📁 Project Structure

```
smartretailx-project/
├── frontend/
│   └── index.html          # Open this in browser
├── backend/
│   ├── app.py              # Run this first
│   ├── create_db.py        # Setup database
│   └── import_products.py  # Import products
└── database/
    └── products_complete.csv
```

## 🆘 Troubleshooting

**Backend won't start?**
- Check if port 5000 is free
- Verify Python is installed: `python --version`

**Frontend can't connect?**
- Make sure backend is running
- Check browser console (F12)

**Product not found?**
- Verify database was imported: `python import_products.py`
- Check barcode exists: `890000001`

## 🎯 Next Steps

1. ✅ Backend running
2. ✅ Frontend working
3. ✅ Test barcode scanning
4. ✅ Try checkout flow
5. ✅ Explore recommendations

## 📚 Full Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup
- [Backend README](backend/README.md) - API docs
- [Main README](README.md) - Project overview

---

**You're all set! 🎉**

Start with: `cd backend && python app.py`

