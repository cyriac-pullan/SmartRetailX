import React from 'react'
import { motion } from 'framer-motion'
import { Minus, Plus, Trash2 } from 'lucide-react'
import { useCart } from '../../hooks/useCart'
import Badge from '../ui/Badge'

export default function CartItem({ product }) {
  const { updateQuantity, removeItem } = useCart()

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="flex items-center space-x-4 p-4 bg-white rounded-2xl border border-bg-2 hover:border-brand-200 transition-colors shadow-sm"
    >
      {/* Image Placeholder */}
      <div className="h-16 w-16 bg-gradient-to-br from-brand-100 to-indigo-50 rounded-xl flex items-center justify-center text-brand-500 overflow-hidden shrink-0">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
        ) : (
          <span className="font-bold text-xs uppercase opacity-40">ITEM</span>
        )}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-0.5">
          <h4 className="text-sm font-bold text-text-900 truncate pr-2">
            {product.name}
          </h4>
          <span className="text-sm font-bold text-brand-600 shrink-0">
            ₹{product.price}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="gray" className="py-0 px-1.5">{product.category || 'General'}</Badge>
          <span className="text-[11px] text-text-400 font-medium">#{product.barcode}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-3 bg-bg-1 p-1 rounded-xl">
        <button
          onClick={() => updateQuantity(product.barcode, -1)}
          className="p-1 hover:bg-white rounded-lg transition-colors text-text-600"
          aria-label="Decrease quantity"
        >
          <Minus size={14} />
        </button>
        <span className="text-sm font-bold text-text-900 w-4 text-center">
          {product.quantity}
        </span>
        <button
          onClick={() => updateQuantity(product.barcode, 1)}
          className="p-1 hover:bg-white rounded-lg transition-colors text-text-600"
          aria-label="Increase quantity"
        >
          <Plus size={14} />
        </button>
      </div>

      <button
        onClick={() => removeItem(product.barcode)}
        className="p-2 text-text-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
        aria-label="Remove item"
      >
        <Trash2 size={18} />
      </button>
    </motion.div>
  )
}
