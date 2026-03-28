import React from 'react'
import { motion } from 'framer-motion'
import { twMerge } from 'tailwind-merge'

export default function Card({
  children,
  hoverable = false,
  elevated = false,
  gradient = false,
  className = '',
  ...props
}) {
  return (
    <motion.div
      whileHover={hoverable ? { translateY: -4, boxShadow: 'var(--shadow-float)' } : {}}
      className={twMerge(
        'bg-white rounded-3xl p-6 overflow-hidden border border-bg-1/60',
        elevated ? 'shadow-card' : 'shadow-sm',
        gradient && 'border-gradient-brand', // Requires custom CSS or util
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}
