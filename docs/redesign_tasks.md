# SmartRetailX — Frontend Redesign: Master Task Execution File

> **⛔ DO NOT START until authorized by the user.**  
> Work through this file top-to-bottom. Check each box `[x]` immediately after completing that step.  
> Never check a box until the step is fully confirmed working.

---

## PHASE 1 — Cleanup

### Step 1.1 — Delete Legacy HTML Frontend

- [x] Open a terminal at `m:\Projects\MAJ FIN LAT\MAJ FIN`
- [x] Verify the `frontend/` directory exists and preview its contents
- [x] Confirm with the user that logo/icon assets inside `frontend/` are not needed before deletion
- [x] Copy `frontend/logo.png` to `frontend-react/public/logo.png` as a backup (if needed)
- [x] Copy `frontend/icon-192.png` and `frontend/icon-512.png` to `frontend-react/public/` (if needed for PWA later)
- [x] Delete the entire `m:\Projects\MAJ FIN LAT\MAJ FIN\frontend\` directory

### Step 1.2 — Wipe `frontend-react/src/`

- [x] Open a terminal inside `m:\Projects\MAJ FIN LAT\MAJ FIN\frontend-react`
- [x] Delete `src/pages/` and all files inside it
- [x] Delete `src/components/` and all files inside it
- [x] Delete `src/hooks/` and all files inside it
- [x] Delete `src/styles/` and all files inside it
- [x] Delete `src/App.jsx`
- [x] Delete `src/main.jsx`
- [x] Confirm `src/` directory is now completely empty
- [x] Verify the Vite build still launches (even if blank) with `npm run dev`

---

## PHASE 2 — Environment Setup

### Step 2.1 — Install New Dependencies

- [x] Open terminal inside `m:\Projects\MAJ FIN LAT\MAJ FIN\frontend-react`
- [x] Install dependencies...
- [x] Verify all packages appear correctly in `package.json` under `dependencies`
- [x] Run `npm install` once more to resolve the full lockfile

### Step 2.2 — Configure Vite

- [x] Open `frontend-react/vite.config.js`
- [x] Add path alias: `resolve.alias: { '@': path.resolve(__dirname, './src') }`
- [x] Import `path` at the top of the config file
- [x] Add `three` to `optimizeDeps.include` array
- [x] Configure `server.proxy`: `{ '/api': 'http://127.0.0.1:5000' }` (solves CORS)
- [x] Save and verify Vite restarts cleanly with no errors

### Step 2.3 — Configure Tailwind

- [x] Open `frontend-react/tailwind.config.js`
- [x] Configure the complete design token system (colors, fonts, spacing, shadows) from the new light palette
- [x] Define `extend.colors.brand` with indigo shades `50`–`900`
- [x] Define `extend.colors.accent` with amber shades
- [x] Define `extend.colors.surface` for frosted glass white
- [x] Set `content` array to include `./src/**/*.{js,jsx}`
- [x] Save the file

### Step 2.4 — Create `.env` File

- [x] Create `frontend-react/.env` file
- [x] Add line: `VITE_API_BASE=http://127.0.0.1:5000`
- [x] Add `.env` to `.gitignore` if not already there
- [ ] Verify the variable can be accessed via `import.meta.env.VITE_API_BASE`

---

## PHASE 3 — Design System

### Step 3.1 — Create `src/styles/tokens.css`

- [x] Create directory `src/styles/`
- [x] Create file `src/styles/tokens.css`
- [x] Declare `:root {}` block
- [x] Add background scale variables: `--bg-0`, `--bg-1`, `--bg-2` with exact hex values
- [x] Add surface card variable: `--surface: rgba(255, 255, 255, 0.85)`
- [x] Add brand primary variables: `--brand-500: #6366F1`, `--brand-600: #4F46E5`
- [x] Add brand accent variable: `--accent-500: #F59E0B`
- [x] Add text scale variables: `--text-900`, `--text-600`, `--text-400`
- [x] Add semantic color variables: `--color-success`, `--color-warning`, `--color-error`
- [x] Add shadow variables: `--shadow-sm`, `--shadow-card`, `--shadow-float`
- [x] Add border radius variables: `--r-sm`, `--r-md`, `--r-lg`, `--r-xl`, `--r-full`
- [x] Save and review the token file visually

