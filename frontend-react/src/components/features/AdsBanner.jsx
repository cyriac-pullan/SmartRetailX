import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShoppingCart, Tag, Zap } from 'lucide-react'
import { getAds, logAdImpression } from '../../services/api'
import { useCart } from '../../hooks/useCart'
import { useToast } from '../../hooks/useToast'
import Button from '../ui/Button'

export default function AdsBanner({ position = '' }) {
  const [ads, setAds] = useState([])
  const { addItem } = useCart()
  const { toast } = useToast()

  useEffect(() => {
    getAds(position).then(({ data }) => {
      if (data && data.length) {
        setAds(data.slice(0, 2))
        // Log impressions
        data.slice(0, 2).forEach(ad => {
          if (ad.id) logAdImpression(ad.id).catch(() => {})
        })
      }
    })
  }, [position])

  if (!ads.length) return null

  const compulsory = ads.find(a => a.is_compulsory)
  const regular = ads.find(a => !a.is_compulsory)

  return (
    <div className="space-y-3">
      {/* Section Header */}
      <div className="flex items-center gap-2">
        <Zap size={14} className="text-brand-500" />
        <span className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Special Offers</span>
      </div>

      <AnimatePresence>
        {/* Compulsory / Featured Ad */}
        {compulsory && (
          <motion.div
            key={compulsory.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-2xl border-l-4 border-red-500 bg-red-50"
            style={{ boxShadow: '0 4px 20px rgba(220,38,38,0.06)' }}
          >
            <div className="text-[10px] font-black text-red-500 uppercase tracking-wider mb-1 flex items-center gap-1">
              <Zap size={10} /> Featured Deal
            </div>
            <h4 className="font-bold text-text-900 text-sm mb-1">{compulsory.title}</h4>
            {compulsory.description && (
              <p className="text-xs text-text-400 mb-2">{compulsory.description}</p>
            )}
            {compulsory.image_url && (
              <img
                src={compulsory.image_url}
                alt={compulsory.title}
                className="w-full h-24 object-cover rounded-xl mb-2"
                onError={e => { e.target.style.display = 'none' }}
              />
            )}
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-text-400">Sponsored</span>
              {compulsory.product_barcode && (
                <button
                  onClick={async () => {
                    const { lookupBarcode } = await import('../../services/api')
                    const { data } = await lookupBarcode(compulsory.product_barcode)
                    if (data) { addItem(data); toast(`${data.name} added!`, 'success') }
                  }}
                  className="flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white text-xs font-bold rounded-lg hover:bg-red-600 transition-colors"
                >
                  <ShoppingCart size={12} /> Add to Cart
                </button>
              )}
            </div>
          </motion.div>
        )}

        {/* Location-based / Regular Ad */}
        {regular && (
          <motion.div
            key={regular.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 }}
            className="p-4 rounded-2xl border-l-4 border-brand-500 bg-brand-50"
          >
            <div className="text-[10px] font-black text-brand-500 uppercase tracking-wider mb-1 flex items-center gap-1">
              <Tag size={10} /> Top Pick For You
            </div>
            <h4 className="font-bold text-text-900 text-sm mb-1">{regular.title}</h4>
            {regular.description && (
              <p className="text-xs text-text-400 mb-2">{regular.description}</p>
            )}
            {regular.image_url && (
              <img
                src={regular.image_url}
                alt={regular.title}
                className="w-full h-24 object-cover rounded-xl mb-2"
                onError={e => { e.target.style.display = 'none' }}
              />
            )}
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-text-400">Sponsored</span>
              {regular.product_barcode && (
                <button
                  onClick={async () => {
                    const { lookupBarcode } = await import('../../services/api')
                    const { data } = await lookupBarcode(regular.product_barcode)
                    if (data) { addItem(data); toast(`${data.name} added!`, 'success') }
                  }}
                  className="flex items-center gap-1 px-3 py-1.5 bg-brand-500 text-white text-xs font-bold rounded-lg hover:bg-brand-600 transition-colors"
                >
                  <ShoppingCart size={12} /> Add to Cart
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
