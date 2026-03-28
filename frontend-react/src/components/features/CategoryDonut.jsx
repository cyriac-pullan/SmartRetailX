import React, { useEffect, useState } from 'react'
import { Doughnut } from 'react-chartjs-2'
import { getCategoryBreakdown } from '../../services/api'
import { Loader2 } from 'lucide-react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function CategoryDonut() {
  const [chartData, setChartData] = useState(null)
  
  useEffect(() => {
    getCategoryBreakdown().then(({ data }) => {
      if (!data || !data.length) return
      
      const labels = data.slice(0, 8).map(d => d.category)
      const values = data.slice(0, 8).map(d => d.revenue || d.purchases)
      const palette = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6', '#14b8a6']

      setChartData({
        labels,
        datasets: [{
          data: values,
          backgroundColor: palette,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 8
        }]
      })
    })
  }, [])

  if (!chartData) {
    return (
      <div className="h-[260px] flex items-center justify-center bg-bg-1 rounded-2xl mt-4">
        <Loader2 className="animate-spin text-text-300" />
      </div>
    )
  }

  return (
    <div className="h-[260px] mt-4 relative">
      <Doughnut 
        data={chartData} 
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              position: 'right', 
              labels: { 
                color: '#64748b', 
                font: { size: 11, family: 'Inter' }, 
                padding: 12,
                usePointStyle: true,
                pointStyle: 'circle'
              } 
            },
            tooltip: {
              boxPadding: 6,
              padding: 12,
              backgroundColor: '#0f172a',
              titleFont: { size: 13, family: 'Inter' },
              bodyFont: { size: 13, family: 'Inter', weight: 'bold' },
              callbacks: {
                label: (ctx) => `  ₹${ctx.raw.toLocaleString('en-IN')}`
              }
            }
          },
          cutout: '70%'
        }} 
      />
    </div>
  )
}
