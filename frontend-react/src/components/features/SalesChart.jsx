import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend
)

export default function SalesChart({ data = [], loading = false }) {
  const chartData = {
    labels: data.map(d => d.date),
    datasets: [
      {
        fill: true,
        label: 'Daily Revenue',
        data: data.map(d => d.revenue),
        borderColor: '#6366F1',
        backgroundColor: (context) => {
            const chart = context.chart;
            const {ctx, chartArea} = chart;
            if (!chartArea) return null;
            const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
            gradient.addColorStop(0, 'rgba(99, 102, 241, 0)');
            gradient.addColorStop(1, 'rgba(99, 102, 241, 0.15)');
            return gradient;
        },
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        borderWidth: 3,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#0F172A',
        padding: 12,
        titleFont: { size: 12, weight: 'bold' },
        bodyFont: { size: 14 },
        displayColors: false,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#64748B', font: { size: 10 } }
      },
      y: {
        grid: { color: '#F1F5F9' },
        ticks: { 
            color: '#64748B', 
            font: { size: 10 },
            callback: (value) => '₹' + value
        }
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  }

  if (loading) return (
    <div className="w-full h-[300px] flex items-center justify-center bg-bg-1 rounded-2xl animate-pulse">
        <p className="text-sm font-medium text-text-400">Loading Analytics...</p>
    </div>
  )

  return (
    <div className="h-[300px] w-full">
      <Line options={options} data={chartData} />
    </div>
  )
}
