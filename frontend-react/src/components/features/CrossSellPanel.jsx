import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ProductCard from './ProductCard'
import Skeleton from '../ui/Skeleton'
import { Sparkles } from 'lucide-react'

export default function CrossSellPanel({ recommendations = [], loading = false, onAddToCart }) {
  if (!loading && recommendations.length === 0) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 px-1">
        <Sparkles size={18} className="text-amber-500" />
        <h3 className="text-base font-extrabold text-text-900 tracking-tight">
          Frequently Bought Together
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-4 overflow-y-auto pr-2 max-h-[500px] custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {loading ? (
             Array.from({ length: 3 }).map((_, i) => (
               <Skeleton key={i} variant="card" className="h-48" />
             ))
          ) : (
            recommendations.map((product) => (
              <motion.div
                key={product.barcode}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                <ProductCard 
                    product={product} 
                    onAddToCart={onAddToCart} 
                    className="max-w-full" 
                />
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
