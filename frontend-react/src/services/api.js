const BASE_URL = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const defaultOptions = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  }
  try {
    const response = await fetch(url, defaultOptions)
    const data = await response.json()
    if (!response.ok) {
      if (response.status === 401) window.dispatchEvent(new CustomEvent('unauthorized'))
      return { data: null, error: { message: data.message || 'Something went wrong', status: response.status } }
    }
    return { data, error: null }
  } catch (err) {
    return { data: null, error: { message: 'Network error. Is the server running?', status: 500 } }
  }
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const loginUser = (identifier, password) =>
  request('/api/auth/login', { method: 'POST', body: JSON.stringify({ identifier, password }) })

export const registerUser = (data) =>
  request('/api/auth/register', { method: 'POST', body: JSON.stringify(data) })

// ── Products & Search ─────────────────────────────────────────────────────────
export const lookupBarcode = (barcode) =>
  request('/api/products/barcode', { method: 'POST', body: JSON.stringify({ barcode }) })

export const searchProducts = (query) =>
  request(`/api/products/search?q=${encodeURIComponent(query)}`)

// ── Recommendations ───────────────────────────────────────────────────────────
export const getContextRecs = (cartBarcodes, lastAdded, limit = 5) =>
  request('/api/recommendations/context', { method: 'POST', body: JSON.stringify({ cart_items: cartBarcodes, last_added: lastAdded, limit }) })

export const getGeneralRecs = (limit = 10) =>
  request(`/api/recommendations/general?limit=${limit}`)

export const getRestockRecs = (customerId) =>
  request(`/api/recommendations/restock/${customerId}`)

export const getMarketBasket = (barcode, limit = 4) =>
  request('/api/recommendations/basket', { method: 'POST', body: JSON.stringify({ barcode, limit }) })

export const getCartScore = (cartItems) =>
  request('/api/recommendations/cart-score', { method: 'POST', body: JSON.stringify({ cart_items: cartItems }) })

// ── Cart & Billing ────────────────────────────────────────────────────────────
export const processCheckout = (cartItems) =>
  request('/api/bills', { method: 'POST', body: JSON.stringify({ items: cartItems }) })

// ── Inventory ─────────────────────────────────────────────────────────────────
export const getInventory = () =>
  request('/api/inventory/all')

export const updateStock = (barcode, quantity) =>
  request('/api/inventory/update', { method: 'POST', body: JSON.stringify({ barcode, quantity }) })

// ── Navigation & Location ─────────────────────────────────────────────────────
export const locateProduct = (name) =>
  request('/api/nav/locate', { method: 'POST', body: JSON.stringify({ name }) })

export const getNavPath = (from, to) =>
  request(`/api/nav/path?from=${from}&to=${to}`)

export const getEspStatus = () =>
  request('/api/nav/esp-status')

// ── Advertisements ────────────────────────────────────────────────────────────
export const getAds = (position = '') =>
  request(`/api/nav/ads${position ? `?position=${position}` : ''}`)

export const getAdminAds = () =>
  request('/api/admin/ads')

export const createAd = (adData) =>
  request('/api/admin/ads', { method: 'POST', body: JSON.stringify(adData) })

export const updateAd = (id, adData) =>
  request(`/api/admin/ads/${id}`, { method: 'PATCH', body: JSON.stringify(adData) })

export const deleteAd = (id) =>
  request(`/api/admin/ads/${id}`, { method: 'DELETE' })

export const logAdImpression = (adId) =>
  request('/api/nav/ads/impression', { method: 'POST', body: JSON.stringify({ ad_id: adId }) })

// ── Analytics ─────────────────────────────────────────────────────────────────
export const getDashboardStats = () =>
  request('/api/analytics/dashboard')

export const getSalesAnalytics = (month = '', year = '') => {
  const params = month && year ? `?month=${month}&year=${year}` : ''
  return request(`/api/analytics/sales${params}`)
}

export const getInventoryAnalytics = () =>
  request('/api/analytics/inventory')

export const getProductPerformance = (limit = 5) =>
  request(`/api/analytics/products/performance?limit=${limit}`)

export const getCategoryBreakdown = () =>
  request('/api/analytics/category-breakdown')

export const getAisleHeatmap = () =>
  request('/api/analytics/heatmap')

// ── Customer History & Suggestions ──────────────────────────────────────────────
export const getTransactions = (customerId) =>
  request(`/api/customer/history?customer_id=${customerId}`)

export const getPathSuggestions = (customerId, targetPartition) =>
  request(`/api/nav/path-suggestions?customer_id=${customerId}&target=${targetPartition}`)

// ── Chat ──────────────────────────────────────────────────────────────────────
export const chatWithRecipeBot = (message) =>
  request('/api/chat/recipe', { method: 'POST', body: JSON.stringify({ message }) })

// ── ESP Calibration ───────────────────────────────────────────────────────────
export const getCalibStatus = () =>
  request('/api/admin/calibration/status')

export const saveCalibration = (calibData) =>
  request('/api/admin/calibration/save', { method: 'POST', body: JSON.stringify(calibData) })

export const captureSignal = (aisleNum, position) =>
  request('/api/admin/calibration/capture', { method: 'POST', body: JSON.stringify({ aisle: aisleNum, position }) })

export const getTrackerConfig = () =>
  request('/api/admin/tracker/config')

export const updateTrackerConfig = (config) =>
  request('/api/admin/tracker/config', { method: 'POST', body: JSON.stringify(config) })
