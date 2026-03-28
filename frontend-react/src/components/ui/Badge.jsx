import React from 'react'
import { twMerge } from 'tailwind-merge'

const variants = {
  indigo: 'bg-brand-50 text-brand-600',
  amber: 'bg-accent-50 text-accent-700',
  green: 'bg-green-50 text-green-700',
  red: 'bg-red-50 text-red-700',
  gray: 'bg-bg-2 text-text-600',
}

export default function Badge({ variant = 'indigo', children, className = '' }) {
  return (
    <span className={twMerge(
      'px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider inline-flex items-center',
      variants[variant],
      className
    )}>
      {children}
    </span>
  )
}
