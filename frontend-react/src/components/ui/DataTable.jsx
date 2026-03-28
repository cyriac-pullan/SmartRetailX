import React, { useState, memo } from 'react'
import Skeleton from './Skeleton'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

function DataTable({ 
    columns = [], 
    data = [], 
    loading = false, 
    onRowClick,
    className = ''
}) {
  const [sortConfig, setSortConfig] = useState(null)

  const handleSort = (key) => {
    let direction = 'ascending'
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending'
    }
    setSortConfig({ key, direction })
  }

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig) return 0
    const { key, direction } = sortConfig
    if (a[key] < b[key]) return direction === 'ascending' ? -1 : 1
    if (a[key] > b[key]) return direction === 'ascending' ? 1 : -1
    return 0
  })

  return (
    <div className={twMerge('overflow-hidden rounded-xl border border-bg-2 bg-white', className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-bg-1 text-text-600 font-semibold border-b border-bg-2">
            <tr>
              {columns.map((col) => (
                <th 
                  key={col.key} 
                  className={twMerge(
                    "px-6 py-4",
                    col.sortable && "cursor-pointer hover:text-brand-500 transition-colors"
                  )}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{col.label}</span>
                    {col.sortable && sortConfig?.key === col.key && (
                      <span className="text-brand-500">
                        {sortConfig.direction === 'ascending' ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-bg-2">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {columns.map((_, j) => (
                    <td key={j} className="px-6 py-4">
                      <Skeleton variant="line" className="h-4" />
                    </td>
                  ))}
                </tr>
              ))
            ) : sortedData.length > 0 ? (
              sortedData.map((row, i) => (
                <tr 
                  key={i} 
                  className={twMerge(
                    "hover:bg-brand-50/30 transition-colors",
                    onRowClick && "cursor-pointer"
                  )}
                  onClick={() => onRowClick && onRowClick(row)}
                >
                  {columns.map((col) => (
                    <td key={col.key} className="px-6 py-4 text-text-900">
                      {row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center text-text-400">
                  No data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default memo(DataTable)
