import React from 'react'
import { twMerge } from 'tailwind-merge'

export default function Skeleton({ variant = 'line', className = '' }) {
  const base = 'animate-shimmer rounded bg-bg-1'
  
  const variants = {
    line: 'h-4 w-full',
    avatar: 'h-12 w-12 rounded-full',
    card: 'h-64 w-full rounded-xl',
    'table-row': 'h-12 w-full',
    title: 'h-8 w-1/3',
  }

  return (
    <div className={twMerge(base, variants[variant], className)} />
  )
}
