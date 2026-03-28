import React from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export function Modal({ 
    open, 
    onOpenChange, 
    title, 
    children, 
    className = '',
    maxWidth = 'max-w-md'
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-text-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              >
                <Dialog.Content asChild>
                  <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 10 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 10 }}
                    className={twMerge(
                      'bg-white relative rounded-xl shadow-2xl p-6 w-full z-50 overflow-hidden',
                      maxWidth,
                      className
                    )}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <Dialog.Title className="text-lg font-bold text-text-900">
                        {title}
                      </Dialog.Title>
                      <Dialog.Close className="text-text-400 hover:text-text-600 transition-colors p-1 rounded-lg">
                        <X size={20} />
                      </Dialog.Close>
                    </div>
                    
                    <div className="max-h-[80vh] overflow-y-auto pr-2 custom-scrollbar">
                      {children}
                    </div>
                  </motion.div>
                </Dialog.Content>
              </motion.div>
            </Dialog.Overlay>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  )
}
