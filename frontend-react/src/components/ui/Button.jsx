import React, { memo } from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const variants = {
  primary: 'bg-brand-500 text-white hover:bg-brand-600 shadow-sm',
  secondary: 'bg-brand-50 text-brand-600 hover:bg-brand-100',
  ghost: 'bg-transparent text-text-600 hover:bg-bg-1',
  danger: 'bg-red-500 text-white hover:bg-red-600',
  outline: 'bg-transparent border border-bg-2 text-text-900 hover:bg-white',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-8 py-4 text-base font-semibold',
}

function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  onClick,
  children,
  type = 'button',
  className = '',
  ...props
}) {
  return (
    <motion.button
      whileTap={!disabled && !loading ? { scale: 0.97 } : {}}
      whileHover={!disabled && !loading ? { scale: 1.02, translateY: -1 } : {}}
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={twMerge(
        'relative flex items-center justify-center rounded-r-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {loading ? (
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="opacity-80">Processing...</span>
        </div>
      ) : (
        children
      )}
    </motion.button>
  )
}

export default memo(Button)
