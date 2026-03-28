import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { twMerge } from 'tailwind-merge'
import Card from '../ui/Card'

export default function MetricCard({ 
    label, 
    value, 
    icon: Icon, 
    trend, 
    trendUp,
    className = ''
}) {
  return (
    <Card hoverable className={twMerge('p-5 flex flex-col justify-between h-full', className)}>
      <div className="flex items-start justify-between">
        <div className="p-2.5 bg-brand-50 rounded-xl text-brand-500">
          {Icon && <Icon size={22} />}
        </div>
        
        {trend && (
          <div className={twMerge(
            'flex items-center space-x-1 px-2 py-1 rounded-lg text-xs font-bold',
            trendUp ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
          )}>
            {trendUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>{trend}</span>
          </div>
        )}
      </div>

      <div className="mt-4">
        <p className="text-sm font-medium text-text-600 mb-1">{label}</p>
        <motion.h3 
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="text-2xl font-extrabold text-text-900"
        >
          {value}
        </motion.h3>
      </div>
    </Card>
  )
}
