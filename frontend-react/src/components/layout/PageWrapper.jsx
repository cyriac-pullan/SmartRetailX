import React from 'react'
import { twMerge } from 'tailwind-merge'

export function PageWrapper({ children, className = '' }) {
  return (
    <main className={twMerge('max-w-[1440px] mx-auto px-6 pt-24 pb-12 min-h-screen', className)}>
      {children}
    </main>
  )
}

export function PageHeader({ title, subtitle, children, className = '' }) {
  return (
    <div className={twMerge('mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4', className)}>
      <div className="space-y-1">
        <h1 className="text-3xl md:text-4xl font-extrabold text-text-900 tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-text-600 text-sm md:text-base font-medium">
            {subtitle}
          </p>
        )}
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  )
}
