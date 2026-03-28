import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShoppingCart, Sparkles } from 'lucide-react'
import { getMarketBasket } from '../../services/api'
import { useCart } from '../../hooks/useCart'
import { useToast } from '../../hooks/useToast'

export default function MarketBasketPanel({ lastAddedBarcode }) {
  const [suggestions, setSuggestions] = useState([])
  const { addItem } = useCart()
  const { toast } = useToast()

  useEffect(() => {
    if (!lastAddedBarcode) return
    setSuggestions([])
    getMarketBasket(lastAddedBarcode, 4).then(({ data }) => {
      if (data?.recommendations?.length) {
        setSuggestions(data.recommendations)
      }
    })
  }, [lastAddedBarcode])

  if (!suggestions.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mt-3 p-4 rounded-2xl border border-dashed border-brand-300 bg-brand-50/50"
    >
      <div className="flex items-center gap-2 mb-3">
        <Sparkles size={14} className="text-brand-500" />
        <span className="text-xs font-black text-brand-700 uppercase tracking-wider">Usually Bought Together</span>
      </div>
      <div className="space-y-2">
        {suggestions.map((item) => (
          <motion.div
            key={item.barcode || item.name}
            layout
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center justify-between bg-white rounded-xl p-2.5 border border-bg-2 shadow-sm"
          >
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-text-900 truncate">{item.name}</p>
              <p className="text-[10px] text-text-400">₹{item.price}</p>
            </div>
            <button
              onClick={() => { addItem(item); toast(`${item.name} added!`, 'success') }}
              className="ml-2 shrink-0 p-1.5 bg-brand-50 text-brand-600 rounded-lg hover:bg-brand-100 transition-colors border border-brand-200"
            >
              <ShoppingCart size={14} />
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
