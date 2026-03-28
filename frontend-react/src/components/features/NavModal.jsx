import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Modal } from '../ui/Modal'
import { MapPin, Navigation } from 'lucide-react'
import { locateProduct } from '../../services/api'
import Badge from '../ui/Badge'
import Skeleton from '../ui/Skeleton'

export default function NavModal({ open, onOpenChange, productName }) {
  const [loading, setLoading] = useState(false)
  const [locationData, setLocationData] = useState(null)

  useEffect(() => {
    if (open && productName) {
      handleLocate()
    }
  }, [open, productName])

  const handleLocate = async () => {
    setLoading(true)
    const { data, error } = await locateProduct(productName)
    if (data) setLocationData(data)
    setLoading(false)
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Product Finder" maxWidth="max-w-2xl">
      <div className="space-y-6">
        <div className="flex items-center justify-between bg-bg-1 p-4 rounded-xl border border-bg-2">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-white rounded-lg border border-bg-2 shadow-sm">
                    <MapPin size={20} className="text-brand-500" />
                </div>
                <div>
                    <p className="text-xs font-bold text-text-400 uppercase tracking-widest">Searching For</p>
                    <p className="font-extrabold text-text-900">{productName}</p>
                </div>
            </div>
            
            {locationData && (
                <div className="text-right">
                    <p className="text-xs font-bold text-text-400 uppercase tracking-widest">Aisle Location</p>
                    <Badge variant="indigo" className="text-sm px-3 py-1 mt-1">{locationData.aisle || 'N/A'}</Badge>
                </div>
            )}
        </div>

        {/* Map Visualization */}
        <div className="aspect-video bg-white rounded-2xl border-2 border-bg-2 p-8 relative overflow-hidden group">
            {loading ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center space-y-4">
                    <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-500" />
                    <p className="text-sm font-medium text-text-400">Mapping store route...</p>
                </div>
            ) : locationData ? (
                <div className="h-full w-full relative">
                    {/* Simulated SVG Map */}
                    <svg viewBox="0 0 400 200" className="w-full h-full text-bg-2">
                        <rect x="10" y="10" width="380" height="180" fill="none" stroke="currentColor" strokeWidth="2" rx="4" />
                        <rect x="30" y="30" width="60" height="140" fill="currentColor" opacity="0.1" rx="2" />
                        <rect x="110" y="30" width="60" height="140" fill="currentColor" opacity="0.1" rx="2" />
                        <rect x="190" y="30" width="60" height="140" fill="currentColor" opacity="0.1" rx="2" />
                        <rect x="270" y="30" width="60" height="140" fill="currentColor" opacity="0.1" rx="2" />
                        
                        {/* Highlights */}
                        <motion.path 
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                            d="M 20 180 L 140 180 L 140 100" 
                            fill="none" 
                            stroke="var(--brand-500)" 
                            strokeWidth="3" 
                            strokeLinecap="round"
                        />
                        <circle cx="140" cy="100" r="5" fill="var(--brand-500)">
                            <animate attributeName="r" values="5;8;5" dur="1s" repeatCount="indefinite" />
                        </circle>
                    </svg>
                    
                    <div className="absolute top-4 right-4 flex items-center space-x-2 bg-brand-500 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg shadow-brand-500/20">
                        <Navigation size={14} className="animate-pulse" />
                        <span>Aisle {locationData.aisle}</span>
                    </div>
                </div>
            ) : (
                <div className="absolute inset-0 flex items-center justify-center text-text-400">
                    Enter a product name to see its location.
                </div>
            )}
        </div>

        <div className="flex gap-3">
            <div className="flex-1 p-3 bg-white border border-bg-2 rounded-xl text-center">
                <p className="text-[10px] font-bold text-text-400 uppercase mb-1">Estimated Distance</p>
                <p className="font-extrabold text-text-900">12 Meters</p>
            </div>
            <div className="flex-1 p-3 bg-white border border-bg-2 rounded-xl text-center">
                <p className="text-[10px] font-bold text-text-400 uppercase mb-1">Time to Reach</p>
                <p className="font-extrabold text-text-900">45 Seconds</p>
            </div>
        </div>
      </div>
    </Modal>
  )
}
