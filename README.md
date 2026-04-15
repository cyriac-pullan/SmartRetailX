<div align="center">
  <h1>SmartRetailX</h1>
  <p><strong>Next-Generation AI-Powered Indoor Navigation & Smart Shopping Companion</strong></p>
  
  [![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=white&style=flat-square)](#)
  [![Flask](https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white&style=flat-square)](#)
  [![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-336791?logo=postgresql&logoColor=white&style=flat-square)](#)
  [![Vite](https://img.shields.io/badge/Build_Tool-Vite-646CFF?logo=vite&logoColor=white&style=flat-square)](#)
  [![ESP32](https://img.shields.io/badge/Hardware-ESP32_BLE-E7352C?logo=espressif&logoColor=white&style=flat-square)](#)
</div>

<br />

SmartRetailX is a full-stack retail navigation system that combines **real-time BLE indoor positioning** (using ESP32 hardware), **AI-driven product suggestions**, and a **beautiful React frontend** to guide shoppers to their desired products inside a physical store.

---

## Table of Contents

1.  [Prerequisites (What You Need)](#-prerequisites-what-you-need)
2.  [Project Structure](#-project-structure)
3.  [Step 1: Clone the Repository](#step-1-clone-the-repository)
4.  [Step 2: Backend Setup (Python/Flask)](#step-2-backend-setup-pythonflask)
5.  [Step 3: Frontend Setup (React/Vite)](#step-3-frontend-setup-reactvite)
6.  [Step 4: ESP32 Hardware Setup](#step-4-esp32-hardware-setup)
7.  [Step 5: Calibration (IMPORTANT)](#step-5-calibration-important)
8.  [Step 6: Running the Full Demo](#step-6-running-the-full-demo)
9.  [The Demo Script (What to Show)](#-the-demo-script-what-to-show)
10. [Architecture Overview](#-architecture-overview)
11. [Troubleshooting](#-troubleshooting)

---

## Prerequisites (What You Need)

Before you begin, make sure the following software and hardware are available on the **demo machine**.

### Software Requirements

| Tool | Version | Download Link | Purpose |
|---|---|---|---|
| **Python** | 3.10 or higher | [python.org/downloads](https://www.python.org/downloads/) | Runs the backend server |
| **Node.js** | 18.x or higher | [nodejs.org](https://nodejs.org/) | Runs the frontend dev server |
| **Git** | Any recent version | [git-scm.com](https://git-scm.com/) | Clone the repository |
| **Arduino IDE** | 2.x | [arduino.cc/en/software](https://www.arduino.cc/en/software) | Flash ESP32 beacons (one-time) |

> **IMPORTANT:** When installing Python on Windows, **check the box that says "Add Python to PATH"** during installation. Without this, `python` commands will not work from the terminal.

> **IMPORTANT:** When installing Node.js, use the **LTS** version. The installer will also install `npm` automatically.

### Hardware Requirements

| Item | Quantity | Purpose |
|---|---|---|
| **ESP32 Dev Board** (any variant with BLE) | 4 | BLE beacons for indoor positioning |
| **Micro-USB Cables** | 4 | Power the ESP32 boards |
| **USB Power Banks or Wall Adapters** | 4 | Keep ESP32s powered during demo |
| **Laptop/PC with Bluetooth** | 1 | The demo machine (runs the scanner) |

---

## Project Structure

```
SmartRetailX/
├── backend/                  # Python Flask API server
│   ├── app.py                # Main server (all API routes)
│   ├── backend_service.py    # BLE scanning service + SmartCartService
│   ├── esp32_tracker.py      # Indoor positioning engine (RSSI → partition)
│   ├── calibrate_esp32.py    # Calibration tool (run at demo site)
│   ├── import_products.py    # Product database import pipeline
│   ├── path_planner.py       # Graph-based aisle navigation
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variable template
│   └── smartretail.db        # Local SQLite database
│
├── frontend-react/           # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── features/
│   │   │       └── LiveNavigationModal.jsx  # The main navigation map UI
│   │   ├── services/
│   │   │   └── api.js        # API client (talks to Flask)
│   │   └── store/
│   │       └── useAppStore.js # Zustand state management
│   └── package.json
│
├── esp32_beacon/             # Arduino firmware for ESP32 beacons
│   └── esp32_beacon.ino      # BLE advertising firmware
│
├── database/                 # CSV product catalogs
│   └── products_unique_remapped.csv
│
└── README.md                 # This file
```

---

## Step 1: Clone the Repository

Open a terminal (PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/cyriac-pullan/SmartRetailX.git
cd SmartRetailX
```

---

## Step 2: Backend Setup (Python/Flask)

### 2.1 Create a Virtual Environment

This keeps your Python packages isolated from the system.

**Windows (PowerShell):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` appear at the beginning of your terminal prompt. This means the virtual environment is active.

### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install Flask, psycopg2, bleak (BLE scanner), numpy, pandas, and all other required packages. It may take 2-3 minutes.

### 2.3 Set Up Environment Variables

The backend needs a database connection string to work. Create a `.env` file:

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Now open the `.env` file in any text editor and fill in the values:

```env
# All DSN values point to the same Neon database
NEON_DB_DSN="postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEON_HISTORY_DSN="postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEON_PRODUCTS_DSN="postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEON_CARTS_DSN="postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEON_ANALYTICS_DSN="postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Optional: For AI chatbot features
GEMINI_API_KEY="your_google_gemini_key_here"

# Application Settings
FLASK_ENV="development"
FLASK_APP="app.py"
PORT=5000
```

> **Note:** The Neon DB connection string shown above is the project's shared cloud database. It is already pre-populated with product data. You do NOT need to create your own database.

### 2.4 Verify the Database

Run this quick check to make sure the product database is ready:

```bash
python import_products.py
```

You should see output like:
```
11:36:12 [INFO] Source: products_unique_remapped.csv
11:36:14 [INFO] Connected to Neon DB
11:36:18 [INFO] Pipeline finished in 6.88s
11:36:18 [INFO] Summary: 578 records imported, 0 errors.
```

### 2.5 Start the Backend Server

```bash
python app.py
```

You should see:
```
--- INIT FLASK ROUTES ---
ROUTE: /api/nav/esp-status ...
ROUTE: /api/products/search ...
...
Backend Service Started
* Running on http://0.0.0.0:5000
```

> **Leave this terminal running.** Open a NEW terminal for the frontend.

---

## Step 3: Frontend Setup (React/Vite)

Open a **second terminal window** (keep the backend running in the first one).

### 3.1 Install Node Dependencies

```bash
cd frontend-react
npm install
```

This will download all React, Vite, Tailwind, and animation libraries. It may take 3-5 minutes on first run.

### 3.2 Start the Frontend Dev Server

```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in 500ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### 3.3 Open the Application

Open your web browser (Chrome recommended) and go to:

```
http://localhost:5173
```

You should see the SmartRetailX shopping interface. The app is now running!

---

## Step 4: ESP32 Hardware Setup

This section explains how to flash the ESP32 boards with the beacon firmware. **You only need to do this once per ESP32.**

### 4.1 Install Arduino IDE

1. Download from [arduino.cc/en/software](https://www.arduino.cc/en/software)
2. Install and open Arduino IDE

### 4.2 Add ESP32 Board Support

1. Go to **File → Preferences**
2. In the **"Additional Boards Manager URLs"** field, paste:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
3. Click **OK**
4. Go to **Tools → Board → Boards Manager**
5. Search for **"esp32"**
6. Install **"esp32 by Espressif Systems"** (version 2.x or 3.x)
7. Wait for installation to complete

### 4.3 Flash Each ESP32

You need to flash **4 ESP32 boards**, each with a different name.

1. Open the file `esp32_beacon/esp32_beacon.ino` in Arduino IDE
2. **For each ESP32, change line 14** to match the device number:

| ESP32 # | Change `BEACON_NAME` to | Physical Position |
|---|---|---|
| 1st ESP32 | `"ESP32_AISLE_1"` | Left wall (start of corridor) |
| 2nd ESP32 | `"ESP32_AISLE_2"` | Between Aisle 1 and Aisle 2 |
| 3rd ESP32 | `"ESP32_AISLE_3"` | Between Aisle 2 and Aisle 3 |
| 4th ESP32 | `"ESP32_AISLE_4"` | Right wall (end of corridor) |

3. Connect the ESP32 via USB
4. In Arduino IDE:
   - **Tools → Board** → Select **"ESP32 Dev Module"**
   - **Tools → Port** → Select the COM port that appeared (e.g., `COM3` on Windows)
5. Click the **Upload** button (→ arrow)
6. Wait for "Done uploading"
7. Open **Tools → Serial Monitor** (set baud to `115200`)
8. You should see: `BLE Beacon Active! Broadcasting as: ESP32_AISLE_1`
9. **Repeat for all 4 ESP32s**, changing the name each time

### 4.4 Physical Placement

Place the 4 ESP32 boards in a line, spaced approximately **2.0–2.5 meters apart**:

```
                    ~2.0m        ~2.0m        ~2.0m
  [ESP32_AISLE_1] --------- [ESP32_AISLE_2] --------- [ESP32_AISLE_3] --------- [ESP32_AISLE_4]
   Left Wall                 Aisle 1-2                  Aisle 2-3                Right Wall
   Corridor                  Corridor                   Corridor                 Corridor
```

- Mount them at **chest height** (~1.2m from floor) for best signal
- Ensure they are **powered** (USB power bank or wall adapter)
- Keep them **away from metal objects** which interfere with BLE signals

---

## Step 5: Calibration (IMPORTANT)

Calibration ensures the system accurately measures distance from RSSI signals. **Do this at the demo location.**

### 5.1 Run the Calibration Tool

Make sure the backend virtual environment is active, then:

```bash
cd backend
python calibrate_esp32.py
```

### 5.2 Take the Measurement

1. Stand exactly **1 meter away** from any one of your powered ESP32 beacons
2. The tool will print live RSSI readings every 3 seconds:
   ```
   ----------------------------------------
   FOUND -> ESP32_AISLE_1: -82.5 dBm (10 packets)
   FOUND -> ESP32_AISLE_2: -89.1 dBm (8 packets)
   ...
   ```
3. Note the **dBm value** of the ESP32 you are standing closest to (it should be the strongest / least negative number, e.g., `-82`)
4. Press `Ctrl+C` to stop

### 5.3 Update the Calibration Value

Open `backend/esp32_tracker.py` in any text editor and update **line 15**:

```python
self.tx_power = -82  # <-- Replace -82 with your measured value
```

For example, if your reading was `-78 dBm` at 1 meter, change it to:
```python
self.tx_power = -78
```

> **Rule of thumb:** The `tx_power` value should equal the average RSSI you see when standing 1 meter from a beacon. Current default is `-82` which works well for most indoor environments.

### 5.4 Adjust Scale (Optional)

If your demo area is very small (e.g., a classroom table), you can adjust the walkway length on **line 4** of `esp32_tracker.py`:

```python
self.walkway_length_m = 2.0  # Total corridor length in meters
```

- For a **small table demo**: Use `1.0` to `2.0`
- For a **room-sized demo**: Use `3.0` to `6.0`

---

## Step 6: Running the Full Demo

### Quick Checklist

- [ ] All 4 ESP32 boards are powered and broadcasting
- [ ] Backend server is running (`python app.py` in terminal 1)
- [ ] Frontend is running (`npm run dev` in terminal 2)
- [ ] Browser is open at `http://localhost:5173`
- [ ] Calibration has been done at the demo location

### Start Order

1. **Power on all 4 ESP32s** (plug in USB cables)
2. **Terminal 1 (Backend):**
   ```bash
   cd backend
   .\venv\Scripts\Activate   # Windows
   # source venv/bin/activate  # Mac/Linux
   python app.py
   ```
3. **Terminal 2 (Frontend):**
   ```bash
   cd frontend-react
   npm run dev
   ```
4. **Open browser:** `http://localhost:5173`

---

## The Demo Script (What to Show)

Follow these steps during the live demo to showcase all features:

### Demo Step 1: Login
1. On the app's landing page, click **"Login"**
2. Use these demo credentials:
   - **Email:** `asha@smartretailx.com`
   - **Password:** `pass123`
3. You will be taken to the main shopping dashboard

### Demo Step 2: Product Search & Navigation
1. In the **search bar**, type a product name (e.g., `"Rice"` or `"Ghee"`)
2. Click on the product from the search results
3. Click the **"Navigate" / location button** on the product card
4. The **Live Navigation Modal** will open showing:
   - A **store map** with 3 aisles and 4 corridors
   - A **pulsing green "YOU" dot** showing your real-time position (from ESP32)
   - A **purple dashed path** from your location to the product's shelf
   - The **"Your Location"** field updating live with your corridor position

### Demo Step 3: Walk and Watch
1. Physically **walk towards different ESP32 beacons**
2. Watch the **green dot move** on the map in real-time
3. The **blue dashed path** will update to show the shortest route from your new position
4. The **"Your Location" text** in the status bar will update (e.g., "P107 (Aisle 1-2)")

### Demo Step 4: AI Suggestions ("On Your Way")
1. If the logged-in user has purchase history, the system will show **amber-colored "On Your Way" cards**
2. These are products the user has bought before that are located **along the walking path**
3. The amber dots also appear on the map canvas

### Demo Step 5: Additional Features to Show
- **Barcode Scanner:** Click the barcode icon to scan product barcodes
- **AI Chatbot:** Click the chat icon and ask for recipe suggestions (e.g., "How to make biryani?")
- **Cart System:** Add products to cart, view totals
- **Ads System:** Contextual advertisements appear based on aisle position

---

## Architecture Overview

```
┌─────────────────┐     BLE Signals      ┌──────────────┐
│   ESP32 Beacons │  ─────────────────►   │  Demo Laptop │
│   (4 devices)   │     (Bluetooth)       │  (Scanner)   │
└─────────────────┘                       └──────┬───────┘
                                                 │
                                    ┌────────────┴────────────┐
                                    │    Backend (Flask)       │
                                    │    - BLE Scanner         │
                                    │    - IndoorPositioning   │
                                    │    - Path Planner        │
                                    │    - Product API         │
                                    ├────────────┬────────────┤
                                    │  SQLite    │   Neon DB  │
                                    │  (local)   │  (cloud)   │
                                    └────────────┴────────────┘
                                                 │
                                          REST API (JSON)
                                                 │
                                    ┌────────────┴────────────┐
                                    │   Frontend (React+Vite) │
                                    │   - Live Navigation Map │
                                    │   - Product Search      │
                                    │   - AI Suggestions      │
                                    │   - Cart & Checkout     │
                                    └─────────────────────────┘
```

### How Indoor Positioning Works

1. **ESP32 beacons** continuously broadcast BLE (Bluetooth Low Energy) signals
2. The **backend BLE scanner** (using `bleak` library) picks up these signals every 2 seconds
3. The **IndoorPositioning engine** (`esp32_tracker.py`):
   - Applies an **Exponential Moving Average (EMA)** filter to smooth noisy RSSI values
   - Uses **hysteresis** to prevent the position from "bouncing" between corridors
   - Converts RSSI to **distance** using the Log-Distance Path Loss Model
   - Maps the distance to a specific **partition** (shelf position) in the store
4. The **frontend** polls the `/api/nav/esp-status` endpoint every 1.5 seconds
5. The **LiveNavigationModal** canvas renders the user's position and draws an animated path

---

## Troubleshooting

### "python is not recognized as a command"
- Python was not added to PATH during installation
- **Fix:** Reinstall Python and check **"Add Python to PATH"** during setup
- Or use `python3` instead of `python`

### "npm is not recognized"
- Node.js is not installed or not in PATH
- **Fix:** Download and install Node.js from [nodejs.org](https://nodejs.org/)

### "No ESP32 beacons detected this scan cycle"
- ESP32s are not powered or not broadcasting
- **Fix:** Check USB power, open Arduino Serial Monitor to verify "BLE Beacon Active!" message
- Make sure the laptop has **Bluetooth turned ON**

### "UnicodeEncodeError" when running Python scripts
- Windows terminal encoding issue
- **Fix:** The `app.py` already handles this. If it happens in other scripts, add this at the top:
  ```python
  import sys
  sys.stdout.reconfigure(encoding='utf-8', errors='replace')
  ```

### The green dot is not moving on the map
- The backend BLE scanner may not be picking up signals
- **Fix:** Check the backend terminal for `Pos: P107 | Dist: 0.5m | Corr: 12` messages
- If no messages appear, run `python calibrate_esp32.py` to verify ESP32s are visible

### Frontend shows "Scanning for beacons..."
- This is normal if no ESP32 is detected yet
- **Fix:** Wait 5-10 seconds for the first scan cycle to complete
- Ensure ESP32s are within Bluetooth range (~10 meters)

### Products not showing in search
- Database may not be populated
- **Fix:** Run `python import_products.py` from the `backend` folder

### Port already in use
- Another process is using port 5000 or 5173
- **Fix (Backend):** Change the port in `app.py` at the bottom (`app.run(port=5001)`)
- **Fix (Frontend):** Vite will automatically try the next available port

---

<div align="center">
  <br />
  <p><strong>SmartRetailX</strong> - Designed and Built for the Next Generation of Retail.</p>
  <p><em>ESP32 Indoor Navigation | AI Product Suggestions | Real-Time Store Mapping</em></p>
</div>
