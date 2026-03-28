import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'
import { twMerge } from 'tailwind-merge'

const icons = {
  success: <CheckCircle className="text-green-500" size={18} />,
  error: <AlertCircle className="text-red-500" size={18} />,
  warning: <AlertTriangle className="text-amber-500" size={18} />,
  info: <Info className="text-brand-500" size={18} />,
}

const backgrounds = {
  success: 'bg-green-50 border-green-100',
  error: 'bg-red-50 border-red-100',
  warning: 'bg-amber-50 border-amber-100',
  info: 'bg-brand-50 border-brand-100',
}

export default function ToastContainer() {
  const toasts = useAppStore((state) => state.toasts)
  const dismissToast = useAppStore((state) => state.dismissToast)

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col space-y-3 w-full max-w-sm pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            layout
            initial={{ opacity: 0, x: 20, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.2 } }}
            className={twMerge(
              'pointer-events-auto flex items-center p-4 rounded-xl border shadow-lg glass',
              backgrounds[toast.type] || backgrounds.info
            )}
          >
            <div className="mr-3">{icons[toast.type] || icons.info}</div>
            <p className="text-sm font-medium text-text-900 flex-1">{toast.message}</p>
            <button
              onClick={() => dismissToast(toast.id)}
              className="ml-3 text-text-400 hover:text-text-600 transition-colors"
            >
              <X size={16} />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
