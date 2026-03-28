import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

// Safe JSON parse — guards against null, "undefined", and malformed stored values
function safeParse(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw || raw === 'undefined' || raw === 'null') return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const useAppStore = create(
  devtools((set, get) => ({
    // Authentication Slice
    user: safeParse('customer'),
    setUser: (user) => {
      localStorage.setItem('customer', JSON.stringify(user))
      set({ user })
    },
    clearUser: () => {
      localStorage.removeItem('customer')
      set({ user: null })
    },

    // Cart Slice
    cartItems: [],
    addItem: (product) => {
      const items = get().cartItems
      const existing = items.find((i) => i.barcode === product.barcode)
      if (existing) {
        set({
          cartItems: items.map((i) =>
            i.barcode === product.barcode ? { ...i, quantity: (i.quantity || 1) + 1 } : i
          ),
        })
      } else {
        set({ cartItems: [...items, { ...product, quantity: 1 }] })
      }
    },
    removeItem: (barcode) => {
      set({ cartItems: get().cartItems.filter((i) => i.barcode !== barcode) })
    },
    updateQuantity: (barcode, delta) => {
      set({
        cartItems: get().cartItems.map((i) =>
          i.barcode === barcode ? { ...i, quantity: Math.max(1, (i.quantity || 1) + delta) } : i
        ),
      })
    },
    clearCart: () => set({ cartItems: [] }),
    get cartTotal() {
      return get().cartItems.reduce((acc, item) => acc + (item.price || 0) * (item.quantity || 1), 0)
    },

    // UI Slice
    toasts: [],
    pushToast: (toast) => {
      const id = Math.random().toString(36).substr(2, 9)
      set({ toasts: [...get().toasts, { ...toast, id }] })
      setTimeout(() => get().dismissToast(id), toast.duration || 4000)
    },
    dismissToast: (id) => {
      set({ toasts: get().toasts.filter((t) => t.id !== id) })
    },
    navModalOpen: false,
    setNavModalOpen: (open) => set({ navModalOpen: open }),
  }))
)
