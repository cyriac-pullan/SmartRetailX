@echo off
echo ========================================
echo SmartRetailX Setup Script
echo ========================================
echo.

echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Creating database...
python create_db.py
if errorlevel 1 (
    echo ERROR: Failed to create database
    pause
    exit /b 1
)

echo.
echo [3/4] Importing products...
python import_products.py
if errorlevel 1 (
    echo ERROR: Failed to import products
    pause
    exit /b 1
)

echo.
echo [4/4] Setup complete!
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& python app.py
echo 2. Open frontend: frontend\index.html
echo.
pause

