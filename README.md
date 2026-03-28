<div align="center">
  <h1>🛒 SmartRetailX</h1>
  <p><strong>Next-Generation AI-Powered Indoor Navigation & Smart Shopping Companion</strong></p>
  
  [![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=white&style=flat-square)](#)
  [![Flask](https://img.shields.io/badge/Flask-Backend-000000?logo=flask&logoColor=white&style=flat-square)](#)
  [![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-336791?logo=postgresql&logoColor=white&style=flat-square)](#)
  [![Vite](https://img.shields.io/badge/Buid_Tool-Vite-646CFF?logo=vite&logoColor=white&style=flat-square)](#)
  [![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?logo=tailwind-css&logoColor=white&style=flat-square)](#)
</div>

<br />

Welcome to **SmartRetailX**, the future of brick-and-mortar shopping. This cross-platform system combines high-precision digital indoor mapping, real-time ESP32 hardware tracking, and AI-driven machine-learning insights to effortlessly guide shoppers exactly to their desired products—while intelligently suggesting forgotten items along their physical path!

---

## ✨ Key Features

- 🗺️ **Corridor-Based Pathfinding:** An intelligent canvas-based digital twin of the store layout. Users search for an item, and the system instantly draws a flawless, dynamic glowing path down valid walkable corridors right to the target partition, avoiding non-accessible warehouse elements (like "shelf-cutting").
- 📍 **Real-Time ESP32 Localization:** Built-in backend support for Bluetooth low-energy hardware beacons capable of accurately triangulating where the customer is standing within a macro zone (e.g., Aisle 2 - Left).
- 🧠 **Contextual AI Suggestions ("On Your Way"):** SmartRetailX bridges past and present. Upon path generation, the backend runs ultra-fast queries against a Neon Postgres Database containing user purchase history. It then maps the user's upcoming walking path against their historical cart to surface items they used to buy *that literally sit on the corridor they are about to walk down*.
- ⚡ **Dual-Layer Database System:** Uses a robust cloud **PostgreSQL (Neon)** cluster for heavy transactional data (customer logs, purchase history) and an ultra-fast local **SQLite** node for high-frequency low-latency physical inventory queries.

---

## 🛠️ Architecture Stack

### **Frontend (Interactive UI)**
- **React (Vite):** Blazing fast interactive SPA.
- **Tailwind CSS:** Fully responsive, modern floating UI design.
- **HTML Canvas:** Rendering multi-aisle and partition mappings with animated dot/route tracers.
- **Zustand:** Core state management for active user sessions and modal triggers.
- **Framer Motion:** Fluid modal entrances and notification overlays.

### **Backend (Intelligence Engine)**
- **Python / Flask:** Serves RESTful endpoints to the frontend.
- **psycopg2:** Powers real-time connectivity to cloud Postgres (Neon DB) arrays.
- **Built-in Path Planner Generator:** Advanced algorithmic logic determines logical corridors (`Corr-L`, `Corr-12`, `Corr-23`, `Corr-R`).

---

## 🚀 Quick Start Guide

You will need two terminal tabs to run the system completely.

### 1. Backend Setup
The backend serves the inventory catalog, coordinates the path planner, and verifies DB history.

```bash
cd backend
# Make sure you have python 3.9+ installed
pip install -r requirements.txt

# Run the Flask Server (default port: 5000/5001 proxy)
python app.py
```
*(Ensure you have a `.env` file containing `NEON_HISTORY_DSN=your_neon_db_url` and your `smartretail.db` sqlite file initialized!)*

### 2. Frontend Setup
The frontend serves the user-facing responsive React components.

```bash
cd frontend-react
# Install all required modules
npm install

# Spin up the Vite development proxy
npm run dev
```
Navigate to your localhost port (typically `http://localhost:3000` or `3001`).

---

## 🗺️ How "Path-Based Suggestions" Work
1. **Trigger:** User `22RA237` decides to navigate to `Lipton Yellow Label Tea` (Partition P104).
2. **Analysis:** The algorithmic mapper identifies the optimal walking path is down the `Left Wall Corridor`.
3. **Database Join:** The Flask app queries Neon DB to retrieve the user's last 100 bought items, maps them against local SQLite partition numbers, and computes their spatial coordinates.
4. **Intersection:** Any previously bought item that physically rests within the `Left Wall Corridor` and between the user's location and their final destination (P104) is injected as a suggestion.
5. **Render:** The frontend draws glowing amber indicators precisely mapped to the relevant real-world partitions and drops an "On Your Way" prompt. 

---

<div align="center">
  <i>Designed and Built for the Next Generation of Retail.</i>
</div>