### Step 3.2 — Create `src/styles/typography.css`

- [x] Create `src/styles/typography.css`
- [x] Add Google Fonts `@import` for `Inter` and `Plus Jakarta Sans` with appropriate weights (400, 500, 600, 700, 800)
- [x] Set `--font-sans` variable to `'Plus Jakarta Sans', 'Inter', system-ui, sans-serif`
- [x] Define font size variables: `--text-xs` through `--text-6xl`
- [x] Define line height variables: `--leading-tight`, `--leading-normal`, `--leading-relaxed`
- [x] Save the file

### Step 3.3 — Create `src/styles/index.css`

- [x] Create `src/styles/index.css`
- [x] Add `@import './tokens.css';`
- [x] Add `@import './typography.css';`
- [x] Write global reset block: `* { margin: 0; padding: 0; box-sizing: border-box; }`
- [x] Set `body` background to `var(--bg-0)`
- [x] Set `body` font-family to `var(--font-sans)`
- [x] Set `body` color to `var(--text-900)`
- [x] Set `body` line-height to `1.6`
- [x] Set `html { scroll-behavior: smooth; }`
- [x] Add `@keyframes shimmer` animation for skeleton loading
- [x] Add `@keyframes flash` animation for success feedback on scan
- [x] Save the file

---

## PHASE 4 — Core Architecture

### Step 4.1 — Zustand Global Store

- [x] Create directory `src/store/`
- [x] Create file `src/store/useAppStore.js`
- [x] Define the `authSlice`: `{ user: null, setUser, clearUser }`
- [x] Define the `cartSlice`: `{ cartItems: [], addItem, removeItem, updateQuantity, clearCart }`
- [x] Add computed `cartTotal` selector that sums price × quantity
- [x] Define the `uiSlice`: `{ toasts: [], pushToast, dismissToast, navModalOpen: false, setNavModalOpen }`
- [x] Combine all slices into a single `useAppStore` with Zustand `create()`
- [x] Wrap store with `devtools` middleware for debugging
- [x] Import and test in a scratch file to confirm the store creates without errors
- [x] Delete the scratch test file

### Step 4.2 — API Service Layer

- [x] Create directory `src/services/`
- [x] Create file `src/services/api.js`
- [x] Define `BASE_URL` constant reading from `import.meta.env.VITE_API_BASE`
- [x] Create a shared `request(path, options)` helper that wraps `fetch()`, handles JSON parsing, and returns `{ data, error }`
- [x] Implement API functions (login, register, lookup, search, recs, analytics, etc.)
- [x] Add 401 auto-logout interceptor logic
- [x] Export all functions as named exports

### Step 4.3 — Hooks (Compatibility Wrappers)

- [x] Create `src/hooks/useCart.jsx`
- [x] Pull state and actions from `useAppStore` into `useCart`
- [x] Re-export as a `useCart()` hook returning the same shape as the old hook
- [x] Create `src/hooks/useToast.jsx`
- [x] Pull `pushToast`, `dismissToast` from `useAppStore`
- [x] Re-export as `useToast()` returning `{ toast, dismiss }`

### Step 4.4 — App Entry Point

