import { useMemo } from 'react'
import { useAppStore } from '../store/useAppStore'

export const useCart = () => {
    const cartItems = useAppStore((state) => state.cartItems)
    const addItem = useAppStore((state) => state.addItem)
    const removeItem = useAppStore((state) => state.removeItem)
    const updateQuantity = useAppStore((state) => state.updateQuantity)
    const clearCart = useAppStore((state) => state.clearCart)

    const cartTotal = useMemo(() => {
        return cartItems.reduce((acc, item) => acc + (item.price || 0) * (item.quantity || 1), 0)
    }, [cartItems])

    return {
        cartItems,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
        cartTotal
    }
}
