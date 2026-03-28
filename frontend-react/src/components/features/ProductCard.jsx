import React from 'react'
import { motion } from 'framer-motion'
import { Plus, ShoppingCart } from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { twMerge } from 'tailwind-merge'

export default function ProductCard({ product, onAddToCart, className = '' }) {
  return (
    <Card 
        hoverable 
        className={twMerge('group p-0 overflow-hidden w-full max-w-[280px] flex flex-col h-full bg-white', className)}
    >
      {/* Image Area */}
      <div className="h-40 bg-gradient-to-br from-bg-1 to-bg-2 relative flex items-center justify-center">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
        ) : (
          <ShoppingCart size={40} className="text-bg-2 opacity-50" />
        )}
        
        <div className="absolute top-3 left-3">
          <Badge variant="indigo">{product.category}</Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col">
        <h4 className="font-bold text-text-900 mb-1 group-hover:text-brand-500 transition-colors line-clamp-1">
          {product.name}
        </h4>
        <div className="mt-auto pt-3 flex items-center justify-between">
          <div className="flex flex-col">
             <span className="text-[10px] text-text-400 font-bold uppercase tracking-wider">Price</span>
             <span className="text-lg font-extrabold text-text-900">₹{product.price}</span>
          </div>
          
          <Button
            variant="primary"
            size="sm"
            className="w-10 h-10 p-0 rounded-xl shadow-lg shadow-brand-500/10"
            onClick={() => onAddToCart(product)}
          >
            <Plus size={20} />
          </Button>
        </div>
      </div>
    </Card>
  )
}
