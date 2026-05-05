import React, { useState, useEffect } from 'react'
import { RefreshCw, Package, AlertTriangle, Plus, Minus, Search, CheckCircle } from 'lucide-react'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import { useToast } from '../hooks/useToast'

const API = 'http://127.0.0.1:5000'

export default function RestockPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [updates, setUpdates] = useState({})  // { barcode: qty_to_add }
  const [saving, setSaving] = useState({})
  const [showAll, setShowAll] = useState(true)
  const { toast } = useToast()

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/api/inventory/all`)
      const data = await res.json()
      const arr = Array.isArray(data) ? data : (data?.inventory || [])
      // Sort: critical first, then low, then OK
      arr.sort((a, b) => {
        const sa = a.stock_quantity ?? a.stock ?? 0
        const sb = b.stock_quantity ?? b.stock ?? 0
        const ra = a.reorder_level ?? 5
        const rb = b.reorder_level ?? 5
        const scoreA = sa <= ra ? 0 : sa <= ra*2 ? 1 : 2
        const scoreB = sb <= rb ? 0 : sb <= rb*2 ? 1 : 2
        return scoreA - scoreB || sa - sb
      })
      setItems(arr)
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  const setQty = (barcode, val) =>
    setUpdates(p => ({ ...p, [barcode]: Math.max(0, val) }))

  const handleRestock = async (item) => {
    const qty = updates[item.barcode] || 0
    if (qty <= 0) { toast('Set a quantity first', 'error'); return }
    setSaving(p => ({ ...p, [item.barcode]: true }))
    try {
      const current = item.stock_quantity ?? item.stock ?? 0
      const res = await fetch(`${API}/api/inventory/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ barcode: item.barcode, quantity: current + qty })
      })
      const data = await res.json()
      if (res.ok) {
        toast(`Restocked ${item.name} (+${qty})`, 'success')
        setUpdates(p => ({ ...p, [item.barcode]: 0 }))
        load()
      } else {
        toast(data?.error || 'Update failed', 'error')
      }
    } catch (e) {
      toast(e.message, 'error')
    }
    setSaving(p => ({ ...p, [item.barcode]: false }))
  }

  const filtered = items.filter(i =>
    !search ||
    (i.name || '').toLowerCase().includes(search.toLowerCase()) ||
    String(i.barcode || '').includes(search)
  )

  const criticalItems = filtered.filter(i => {
    const s = i.stock_quantity ?? i.stock ?? 0
    const r = i.reorder_level ?? 5
    return s <= r * 2  // show low + critical
  })

  const displayItems = showAll ? filtered : criticalItems
  const stats = {
    critical: items.filter(i => (i.stock_quantity ?? i.stock ?? 0) <= (i.reorder_level ?? 5)).length,
    low: items.filter(i => { const s = i.stock_quantity ?? i.stock ?? 0; const r = i.reorder_level ?? 5; return s > r && s <= r*2 }).length,
    total: items.length,
  }

  return (
    <div className="bg-bg-0 min-h-screen">
      <Header />
      <PageWrapper>
        <PageHeader title="Restock." subtitle="Monitor and replenish inventory stock">
          <button onClick={load} className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </PageHeader>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card className="p-5 flex items-center gap-4 bg-red-50 border-red-200">
            <div className="p-3 rounded-xl bg-red-100 text-red-600"><AlertTriangle size={20}/></div>
            <div>
              <p className="text-2xl font-extrabold text-red-700">{loading ? '…' : stats.critical}</p>
              <p className="text-xs font-bold text-red-500 uppercase tracking-widest">Critical</p>
            </div>
          </Card>
          <Card className="p-5 flex items-center gap-4 bg-amber-50 border-amber-200">
            <div className="p-3 rounded-xl bg-amber-100 text-amber-600"><Package size={20}/></div>
            <div>
              <p className="text-2xl font-extrabold text-amber-700">{loading ? '…' : stats.low}</p>
              <p className="text-xs font-bold text-amber-500 uppercase tracking-widest">Low Stock</p>
            </div>
          </Card>
          <Card className="p-5 flex items-center gap-4 bg-emerald-50 border-emerald-200">
            <div className="p-3 rounded-xl bg-emerald-100 text-emerald-600"><CheckCircle size={20}/></div>
            <div>
              <p className="text-2xl font-extrabold text-emerald-700">{loading ? '…' : stats.total - stats.critical - stats.low}</p>
              <p className="text-xs font-bold text-emerald-500 uppercase tracking-widest">OK</p>
            </div>
          </Card>
        </div>

        {/* Search + toggle */}
        <Card className="p-4 mb-6 flex flex-col sm:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search product to restock…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <button onClick={() => setShowAll(v => !v)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-colors whitespace-nowrap ${
              !showAll ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}>
            {!showAll ? `Show All (${filtered.length})` : `Critical/Low Only (${criticalItems.length})`}
          </button>
        </Card>

        {error && <div className="p-6 text-center text-red-600 font-medium mb-4">Error: {error}</div>}

        {loading ? (
          <div className="flex justify-center py-16">
            <RefreshCw size={28} className="animate-spin text-indigo-500" />
          </div>
        ) : displayItems.length === 0 ? (
          <Card className="p-12 text-center">
            <CheckCircle size={40} className="text-emerald-400 mx-auto mb-3" />
            <p className="font-bold text-slate-700 text-lg">All stocked up!</p>
            <p className="text-slate-400 text-sm mt-1">No items need restocking right now.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {displayItems.map(item => {
              const stock = item.stock_quantity ?? item.stock ?? 0
              const reorder = item.reorder_level ?? 5
              const isCritical = stock <= reorder
              const isLow = !isCritical && stock <= reorder * 2
              const qty = updates[item.barcode] || 0
              const isSaving = saving[item.barcode]
              const pct = Math.min(100, Math.round((stock / Math.max(reorder * 3, 1)) * 100))

              return (
                <Card key={item.barcode} className={`p-5 flex flex-col gap-4 border-2 ${
                  isCritical ? 'border-red-200 bg-red-50/30' : isLow ? 'border-amber-200 bg-amber-50/20' : 'border-slate-200'
                }`}>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-extrabold text-slate-900 text-sm leading-tight truncate">{item.name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{item.category} · {item.position_tag || `Aisle ${item.aisle || '?'}`}</p>
                    </div>
                    <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-bold ${
                      isCritical ? 'bg-red-100 text-red-700' : isLow ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {isCritical ? 'Critical' : isLow ? 'Low' : 'OK'}
                    </span>
                  </div>

                  {/* Stock bar */}
                  <div>
                    <div className="flex justify-between text-xs font-bold text-slate-500 mb-1">
                      <span>Stock: <strong className="text-slate-900">{stock}</strong></span>
                      <span>Reorder at: {reorder}</span>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${
                        isCritical ? 'bg-red-500' : isLow ? 'bg-amber-500' : 'bg-emerald-500'
                      }`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>

                  {/* Restock controls */}
                  <div className="flex items-center gap-3 pt-1 border-t border-slate-200">
                    <div className="flex items-center gap-2 bg-slate-100 rounded-xl px-1 py-0.5">
                      <button onClick={() => setQty(item.barcode, qty - 1)}
                        className="p-1.5 hover:bg-white rounded-lg text-slate-500 hover:text-slate-900 transition-colors">
                        <Minus size={14}/>
                      </button>
                      <input type="number" min="0" value={qty}
                        onChange={e => setQty(item.barcode, parseInt(e.target.value) || 0)}
                        className="w-12 text-center text-sm font-extrabold bg-transparent focus:outline-none" />
                      <button onClick={() => setQty(item.barcode, qty + 1)}
                        className="p-1.5 hover:bg-white rounded-lg text-slate-500 hover:text-slate-900 transition-colors">
                        <Plus size={14}/>
                      </button>
                    </div>
                    <button onClick={() => handleRestock(item)} disabled={qty <= 0 || isSaving}
                      className={`flex-1 py-2 rounded-xl text-xs font-bold transition-colors ${
                        qty > 0 && !isSaving
                          ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20'
                          : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      }`}>
                      {isSaving ? 'Saving…' : qty > 0 ? `Add +${qty} units` : 'Set quantity'}
                    </button>
                  </div>
                </Card>
              )
            })}
          </div>
        )}

        {!loading && !showAll && criticalItems.length < filtered.length && (
          <div className="text-center mt-6">
            <button onClick={() => setShowAll(true)} className="text-sm text-indigo-600 font-bold hover:underline">
              + Show {filtered.length - criticalItems.length} more OK items
            </button>
          </div>
        )}
      </PageWrapper>
    </div>
  )
}