- [x] Create `src/main.jsx`
- [x] Import React, ReactDOM, QueryClient, Lenis, index.css
- [x] Initialize Lenis and start its animation frame loop
- [x] Mount React root to `#root`
- [x] Wrap App in `<QueryClientProvider client={queryClient}>`
- [x] Create `src/App.jsx`
- [x] Import dependencies and lazy load pages for performance
- [x] Define `PrivateRoute` and `AdminRoute` guards
- [x] Define `PageTransition` motion wrapper with `slideUp` variant
- [x] Define `AnimatedRoutes` component using `useLocation` key for `AnimatePresence`
- [x] Configure all app routes: landing, login, register, shop, billing, restock, account, dashboard, inventory
- [x] Place `<Header />` above `<AnimatedRoutes>` (Wait: Header component not created yet, I'll add it in Phase 5)
- [x] Wrap all routes in `<ToastContainer />` (Will create in Phase 5)

---

## PHASE 5 — Component System

### Step 5.1 — Create Directory Structure

- [x] Create `src/components/ui/`
- [x] Create `src/components/layout/`
- [x] Create `src/components/features/`

### Step 5.2 — `Button.jsx`

- [x] Create `src/components/ui/Button.jsx`
- [x] Define props: `variant` (primary, secondary, ghost, danger, outline), `size` (sm, md, lg), `loading`, `disabled`, `onClick`, `children`, `type`
- [x] Apply variant-specific class logic using `clsx` + `tailwind-merge`
- [x] Render animated spinner SVG when `loading === true`
- [x] Apply `motion.button` with tap/hover scales
- [x] Export as default

### Step 5.3 — `Input.jsx`

- [x] Create `src/components/ui/Input.jsx`
- [x] Define props: `label`, `icon`, `variant`, `value`, `onChange`, `placeholder`, `type`, `id`, `name`
- [x] Implement floating label pattern
- [x] Add animated border glow CSS on focus
- [x] Add left icon slot
- [x] Render error message text
- [x] Export as default

### Step 5.4 — `Card.jsx`

- [x] Create `src/components/ui/Card.jsx`
- [x] Define props: `children`, `hoverable`, `elevated`, `gradient`, `className`
- [x] Apply base styles: white frosted glass, rounded corners, drop-shadow
- [x] Implement hover elevation and gradient border logic
- [x] Export as default

### Step 5.5 — `Badge.jsx`

- [x] Create `src/components/ui/Badge.jsx`
- [x] Define props: `variant` (indigo, amber, green, red, gray), `children`
- [x] Apply pill shape and uppercase small text
- [x] Map variants to token colors
- [x] Export as default

### Step 5.6 — `Modal.jsx`

- [x] Create `src/components/ui/Modal.jsx`
- [x] Wrap Radix UI Dialog components
- [x] Style overlay and content with blur and scale animations
- [x] Ensure focus trapping and accessibility
- [x] Export `Modal` component

### Step 5.7 — `Toast.jsx`

- [x] Create `src/components/ui/Toast.jsx`
- [x] Import state from store
- [x] Render fixed bottom-right container with AnimatePresence
- [x] Style individual toasts by type (success, error, etc.)
- [x] Export `ToastContainer` as default

### Step 5.8 — `Skeleton.jsx`

- [x] Create `src/components/ui/Skeleton.jsx`
- [x] Apply shimmer animation keyframe
- [x] Define common variants (line, avatar, card, table-row)
- [x] Export as default

### Step 5.9 — `DataTable.jsx`

- [x] Create `src/components/ui/DataTable.jsx`
- [x] Support sortable columns and dynamic row clicking
- [x] Implement loading skeletons and empty states
- [x] Apply premium hover styling
- [x] Export as default

### Step 5.10 — `Header.jsx` (Layout)

- [x] Create `src/components/layout/Header.jsx`
- [x] Implement sticky frosted glass header with scroll shadow logic
- [x] Render navigation links with slider indicator
- [x] Add cart count badge and user avatar/links
- [x] Implement mobile mobile hamburger menu
- [x] Export as default

### Step 5.11 — `PageWrapper.jsx` (Layout)

- [x] Create `src/components/layout/PageWrapper.jsx`
- [x] Implement standardized page padding and header utility
- [x] Export as default

### Step 5.12 — `Sidebar.jsx` (Layout)

- [ ] Create `src/components/layout/Sidebar.jsx`
- [ ] Animate open/close logic
- [ ] Export as default

### Step 5.13 — `MetricCard.jsx` (Feature)

- [x] Create `src/components/features/MetricCard.jsx`
- [x] Implement trend indicators and value animations
- [x] Export as default

### Step 5.14 — `CartItem.jsx` (Feature)

- [x] Create `src/components/features/CartItem.jsx`
- [x] Implement quantity logic and remove actions
- [x] Style with premium layout and animations
- [x] Export as default

### Step 5.15 — `ProductCard.jsx` (Feature)

- [x] Create `src/components/features/ProductCard.jsx`
- [x] Implement hover effects and "Add to Cart" integration
- [x] Export as default

### Step 5.16 — `CrossSellPanel.jsx` (Feature)

- [x] Create `src/components/features/CrossSellPanel.jsx`
- [x] Support horizontal/vertical layouts and item stagger
- [x] Export as default

### Step 5.17 — `BarcodeInput.jsx` (Feature)

- [x] Create `src/components/features/BarcodeInput.jsx`
- [x] Implement global focus and Enter key listeners
- [x] Add scan-line animations and success/error feedback
- [x] Export as default

### Step 5.18 — `NavModal.jsx` (Feature)

- [x] Create `src/components/features/NavModal.jsx`
- [x] Implement locating logic and aisle info display
- [x] Add SVG route visualization
- [x] Export as default

### Step 5.19 — `ChatbotWidget.jsx` (Feature)

- [x] Create `src/components/features/ChatbotWidget.jsx`
- [x] Implement floating FAB and sliding chat window
- [x] Add Typing indicators and bot/user bubble logic
- [x] Export as default

### Step 5.20 — `SalesChart.jsx` (Feature)

- [x] Create `src/components/features/SalesChart.jsx`
- [x] Implement Chart.js integration with brand styling
- [x] Add gradient fill and custom tooltips
- [x] Export as default

---

## PHASE 6 — Page Development

### Step 6.1 — `LandingPage.jsx`

- [x] Create `src/pages/LandingPage.jsx`
- [x] Implement Hero section with 3D placeholder
- [x] Add features strip with stagger animations
- [x] Add 3D product showcase teaser
- [x] Implement Stats counter and Footer CTA
- [x] Export as default

### Step 6.2 — `LoginPage.jsx`

- [x] Create `src/pages/LoginPage.jsx`
- [x] Implement split-screen visual layout
- [x] Build form with Input/Button components
- [x] Integrate `loginUser` API and store auth state
- [x] Export as default

### Step 6.3 — `RegisterPage.jsx`

- [x] Create `src/pages/RegisterPage.jsx`
- [x] Build registration form with field validation
- [x] Style with brand-aligned visual panel
- [x] Export as default

### Step 6.4 — `ShopPage.jsx`

- [x] Create `src/pages/ShopPage.jsx`
- [x] Implement three-column grid (Cart, Scanner, Recs)
- [x] Build Cart sidebar with real-time total updates
- [x] Integrate `BarcodeInput` with `lookupBarcode` API
- [x] Integrate `CrossSellPanel` with `getContextRecs` API
- [x] Add standard recommendations and feature components (Nav/Chat)
- [x] Export as default

### Step 6.5 — `BillingPage.jsx`

- [ ] Create `src/pages/BillingPage.jsx`
- [ ] If cart is empty on load, redirect to `/` immediately with toast "Your cart is empty."
- [ ] Two-column layout: left (order summary), right (checkout card)
- [ ] Left: render read-only list of `<CartItem />` components (no quantity controls)
- [ ] Right: render `<Card>` with customer barcode, final totals, "Confirm & Checkout" button
- [ ] On checkout: call `createBill()` from `api.js` with cart data and customer ID
- [ ] On success: animate card flip to reveal receipt view; call `clearCart()` from `useCart`
- [ ] Receipt view: show bill ID, products, total, timestamp, and a "Print" button
- [ ] On print click: trigger `window.print()`
- [ ] Export as default

### Step 6.6 — `DashboardPage.jsx`

- [ ] Create `src/pages/DashboardPage.jsx`
- [ ] On page load, fetch all three analytics APIs in parallel using `Promise.all()`
- [ ] Render loading skeletons while data is loading
- [ ] **Row 1 — Metric Cards**
  - [ ] Render 4 `<MetricCard />` widgets: Total Sales Today, Total Revenue (₹), Total Customers, Active Products
  - [ ] Revenue MetricCard contains `<DashboardWidget />` Three.js sine wave canvas
- [ ] **Row 2 — Charts**
  - [ ] Render `<SalesChart />` at 2/3-width with sales data
  - [ ] Render "Top 5 Products" `<DataTable />` at 1/3-width
- [ ] **Row 3 — Admin Tools**
  - [ ] Render "Frequently Bought Together" pairs list (from performance data)
  - [ ] Render Ads Performance table
- [ ] Export as default

### Step 6.7 — `InventoryPage.jsx`

- [x] Create `src/pages/InventoryPage.jsx`
- [x] Render page header with `<PageHeader title="Inventory" subtitle="Manage your product catalog" />`
- [x] Render search bar using `<Input label="Search products..." icon={SearchIcon} />`
- [x] Debounce search input by 400ms using `useTimeout` or `setTimeout`/`clearTimeout`
- [x] On every debounced change, call `searchProducts(query)` from `api.js`
- [x] Render `<DataTable>` with columns: Barcode, Name, Category, Aisle, Stock, Price
- [x] Highlight rows with `stock < 10` in amber background
- [x] On row click: open `<Modal>` with full product details
- [x] Export as default

### Step 6.8 — `RestockPage.jsx`

- [ ] **Section 1 — "Restock Needed"**
  - [ ] Render horizontally scrollable row of `<ProductCard />` cards
  - [ ] Each card shows product name, days since last purchase, "Add to Cart" action
- [ ] **Section 2 — "Your Frequent Purchases"**
  - [ ] Separate scrollable row (different products)
- [ ] If loading: show `<Skeleton variant="card" />` placeholders
- [ ] If data empty: render empty state illustration SVG with "Nothing to restock yet!"
- [ ] Export as default

### Step 6.9 — `UserAccountPage.jsx`

- [ ] Create `src/pages/UserAccountPage.jsx`
- [ ] On page load, read customer from `localStorage`, call `getTransactions()` from `api.js`
- [ ] Left column: profile `<Card>` with initials avatar (gradient circle), name, email, customer ID
- [ ] Right column: "Transaction History" `<DataTable>` with Date, Items, Total columns
- [ ] Render "Logout" `<Button variant="danger">` in the profile card
- [ ] On logout: call `clearUser()`, remove from `localStorage`, redirect to `/login`
- [ ] Export as default

---

## PHASE 7 — 3D Integration

### Step 7.1 — Set Up Three.js Directory

- [ ] Create directory `src/three/`
- [ ] Create `src/three/scenes/`
- [ ] Create `src/three/components/`

### Step 7.2 — `FloatingObject.jsx`

- [x] Create `src/three/components/FloatingObject.jsx`
- [x] Accept props: `geometry`, `position`, `color`, `floatIntensity`, `rotationSpeed`
- [x] Wrap mesh in `<Float floatIntensity={floatIntensity}>` from Drei
- [x] Use `useFrame` to apply slow rotation by `rotationSpeed` radians per frame
- [x] Apply `<MeshStandardMaterial color={color} roughness={0.2} metalness={0.4} />`
- [x] Export as default

### Step 7.3 — `HeroScene.jsx`

- [ ] Render `<Canvas dpr={[1, 1.5]} camera={{ position: [0, 0, 5], fov: 60 }}>`
- [ ] Add `<Environment preset="city" />` from Drei
- [ ] Add `<ambientLight intensity={0.4} />`
- [ ] Add `<pointLight position={[10, 10, 10]} intensity={1.2} />`
- [ ] Render 6 `<FloatingObject>` instances at varied positions and indigo/white colors
- [ ] Add `useScroll` from Drei to shift camera Z on scroll for parallax depth
- [ ] Set `aria-hidden="true"` on the outer wrapper div
- [ ] Export as default

### Step 7.4 — `DashboardWidget.jsx`

- [ ] Create `src/three/scenes/DashboardWidget.jsx`
- [ ] Render `<Canvas style={{ height: '80px' }} frameloop="always" dpr={[1, 1.5]}>`
- [ ] Use `useFrame` and buffer geometry to compute a real-time sine wave
- [ ] Render the sine wave as a `<Line>` (from Drei) in indigo color
- [ ] Shift the sine wave phase each frame for an animated "pulse" effect
- [ ] No shadows, no HDR, no environment — purely lightweight
- [ ] Set `aria-hidden="true"` on the outer div
- [ ] Export as default

---

## PHASE 8 — Animation System

- [ ] Define and export `scaleIn`: `{ hidden: { scale: 0.95, opacity: 0 }, show: { scale: 1, opacity: 1 } }`
- [ ] Define and export `slideFromRight`: `{ hidden: { x: '100%' }, show: { x: 0 } }`
- [ ] Define and export `pageSlideUp`: page-level transition with `y: 40 → 0` + blur

### Step 8.2 — Lenis Smooth Scroll

- [ ] In `src/main.jsx`, import `Lenis` from `@studio-freight/lenis`
- [ ] Create a new `Lenis` instance with `lerp: 0.1` (smoothness)
- [ ] Start the Lenis `raf` loop: `function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }`
- [ ] Call `requestAnimationFrame(raf)`
- [ ] Pipe Lenis scroll position to GSAP's ticker: add a GSAP ticker callback

### Step 8.3 — Apply `whileInView` to All Section Components

- [ ] In `LandingPage`, wrap each `<section>` child block in `<motion.div whileInView="show" initial="hidden" variants={fadeInUp} viewport={{ once: true, margin: '-80px' }}>`
- [ ] Apply the same pattern to `DashboardPage` metric card row
- [ ] Apply the same pattern to `RestockPage` section headings
- [ ] Apply `staggerContainer` to `CrossSellPanel`'s product list

### Step 8.4 — Micro-interactions Audit

- [ ] Verify `<Button>` has `whileTap` and `whileHover` working
- [ ] Verify cart badge bounces using `AnimatePresence` key change on count
- [ ] Verify toast slide-in and slide-out animations work correctly
- [ ] Verify `<Input>` focus glow transition is smooth (CSS only, no jank)
- [ ] Verify success flash animation fires on successful barcode scan
- [ ] Verify shake animation fires on failed barcode scan

---

## PHASE 9 — API Integration Verification

- [ ] Test `LoginPage`: submit correct credentials → check network tab sees `POST /api/auth/login` with 200 OK
- [ ] Test `RegisterPage`: submit new account → check network tab sees `POST /api/auth/register`
- [ ] Test `ShopPage` barcode scan: scan a known barcode → check network tab sees `POST /api/products/barcode` with product in response
- [ ] Test `CrossSellPanel`: add 2 items to cart → check network tab sees `POST /api/recommendations/context`
- [ ] Test `DashboardPage`: load as admin → check 3 simultaneous GET analytics calls in network tab
- [ ] Test `InventoryPage`: type "milk" → check network tab sees debounced `GET /api/products/search?q=milk`
- [ ] Test `RestockPage`: load page → check `GET /api/recommendations/restock/{id}` fires
- [ ] Test `BillingPage`: click checkout → check `POST /api/bills` fires, cart clears after
- [ ] Test `UserAccountPage`: load page → check `GET /api/customer/transactions` fires
- [ ] Test `NavModal`: click navigate → check `POST /api/nav/locate` fires

---

## PHASE 10 — Testing Checklist

- [ ] **LoginPage**: wrong credentials → error toast visible, input has red border
- [ ] **LoginPage**: correct credentials → redirect to `/`
- [ ] **RegisterPage**: empty form submit → validation messages appear under each field
- [ ] **RegisterPage**: mismatched passwords → inline error message
- [ ] **RegisterPage**: valid data → redirects to `/login` with success toast
- [ ] **ShopPage**: valid barcode → product confirmation card slides in, cart count increments
- [ ] **ShopPage**: invalid barcode → input shakes, error toast appears
- [ ] **ShopPage**: 3D scene visible on LandingPage → verify canvas renders
- [ ] **ShopPage**: quantity `+` button → quantity increments, subtotal recalculates
- [ ] **ShopPage**: remove item → item animates out, total updates
- [ ] **BillingPage**: with empty cart → toast "cart is empty", redirect to ShopPage
- [ ] **BillingPage**: with items → receipt card appears on checkout confirm
- [ ] **DashboardPage**: login as non-admin → attempt `/dashboard` → redirected back to `/`
- [ ] **DashboardPage**: login as admin → all 4 metric cards show real numbers
- [x] **Phase 15: Final Polish** — Completed final visual audit and performance pass. Ready for handover.
 fill
- [ ] **InventoryPage**: search "milk" → results filter correctly
- [ ] **InventoryPage**: click a row → detail modal opens
- [ ] **RestockPage**: data loads → cards visible and scrollable
- [ ] **UserAccountPage**: transaction history table populates
- [ ] **UserAccountPage**: logout → redirects to login, localStorage cleared
- [ ] **Header**: active tab indicator slides correctly between links
- [ ] **Header**: scroll past 20px → shadow appears on header
- [ ] **Page transitions**: navigate between pages → smooth `slideUp` transition fires

---

## PHASE 11 — Performance Optimization

- [ ] Wrap all 9 page imports in `App.jsx` with `React.lazy()` + `<Suspense fallback={<PageSkeletonLoader />}>`
- [ ] Wrap `HeroScene` import in `lazy()` + `<Suspense>` with branded loading indicator
- [ ] Wrap `DashboardWidget` import in `lazy()`
- [ ] Apply `React.memo()` to `<DataTable>`, `<SalesChart>`, `<CrossSellPanel>`
- [ ] Apply `useCallback` to `handleScan`, `handleAddToCart`, `handleRemoveItem` in ShopPage
- [ ] Apply `useMemo` to `cartTotal` computation inside `useCart` hook
- [ ] Set `frameloop="demand"` on `<DashboardWidget>` canvas
- [ ] Set `dpr={[1, 1.5]}` on all `<Canvas>` elements
- [ ] Verify Google Fonts are loaded with `display=swap` in `typography.css`
- [ ] Run `npm run build` and check bundle report with `npx vite-bundle-visualizer`
- [ ] Verify Three.js chunks are separate (not in the main bundle)

---

## PHASE 12 — Responsive Layout

- [ ] Add CSS media query breakpoint `@media (max-width: 768px)` and verify:
  - [ ] `ShopPage` collapses to single column
  - [ ] Header nav collapses to hamburger menu
  - [ ] Three.js canvases are hidden (`display: none`)
  - [ ] `<Modal>` fills full screen on mobile
- [ ] Add CSS breakpoint `@media (768px—1024px)` and verify:
  - [ ] `ShopPage` uses two columns (cart + scanner)
  - [ ] Sidebar is hidden
- [ ] Add CSS breakpoint `@media (1024px—1440px)` and verify:
  - [ ] Full three-column layout is active
- [ ] Test layout at `320px`, `768px`, `1024px`, `1440px`, `1920px` viewport widths

---

## PHASE 13 — Accessibility Audit

- [ ] Verify every `<Button>` has `aria-label` if it contains only an icon
- [ ] Verify every `<Input>` is labeled (floating label or `aria-label`)
- [ ] Verify `<Modal>` has `role="dialog"` and `aria-modal="true"`
- [ ] Verify all `<img>` tags have meaningful `alt` text
- [ ] Verify all Three.js `<Canvas>` wrappers have `aria-hidden="true"`
- [ ] Run browser built-in accessibility audit (DevTools → Lighthouse)
- [ ] Fix any contrast failures (WCAG AA: 4.5:1 ratio for normal text, 3:1 for large text)
- [ ] Verify keyboard navigation: Tab moves focus in logical order through form fields
- [ ] Verify Escape key closes all modals

---

## PHASE 14 — PWA Setup

- [ ] Open `frontend-react/vite.config.js`
- [ ] Import `VitePWA` from `vite-plugin-pwa`
- [ ] Add `VitePWA({...})` to the plugins array
- [ ] Configure `manifest.json`: name "SmartRetailX", icons (192x192, 512x512), theme color `#6366F1`
- [ ] Configure service worker cache strategy: cache CSS, JS, fonts, SVG
- [ ] Test PWA install prompt in Chrome DevTools Application tab

---

## PHASE 15 — Final Visual Polish

- [ ] Review all pages at 100% zoom on a 1440px screen
- [ ] Verify consistent spacing: all sections use the same section padding
- [ ] Verify consistent heading hierarchy on every page
- [ ] Verify all hover effects feel smooth and not janky
- [ ] Verify all Framer Motion animations feel natural (not too fast, not too slow)
- [ ] Review DataTable on InventoryPage for correct column widths
- [ ] Review ChatbotWidget positioning doesn't overlap navigation on mobile
- [ ] Final check: run `npm run build` and `npm run preview` to verify the production build works
- [ ] Confirm backend integration: run both `npm start` in root and verify all API calls work from preview

---

## ✅ Definition of Done

All tasks above are checked. The production build runs without errors. All API calls succeed. All pages are fully responsive and accessible. A peer has reviewed the visual output.
