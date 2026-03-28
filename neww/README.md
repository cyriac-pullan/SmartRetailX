# SmartRetailX - Intelligent Shopping System

Complete retail checkout system with barcode scanning, cart management, billing, weight verification, and AI-powered recommendations.

## 🎯 Features

- ✅ **Barcode Scanning** - Scan or type barcodes to add products
- ✅ **Real-time Cart Management** - Add, remove, adjust quantities
- ✅ **Automatic Billing** - Calculate subtotal, tax (5%), and total
- ✅ **Weight Verification** - Exit scale verification system
- ✅ **Smart Recommendations** - AI-powered product suggestions
- ✅ **Analytics Dashboard** - Sales and inventory tracking
- ✅ **Responsive Design** - Works on desktop and mobile

## 📁 Project Structure

```
smartretailx-project/
├── frontend/
│   └── index.html          # Complete frontend application
├── backend/
│   ├── app.py              # Main Flask API server
│   ├── create_db.py        # Database initialization
│   ├── import_products.py  # Product data import
│   ├── test_api.py         # API test suite
│   ├── requirements.txt    # Python dependencies
│   └── ...
├── database/
│   └── products_complete.csv  # 36 products database
├── docs/
│   └── SETUP_GUIDE.md      # Setup instructions
└── hardware/
    └── (hardware integration files)
```

## 🚀 Quick Start

### 1. Setup Backend

```bash
cd backend
pip install -r requirements.txt
python create_db.py
python import_products.py
python app.py
```

### 2. Update Frontend Config

In `index.html`, update:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    USE_MOCK_DATA: false,  // Use real backend
};
```

### 3. Open Frontend

Open `index.html` in your browser or use:
```bash
python -m http.server 8000
```

## 📊 Database

- **36 Products** with complete details
- **8 Tables** for full functionality
- **SQLite** database (easy to use)

## 🔌 API Endpoints

- `POST /api/products/barcode` - Product lookup
- `POST /api/cart/create` - Create cart
- `POST /api/cart/<id>/add` - Add items
- `POST /api/bills` - Generate bill
- `POST /api/weight/verify` - Weight verification
- `GET /api/recommendations/<category>` - Get recommendations
- `GET /api/analytics/sales` - Sales analytics

## 🧪 Testing

```bash
# Test API endpoints
cd backend
python test_api.py

# Integration tests
python integration_test.py
```

## 📝 Test Barcodes

- `890000001` - AJMI MATTA VADI RICE 10KG (₹450)
- `890000006` - AJWA MATTA VADI RICE 10KG (₹500)
- `890000013` - 916 COCONUT OIL 1LTR POUCH (₹280)
- `890000021` - AASHIRVAAD SUPERIOR MP ATTA 1KG (₹75)
- `890000025` - BINGO MAD ANGLES ACHAARI MASTI (₹30)

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Complete setup instructions
- [Backend README](backend/README.md) - API documentation
- [Frontend README](README.md) - Frontend details

## 🛠️ Technology Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python, Flask
- **Database**: SQLite
- **ML**: scikit-learn (recommendations, forecasting)

## 🎓 Project Phases

1. ✅ Database Setup
2. ✅ Backend API
3. ✅ Frontend Integration
4. ⚙️ Weight Verification (Optional)
5. ⚙️ BLE Navigation (Optional)
6. ⚙️ ML Components (Optional)

## 📞 Support

For issues or questions:
1. Check [Setup Guide](docs/SETUP_GUIDE.md)
2. Review backend logs
3. Check browser console

## 🎉 Status

✅ **Core Features Complete**
- Database setup
- Backend API
- Frontend application
- Testing suite

⚙️ **Optional Features**
- Hardware integration
- ML components
- Advanced analytics

---

**SmartRetailX - Intelligent Shopping Companion**

*Built for modern retail checkout systems*
