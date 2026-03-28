# SmartRetailX - Complete Project Documentation & React Migration Guide

Welcome to the **SmartRetailX** documentation! Whether you're a seasoned developer or a complete beginner, this guide will walk you through EVERYTHING in the project. It explains how the system works, breaks down the current codebase, and provides a **step-by-step guide to rebuilding the entire frontend in React**.

---

## 📖 Table of Contents
1. [Project Overview](#1-project-overview)
2. [How the System Works (Simple Explanation)](#2-how-the-system-works-simple-explanation)
3. [Current UI Analysis (HTML + React)](#3-current-ui-analysis-html--react)
4. [UI Components Breakdown & Extraction](#4-ui-components-breakdown--extraction)
5. [React Conversion Plan](#5-react-conversion-plan)
6. [Backend Overview](#6-backend-overview)
7. [API Documentation (The Brains)](#7-api-documentation-the-brains)
8. [Frontend–Backend Interaction](#8-frontendbackend-interaction)
9. [Complete React Folder Structure](#9-complete-react-folder-structure)
10. [Step-by-Step Rebuild Guide](#10-step-by-step-rebuild-guide)
11. [Glossary (For Beginners)](#11-glossary-for-beginners)

---

## 1. Project Overview
**SmartRetailX** is a modern, intelligent retail software system designed to power local grocery stores or supermarkets. It includes a frontend for store managers and cashiers (to track inventory, process bills, and analyze sales) and a backend that acts as the "brain," managing databases, making AI-driven product recommendations (Market Basket Analysis), calculating retail navigation paths, and tracking sales history.

The project currently exists in a **hybrid state**:
*   **Legacy Frontend (HTML/CSS):** The older version of the user interface built purely with HTML, CSS, and basic JavaScript.
*   **Modern Frontend (`frontend-react`):** The new version being built with **React** containing a beautiful "Dark Professional" dark mode theme, glassmorphism, and responsive design.
*   **Backend (`backend/app.py`):** A Python **Flask** server that connects to PostgreSQL and SQLite databases, offering machine learning recommendations, billing, and inventory APIs.

---

## 2. How the System Works (Simple Explanation)

Imagine a restaurant:
*   The **Frontend (React/HTML)** is the dining area and the menu. It's what the user interacts with. They click buttons and scan items.
*   The **Backend (Python Flask)** is the kitchen. When a user clicks "Checkout" (places an order), the frontend sends a request to the backend. The backend calculates the total, updates the database (the pantry), and sends back a receipt (response).
*   The **Database (PostgreSQL / SQLite)** is the filing cabinet where everything (user accounts, product barcodes, past bills) is permanently saved.

**Typical Flow:**
1.  User enters a barcode in the React **Shop Page**.
2.  React sends that barcode to the Python Backend (`/api/products/barcode`).
3.  The Backend finds the product in the Database and sends back the name and price.
4.  React displays the product on the screen.
5.  When the user adds it to the cart, the backend's AI looks at the cart and suggests "Frequently Bought Together" items!

---

## 3. Current UI Analysis (HTML + React)

### Legacy HTML Version (`/frontend/`)
The old layout consists of separate `.html` files linked together: `index.html` (Dashboard), `login.html`, `register.html`, `store.html`, `billing.html`, `inventory.html`, `restock.html`, and `all_ads.html`. It uses one massive CSS file (`style.css`).

### Modern React Version (`/frontend-react/`)
The React version utilizes a Single Page Application (SPA) structure. Instead of refreshing the page when navigating, React simply swaps out the "Components" being displayed.

**Design System (Extracted from CSS):**
*   **Backgrounds:** Deep slate blues (`#1e293b`, `#0f172a`, `#334155`).
*   **Primary Accent:** Indigo / Violet (`#6366f1`), transitioning into beautiful purples (`#8b5cf6`).
*   **Text Colors:** Off-white (`#f8fafc`) for headers, muted grays (`#94a3b8`) for descriptions.
*   **Effects:** Glassmorphism (blurring the background behind slightly transparent dark cards) and smooth drop-shadows on hover (`transform: translateY(-4px)`).

---

## 4. UI Components Breakdown & Extraction

To build this in React, we don't code the whole page at once. We break it down into small, reusable LEGO blocks called **Components**.

### 🔹 Buttons
*   **`PrimaryButton`**: Used for main actions like "Checkout" or "Login".
    *   *Colors:* Background `#6366f1`, Text `white`.
*   **`GhostButton`**: Used for secondary actions (e.g., "Cancel"). Background is transparent until hovered.
*   **`NavScanButton`**: A specialized modular button used for Navigation/Scanning logic (already built in React).

### 🔹 Layout & Cards
*   **`GlassCard`**: A container utilizing backdrop blur for a modern look. Used for grouping items.
*   **`MetricCard`**: A dashboard widget showing numbers (e.g., "Total Sales today").
*   **`CartItem`**: Displays a single item's image, name, price, and a remove button.

### 🔹 Navigation
*   **`Header` / `PillNav`**: The top bar of the application containing the logo, user profile, and main page links.
*   **`NavModal`**: A popup window that displays the store map or navigation paths.

---

## 5. React Conversion Plan

If we are mapping the old HTML files to React Pages, it looks like this:

| Legacy HTML File | ➜ | React Page Component | State / Hooks Needed |
| :--- | :--- | :--- | :--- |
| `index.html` | ➜ | `DashboardPage.jsx` | `useEffect` (Fetch sales analytics), `useState` |
| `store.html` | ➜ | `ShopPage.jsx` | `useCart()` (Custom hook), Context API recommendations |
| `restock.html` | ➜ | `RestockPage.jsx` | `useEffect` (Fetch restock APIs) |
| `billing.html` | ➜ | `BillingPage.jsx` | Calculates totals, calls `/api/bills` |
| `inventory.html` | ➜ | `InventoryPage.jsx` | `useState` (List of products, search queries) |
| `login.html` | ➜ | `LoginPage.jsx` | `useState` (Username/Password) |

---

## 6. Backend Overview

The backend is built with **Python 3** and **Flask**.
The entry point is `backend/app.py`.

**Key Backend Modules:**
*   **`app.py`**: The router. It catches web requests, figures out what they want, and sends back data.
*   **`voice_assistant.py`**: A speech-to-text Python script allowing voice search for products.
*   **`path_planner.py` & `visualizer.py`**: Calculates the shortest physical walking route through the grocery store aisles to find specific products!
*   **`recommendations.py`**: The Machine Learning module handling user patterns.

---

## 7. API Documentation (The Brains)

Here are the most important endpoints the Frontend calls:

### Authentication
*   **`POST /api/auth/login`**: Send `{ identifier, password }`. Returns `{ customer_id, name, is_admin }`.
*   **`POST /api/auth/register`**: Register a new user account.

### Products & Shop
*   **`POST /api/products/barcode`**: Send `{ barcode: "12345" }`. Returns product name, price, aisle, and stock.
*   **`GET /api/products/search?q=milk`**: Text-based search returning matching items.

### Analytics (Dashboard)
*   **`GET /api/analytics/sales`**: Returns total revenue, daily growth, etc.
*   **`GET /api/analytics/highest-sales`**: Returns Top 5 best-selling items.

### Recommendations (Market Basket Analysis)
*   **`POST /api/recommendations/context`**
    *   *What it does:* You send it the items currently in the user's cart. It runs the "Apriori" ML algorithm to figure out what they will likely buy next.
    *   *Input:* `{ cart_barcodes: ["123", "456"], limit: 5 }`
    *   *Output:* List of recommended companion products.

### Cart & Billing
*   **`POST /api/bills`**: Submits a cart for final checkout and creates a permanent record in `purchase_history`.

---

## 8. Frontend–Backend Interaction

**Example: Scanning an Item in React**
1.  **User Action:** Cashier types "89010300" into an input field in `ShopPage.jsx` and hits Enter.
2.  **React Logic (`onChange` / `onSubmit`):** A Javascript function runs. It uses `fetch()` to make an HTTP POST request.
3.  **Network Request:** React sends: `POST http://127.0.0.1:5000/api/products/barcode` with raw JSON body `{"barcode": "89010300"}`.
4.  **Backend Processing:** `app.py` catches the request, connects to PostgreSQL, runs `SELECT * FROM products WHERE barcode = '89010300'`, and returns JSON.
5.  **State Update:** React receives the JSON. It updates a State variable (`const [cart, setCart] = useState([])`).
6.  **Re-render:** Because the state changed, React automatically updates the UI to show the new item visually!

---

## 9. Complete React Folder Structure

To keep the project clean, organize the React code (`frontend-react/`) like this:

```text
frontend-react/
│
├── index.html           # The single HTML file that loads React
├── package.json         # NPM dependencies (React, Vite, etc.)
├── vite.config.js       # Bundler configuration
│
└── src/
    ├── main.jsx         # React application entry point
    ├── App.jsx          # Setup routing (React Router) to pages
    │
    ├── components/      # Reusable LEGO blocks
    │   ├── Header.jsx   # Top navigation bar
    │   ├── MagicBento.jsx # Special grid layouts
    │   └── ui/          # Standardized buttons, inputs, etc.
    │
    ├── pages/           # Full screen views
    │   ├── DashboardPage.jsx
    │   ├── ShopPage.jsx
    │   ├── LoginPage.jsx
    │   └── RestockPage.jsx
    │
    ├── hooks/           # Custom reusable logic
    │   ├── useCart.jsx  # Cart state management
    │   └── useToast.jsx # Popup notification logic
    │
    └── styles/          # Global and component CSS
        └── index.css    # Contains the root palette and Tailwind (if used)
```

---

## 10. Step-by-Step Rebuild Guide

If you wanted to start the React frontend from absolute zero, follow these steps:

### Step 1: Initialize the Project
Open your terminal and create a new Vite project:
```bash
npm create vite@latest frontend-react -- --template react
cd frontend-react
npm install
```

### Step 2: Set up Routing
Install React Router to manage navigating between pages:
```bash
npm install react-router-dom
```
In `src/App.jsx`, import `BrowserRouter`, `Routes`, and `Route`. Wrap your entire app in the router and define paths (e.g., `<Route path="/login" element={<LoginPage />} />`).

### Step 3: Copy the Design System
Create `src/styles/index.css` and copy the `:root` variables from the legacy `style.css`. This ensures your React app has the exact same deep blue colors and fonts.

### Step 4: Build Layout Components
Create `src/components/Header.jsx`. Give it the logo, navigation links, and a logout button. Place this Header inside your `App.jsx` outside of the `<Routes>` so it appears on every page.

### Step 5: Build the Shop Page (Core Feature)
Create `src/pages/ShopPage.jsx`.
*   Create an input field for the barcode.
*   Attach a function to the input that calls the backend `fetch('/api/products/barcode')`.
*   Store the result in `useState`.
*   Map over the state array to render a list of `<CartItem />` components.

### Step 6: Connect the "Frequently Bought Together" AI
In your `ShopPage.jsx`, whenever the Cart state changes, automatically fire off a `useEffect` hook to call `/api/recommendations/context`. Take the response and display a row of recommended products at the bottom of the screen.

---

## 11. Glossary (For Beginners)

*   **API (Application Programming Interface):** A bridge that allows the React Frontend to talk to the Python Backend.
*   **JSON:** A text format used to send data over the internet. It looks like a JavaScript dictionary.
*   **Component:** An isolated piece of the UI in React (like a single button or a single product card).
*   **State / `useState`:** React's memory. When "state" changes, the UI automatically refreshes.
*   **Props:** Short for "Properties." Data passed from a parent component down to a child component (e.g., passing a `price="5.99"` prop to a `ProductCard` component).
*   **PostgreSQL:** The robust database system used in the backend to store data permanently.
*   **Vite:** The tool (bundler) used to compile React code so the browser can understand it quickly.

---

### 🎉 Conclusion
You now have the exact blueprint of SmartRetailX. By focusing on building one small React component at a time and linking it to the specified Backend APIs, converting or expanding this project becomes a straightforward, manageable process!
