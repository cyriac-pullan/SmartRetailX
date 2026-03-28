import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, ChevronDown, ChevronUp, ShoppingBag, Leaf, DollarSign } from 'lucide-react'
import { getCartScore } from '../../services/api'

// SVG Arc Score Ring
function ScoreRing({ score }) {
  const r = 28
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const color = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="relative w-16 h-16 flex items-center justify-center">
      <svg width="64" height="64" viewBox="0 0 64 64" className="-rotate-90">
        <circle cx="32" cy="32" r={r} fill="none" stroke="#e2e8f0" strokeWidth="5" />
        <motion.circle
          cx="32" cy="32" r={r}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: [0.4, 0, 0.2, 1] }}
          strokeLinecap="round"
        />
      </svg>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="absolute text-lg font-black"
        style={{ color }}
      >
        {score}
      </motion.span>
    </div>
  )
}

export default function AiCartPanel({ cartItems = [] }) {
  const [open, setOpen] = useState(true)
  const [scoreData, setScoreData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (cartItems.length < 2) { setScoreData(null); return }
    setLoading(true)
    const timer = setTimeout(() => {
      getCartScore(cartItems).then(({ data }) => {
        if (data) setScoreData(data)
        setLoading(false)
      })
    }, 600)
    return () => clearTimeout(timer)
  }, [cartItems.length])

  if (cartItems.length < 2) return null

  const score = scoreData?.score ?? 0
  const label = score >= 70 ? 'Excellent Cart' : score >= 40 ? 'Good Cart' : 'Improve Your Cart'
  const tip = scoreData?.tip ?? 'Add more varied items to get insights'

  const breakdown = scoreData?.breakdown || [
    { label: 'Variety', value: Math.min(100, cartItems.length * 20), icon: ShoppingBag },
    { label: 'Nutrition', value: scoreData?.nutrition ?? 65, icon: Leaf },
    { label: 'Value', value: scoreData?.value ?? 80, icon: DollarSign },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-brand-200 bg-gradient-to-br from-brand-50 to-indigo-50 p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-brand-500" />
          <span className="text-xs font-black text-brand-700 uppercase tracking-wider">AI Cart Intelligence</span>
        </div>
        <button onClick={() => setOpen(o => !o)} className="text-text-400 hover:text-text-600 transition-colors">
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {loading ? (
              <div className="flex items-center gap-3 py-2">
                <div className="w-16 h-16 rounded-full border-4 border-brand-200 border-t-brand-500 animate-spin" />
                <div>
                  <p className="text-sm font-bold text-text-900">Analysing…</p>
                  <p className="text-xs text-text-400">Add 2+ items to get insights</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-4">
                  <ScoreRing score={score} />
                  <div>
                    <p className="font-bold text-text-900 text-sm">{label}</p>
                    <p className="text-xs text-text-400">{tip}</p>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-brand-100">
                  {breakdown.map(({ label, value, icon: Icon }) => (
                    <div key={label} className="flex items-center gap-2">
                      <Icon size={12} className="text-text-400 shrink-0" />
                      <span className="text-xs text-text-600 w-16">{label}</span>
                      <div className="flex-1 h-1.5 bg-brand-100 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${value}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                          className="h-full bg-brand-500 rounded-full"
                        />
                      </div>
                      <span className="text-xs font-bold text-text-900 w-8 text-right">{value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
