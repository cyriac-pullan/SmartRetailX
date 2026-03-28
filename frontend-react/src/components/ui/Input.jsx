import React, { useState } from 'react'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export default function Input({
  label,
  icon: Icon,
  variant = 'default',
  error,
  type = 'text',
  placeholder,
  value,
  onChange,
  className = '',
  id,
  ...props
}) {
  const [focused, setFocused] = useState(false)
  
  const isError = variant === 'error' || !!error
  const isActive = focused || (value && value.toString().length > 0)

  return (
    <div className={twMerge('flex flex-col space-y-1.5 w-full group', className)}>
      <div className="relative">
        {/* Label (Floating Pattern) */}
        {label && (
          <label
            htmlFor={id}
            className={clsx(
                'absolute pointer-events-none transition-all duration-200 left-3',
                isActive 
                    ? '-top-2.5 text-xs bg-white px-1 font-medium text-brand-600' 
                    : 'top-1/2 -translate-y-1/2 text-sm text-text-400',
                focused && !isError && 'text-brand-600',
                isError && 'text-red-500'
            )}
          >
            {label}
          </label>
        )}

        {/* Icon */}
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-400 group-focus-within:text-brand-500 transition-colors">
            <Icon size={18} />
          </div>
        )}

        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={twMerge(
            'w-full bg-white border border-bg-2 rounded-r-md px-4 py-3 text-sm text-text-900 transition-all duration-200',
            'focus:outline-none focus:ring-4 focus:ring-brand-500/10 focus:border-brand-500',
            Icon && 'pl-10',
            isError && 'border-red-500 focus:ring-red-500/10 focus:border-red-500',
            className
          )}
          placeholder={focused ? placeholder : ''}
          {...props}
        />
      </div>
      
      {error && (
        <span className="text-[11px] font-medium text-red-500 px-1 animate-in fade-in slide-in-from-top-1">
          {error}
        </span>
      )}
    </div>
  )
}
