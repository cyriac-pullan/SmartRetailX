import React, { useRef, useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Scan, Loader2 } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export default function BarcodeInput({ onScan, loading = false, error = false, success = false }) {
  const inputRef = useRef(null)
  const [isRemoveMode, setIsRemoveMode] = useState(false)

  useEffect(() => {
    // Keep focus on the scanner input as much as possible for retail UX
    const handleGlobalClick = (e) => {
      // Don't steal focus if clicking a button, input, textarea, or select element
      if (!e.target.closest('button, input, textarea, select')) {
        inputRef.current?.focus()
      }
    }
    window.addEventListener('click', handleGlobalClick)
    return () => window.removeEventListener('click', handleGlobalClick)
  }, [])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      const barcode = e.target.value.trim()
      if (barcode) {
        onScan(barcode, isRemoveMode)
        e.target.value = ''
      }
    }
  }

  return (
    <div className="w-full relative group flex gap-3">
      <div className="relative flex-1">
        <div className={twMerge(
          'absolute inset-y-0 left-5 flex items-center transition-colors',
          loading ? 'text-brand-500' : 'text-text-400 group-focus-within:text-brand-500'
        )}>
          {loading ? <Loader2 size={24} className="animate-spin" /> : <Scan size={24} />}
        </div>

        <input
          ref={inputRef}
          autoFocus
          type="text"
          onKeyDown={handleKeyDown}
          placeholder={isRemoveMode ? "Scan to remove item..." : "Scan barcode or type ID..."}
          className={twMerge(
            'w-full bg-white border-2 border-bg-2 rounded-2xl pl-14 pr-6 py-5 text-xl font-bold text-text-900',
            'placeholder:text-text-400 focus:outline-none focus:ring-8 transition-all outline-none',
            isRemoveMode ? 'focus:ring-red-500/10 focus:border-red-200' : 'focus:ring-brand-500/10 focus:border-brand-300',
            success && 'border-green-500 animate-pulse',
            error && 'border-red-500'
          )}
        />

        <motion.div 
          animate={loading ? { opacity: [0.2, 0.5, 0.2] } : { opacity: 0 }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className={twMerge("absolute inset-0 pointer-events-none rounded-2xl", isRemoveMode ? "bg-red-500/5" : "bg-brand-500/5")}
        />
        
        {/* Visual Scan line effect */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ top: '10%' }}
              animate={{ top: '90%' }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse', ease: "linear" }}
              className={twMerge(
                "absolute left-6 right-6 h-0.5 z-10 pointer-events-none shadow-[0_0_15px_rgba(99,102,241,0.5)]",
                isRemoveMode ? "bg-red-500 shadow-red-500/50" : "bg-brand-500"
              )}
            />
          )}
        </AnimatePresence>
      </div>

      <button
        onClick={() => setIsRemoveMode(!isRemoveMode)}
        className={twMerge(
          "shrink-0 px-6 rounded-2xl font-bold transition-colors border-2 flex items-center gap-2",
          isRemoveMode 
            ? "bg-red-50 border-red-200 text-red-600 hover:bg-red-100" 
            : "bg-white border-bg-2 text-text-500 hover:bg-bg-1"
        )}
      >
        <span className="text-xl leading-none mb-1">-</span> Remove
      </button>
    </div>
  )
}
