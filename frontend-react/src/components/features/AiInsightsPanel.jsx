import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, PackageOpen, AlertTriangle, TrendingUp, RefreshCw, CheckCircle2 } from 'lucide-react'
import { getInventory, getProductPerformance } from '../../services/api'

export default function AiInsightsPanel() {
  const [loading, setLoading] = useState(true)
  const [insights, setInsights] = useState([])

  const generateInsights = async () => {
    setLoading(true)
    try {
      const [{ data: invData }, { data: perfData }] = await Promise.all([
        getInventory(), getProductPerformance(20)
      ])
      
      const newInsights = []
      const inventory = invData || []
      const perf = perfData?.best_sellers || []

      // 1. Slow movers
      const soldBarcodes = new Set(perf.map(p => p.barcode))
      const slowMovers = inventory.filter(p => !soldBarcodes.has(p.barcode) && p.stock_quantity > 50)
      if (slowMovers.length) {
        newInsights.push({
          id: 'slow-movers',
          type: 'warning',
          icon: PackageOpen,
          title: `${slowMovers.length} Slow-Moving Products Detected`,
          desc: `${slowMovers.slice(0,3).map(p=>p.name).join(', ')}${slowMovers.length > 3 ? '…' : ''} — consider promotions.`,
          color: 'text-amber-500',
          bg: 'bg-amber-50',
          border: 'border-amber-200'
        })
      }

      // 2. Critical stock
      const critical = inventory.filter(p => p.status === 'reorder_needed')
      if (critical.length) {
        newInsights.push({
          id: 'critical',
          type: 'error',
          icon: AlertTriangle,
          title: `${critical.length} Items at Critical Stock`,
          desc: `${critical.slice(0,3).map(p=>p.name).join(', ')} — reorder now to avoid stockouts.`,
          color: 'text-red-500',
          bg: 'bg-red-50',
          border: 'border-red-200'
        })
      } else {
        newInsights.push({
          id: 'stock-ok',
          type: 'success',
          icon: CheckCircle2,
          title: 'No Critical Stock Issues',
          desc: 'All monitored products are above their reorder threshold.',
          color: 'text-emerald-500',
          bg: 'bg-emerald-50',
          border: 'border-emerald-200'
        })
      }

      // 3. Top Performer
      if (perf[0]) {
        newInsights.push({
          id: 'top-perf',
          type: 'info',
          icon: TrendingUp,
          title: `Best Seller: ${perf[0].name}`,
          desc: `₹${(perf[0].revenue||0).toLocaleString()} revenue · ${perf[0].total_sold||0} sold. Consider featuring.`,
          color: 'text-brand-500',
          bg: 'bg-brand-50',
          border: 'border-brand-200'
        })
      }

      setInsights(newInsights)
    } catch (e) {
      setInsights([{ id: 'err', type: 'error', title: 'Could not load insights', desc: 'Connectivity issue', icon: AlertTriangle, color: 'text-slate-500', bg: 'bg-slate-50', border: 'border-slate-200' }])
    }
    setLoading(false)
  }

  useEffect(() => { generateInsights() }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
         <div>
             <h3 className="text-lg font-extrabold text-text-900 flex items-center gap-2 tracking-tight">
                <Brain size={20} className="text-brand-500" />
                AI Store Insights
             </h3>
             <p className="text-xs text-text-400 font-medium">Auto-detected anomalies and recommendations</p>
         </div>
         <button onClick={generateInsights} disabled={loading} className="p-2 text-text-400 hover:bg-bg-1 hover:text-brand-500 rounded-xl transition-colors disabled:opacity-50">
             <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
         </button>
      </div>

      <div className="space-y-3">
        {loading && !insights.length ? (
          <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50 animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-1/2 mb-2" />
            <div className="h-3 bg-slate-200 rounded w-3/4" />
          </div>
        ) : (
          insights.map((ins, i) => {
            const Icon = ins.icon
            return (
              <motion.div 
                key={ins.id}
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                className={`p-4 rounded-2xl border ${ins.border} ${ins.bg} flex gap-4 items-start`}
              >
                <div className={`p-2 rounded-xl bg-white shadow-sm ${ins.color}`}>
                  <Icon size={20} />
                </div>
                <div>
                  <h4 className="font-bold text-text-900 text-sm mb-0.5">{ins.title}</h4>
                  <p className="text-xs text-text-600 leading-relaxed">{ins.desc}</p>
                </div>
              </motion.div>
            )
          })
        )}
      </div>
    </div>
  )
}
