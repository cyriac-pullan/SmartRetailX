import React, { useEffect, useState } from 'react'
import { getAisleHeatmap } from '../../services/api'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export default function AisleHeatmap() {
  const [data, setData] = useState(null)

  useEffect(() => {
    getAisleHeatmap().then(({ data }) => setData(data || []))
  }, [])

  if (!data) {
    return (
      <div className="h-[260px] flex items-center justify-center bg-bg-1 rounded-2xl mt-4">
        <Loader2 className="animate-spin text-text-300" />
      </div>
    )
  }

  if (data.length === 0) {
    return <div className="p-6 text-center text-text-400 mt-4 bg-bg-1 rounded-2xl">No heatmap data yet</div>
  }

  const maxD = Math.max(...data.map(d => d.density), 1)
  const COLOURS = ['#1e293b', '#1e3a5f', '#154e7a', '#0e6080', '#0d7a92', '#0b9290', '#07a28a', '#10b981']

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 h-[260px]">
      {data.map((d, i) => {
        const bucket = Math.min(Math.floor((d.density / maxD) * (COLOURS.length - 1)), COLOURS.length - 1)
        const bg = COLOURS[bucket]
        const textCol = d.density > 50 ? '#ffffff' : '#94a3b8'

        return (
          <motion.div
            key={d.aisle}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-2xl p-4 flex flex-col justify-between"
            style={{ backgroundColor: bg, color: textCol }}
          >
            <div className="text-xs font-bold opacity-80 uppercase tracking-widest">Aisle {d.aisle}</div>
            <div>
              <div className="text-3xl font-black mb-1">{d.density}%</div>
              <div className="text-[10px] opacity-70 font-semibold uppercase">{d.hits} purchases</div>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
