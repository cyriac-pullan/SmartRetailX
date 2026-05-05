import React, { useState, useEffect, Component } from 'react'
import { Package, Search, Filter, Edit, RefreshCw, AlertTriangle, TrendingDown, CheckCircle } from 'lucide-react'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'

const API = 'http://127.0.0.1:5000'

// Error boundary
class Safe extends Component {
  state = { err: null }
  static getDerivedStateFromError(e) { return { err: e } }
  render() {
    if (this.state.err) return <div className="p-4 text-red-600 text-sm">Error: {this.state.err.message}</div>
    return this.props.children
  }
}

function StatusDot({ qty, reorder }) {
  const level = qty <= (reorder || 5) ? 'critical' : qty <= (reorder || 5) * 2 ? 'low' : 'ok'
  const cls = { critical: 'bg-red-500', low: 'bg-amber-500', ok: 'bg-emerald-500' }[level]
  return <span className={`inline-block w-2 h-2 rounded-full ${cls} mr-2`} />
}

export default function InventoryPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all') // all | low | critical
  const [page, setPage] = useState(0)
  const PAGE_SIZE = 30

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/api/inventory/all`, { headers: { 'Content-Type': 'application/json' } })
      const data = await res.json()
      // Handle both plain array and {inventory:[]} responses
      const arr = Array.isArray(data) ? data : (data?.inventory || data?.items || [])
      setItems(arr)
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  const filtered = items.filter(i => {
    const matchSearch = !search ||
      (i.name || '').toLowerCase().includes(search.toLowerCase()) ||
      String(i.barcode || '').includes(search)
    const stock = i.stock_quantity ?? i.stock ?? 0
    const reorder = i.reorder_level ?? i.reorder ?? 5
    const matchFilter =
      filter === 'all' ? true :
      filter === 'low' ? stock <= reorder * 2 :
      filter === 'critical' ? stock <= reorder : true
    return matchSearch && matchFilter
  })

  const paged = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)

  const stats = {
    total: items.length,
    critical: items.filter(i => (i.stock_quantity ?? i.stock ?? 0) <= (i.reorder_level ?? 5)).length,
    low: items.filter(i => { const s = i.stock_quantity ?? i.stock ?? 0; const r = i.reorder_level ?? 5; return s > r && s <= r*2 }).length,
  }

  return (
    <div className="bg-bg-0 min-h-screen">
      <Header />
      <PageWrapper>
        <PageHeader title="Inventory." subtitle="Manage and track your store stock levels">
          <button onClick={load} className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </PageHeader>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Total Products', value: stats.total, icon: Package, color: 'indigo' },
            { label: 'Low Stock', value: stats.low, icon: TrendingDown, color: 'amber' },
            { label: 'Critical / Out', value: stats.critical, icon: AlertTriangle, color: 'red' },
          ].map(({ label, value, icon: Icon, color }) => (
            <Card key={label} className="p-5 flex items-center gap-4">
              <div className={`p-3 rounded-xl bg-${color}-50 text-${color}-600`}><Icon size={20}/></div>
              <div>
                <p className="text-2xl font-extrabold text-slate-900">{loading ? '…' : value}</p>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Search + Filter */}
        <Card className="p-4 mb-4 flex flex-col sm:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search by name or barcode…"
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(0) }}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div className="flex gap-2">
            {[['all','All'],['low','Low Stock'],['critical','Critical']].map(([v, label]) => (
              <button key={v} onClick={() => { setFilter(v); setPage(0) }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors ${
                  filter === v ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}>{label}</button>
            ))}
          </div>
          <p className="text-xs text-slate-400 font-bold shrink-0">{filtered.length} items</p>
        </Card>

        {/* Table */}
        {error && <div className="p-6 text-center text-red-600 font-medium">Error loading inventory: {error}</div>}
        {loading ? (
          <Card className="p-8 text-center">
            <RefreshCw size={24} className="animate-spin text-indigo-500 mx-auto mb-3" />
            <p className="text-slate-500 text-sm">Loading inventory…</p>
          </Card>
        ) : paged.length === 0 ? (
          <Card className="p-12 text-center">
            <CheckCircle size={32} className="text-emerald-400 mx-auto mb-3" />
            <p className="text-slate-500">No items match your filter.</p>
          </Card>
        ) : (
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    {['Barcode','Product Name','Category','Aisle','Position','Price','Stock','Reorder Lvl','Status'].map(h => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-extrabold text-slate-500 uppercase tracking-wider whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {paged.map((item, idx) => {
                    const stock = item.stock_quantity ?? item.stock ?? 0
                    const reorder = item.reorder_level ?? item.reorder ?? 5
                    const rowBg = stock <= reorder ? 'bg-red-50/40' : stock <= reorder * 2 ? 'bg-amber-50/40' : ''
                    return (
                      <tr key={item.barcode || idx} className={`hover:bg-slate-50 transition-colors ${rowBg}`}>
                        <td className="px-4 py-3 font-mono text-xs text-slate-500">{item.barcode}</td>
                        <td className="px-4 py-3 font-bold text-slate-800 max-w-[200px] truncate">{item.name}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-xs font-bold">{item.category}</span>
                        </td>
                        <td className="px-4 py-3 text-slate-600 text-center">{item.aisle || '—'}</td>
                        <td className="px-4 py-3 font-mono text-xs text-indigo-600">{item.position_tag || '—'}</td>
                        <td className="px-4 py-3 font-bold text-slate-700">₹{item.price}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center">
                            <StatusDot qty={stock} reorder={reorder} />
                            <span className="font-extrabold text-slate-900">{stock}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-500 text-center">{reorder}</td>
                        <td className="px-4 py-3">
                          {stock <= reorder
                            ? <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-bold">Critical</span>
                            : stock <= reorder * 2
                            ? <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full text-xs font-bold">Low</span>
                            : <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-bold">OK</span>
                          }
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-4 py-3 border-t border-slate-200 flex items-center justify-between bg-slate-50">
                <button onClick={() => setPage(p => Math.max(0, p-1))} disabled={page === 0}
                  className="px-3 py-1.5 text-xs font-bold rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-white transition-colors">← Prev</button>
                <span className="text-xs text-slate-500 font-medium">Page {page+1} of {totalPages} · {filtered.length} total</span>
                <button onClick={() => setPage(p => Math.min(totalPages-1, p+1))} disabled={page >= totalPages-1}
                  className="px-3 py-1.5 text-xs font-bold rounded-lg border border-slate-200 disabled:opacity-40 hover:bg-white transition-colors">Next →</button>
              </div>
            )}
          </Card>
        )}
      </PageWrapper>
    </div>
  )
}
