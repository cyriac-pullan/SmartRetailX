import React, { useState, useEffect, Component } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp, Users, ShoppingCart, AlertTriangle, Play,
  Plus, Edit, Trash2, MapPin, Navigation2, RefreshCw,
  Calendar, Download, BarChart2, Package
} from 'lucide-react'
import { getDashboardStats, getAdminAds, deleteAd } from '../services/api'
import { useToast } from '../hooks/useToast'
import { Link } from 'react-router-dom'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import MetricCard from '../components/features/MetricCard'
import SalesChart from '../components/features/SalesChart'
import DataTable from '../components/ui/DataTable'
import Badge from '../components/ui/Badge'
import CategoryDonut from '../components/features/CategoryDonut'
import AisleHeatmap from '../components/features/AisleHeatmap'
import AdsCrudModal from '../components/features/AdsCrudModal'

// ── Error boundary so one panel crash can't white-screen the page ─────────────
class PanelBoundary extends Component {
  state = { error: null }
  static getDerivedStateFromError(e) { return { error: e } }
  render() {
    if (this.state.error)
      return (
        <div className="rounded-2xl border border-red-100 bg-red-50 p-6 text-sm text-red-600 font-medium">
          ⚠️ This panel failed to render — {this.state.error.message}
        </div>
      )
    return this.props.children
  }
}

// ── Skeleton loader ────────────────────────────────────────────────────────────
function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-slate-200 rounded-lg ${className}`} />
}

// ── Safe value helpers ─────────────────────────────────────────────────────────
const fmt = (n) => {
  const num = parseFloat(n) || 0
  return num.toLocaleString('en-IN', { maximumFractionDigits: 0 })
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { toast } = useToast()
  const [stats, setStats]       = useState(null)
  const [loading, setLoading]   = useState(true)
  const [ads, setAds]           = useState([])
  const [adsLoading, setAdsLoading] = useState(true)
  const [isAdModalOpen, setIsAdModalOpen] = useState(false)
  const [editingAd, setEditingAd]         = useState(null)

  useEffect(() => { fetchStats(); fetchAds() }, [])

  const fetchStats = async () => {
    setLoading(true)
    try {
      const { data } = await getDashboardStats()
      if (data) setStats(data)
    } catch (e) { /* silent */ }
    setLoading(false)
  }

  const fetchAds = async () => {
    setAdsLoading(true)
    try {
      const { data } = await getAdminAds()
      // API returns { ads: [...] } or plain array
      if (Array.isArray(data)) setAds(data)
      else if (data?.ads && Array.isArray(data.ads)) setAds(data.ads)
      else setAds([])
    } catch (e) { setAds([]) }
    setAdsLoading(false)
  }

  const handleDeleteAd = async (id) => {
    if (!window.confirm('Delete this ad?')) return
    const { error } = await deleteAd(id)
    if (error) toast(`Failed: ${error.message}`, 'error')
    else { toast('Ad deleted', 'success'); fetchAds() }
  }

  // ── Columns ────────────────────────────────────────────────────────────────
  const adColumns = [
    { key: 'title', label: 'Ad Title' },
    { key: 'aisle', label: 'Aisle', render: (r) => r.aisle || 'Any' },
    { key: 'priority', label: 'Priority', render: (r) => r.priority ?? '—' },
    { key: 'impressions', label: 'Impressions', render: (r) => (r.impressions ?? r.views ?? 0).toLocaleString() },
    { key: 'rev', label: 'Rev/View', render: (r) => `₹${(r.revenue_per_impression ?? r.rev_per_view ?? 0).toFixed(2)}` },
    {
      key: 'actions', label: '',
      render: (r) => (
        <div className="flex gap-2">
          <button onClick={() => { setEditingAd(r); setIsAdModalOpen(true) }}
            className="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"><Edit size={15}/></button>
          <button onClick={() => handleDeleteAd(r.id)}
            className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"><Trash2 size={15}/></button>
        </div>
      )
    }
  ]

  const txColumns = [
    { key: 'id', label: 'Bill ID', render: (r) => <span className="font-mono text-xs">{(r.id||'').slice(0,14)}</span> },
    { key: 'customer', label: 'Customer', render: (r) => <span className="text-xs">{r.customer || '—'}</span> },
    { key: 'amount', label: 'Amount', render: (r) => <span className="font-bold text-emerald-700">{r.amount}</span> },
    { key: 'status', label: 'Status', render: (r) => (
      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
        (r.status||'').toLowerCase() === 'paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
      }`}>{r.status || 'Paid'}</span>
    )},
    { key: 'date', label: 'Date', render: (r) => <span className="text-xs text-slate-400">{r.date || '—'}</span> },
  ]

  const fallbackTx = [
    { id: 'BILL_DEMO001', customer: 'CUST_A1B2', amount: '₹1,240', status: 'Paid', date: '2026-05-05 14:20' },
    { id: 'BILL_DEMO002', customer: 'CUST_C3D4', amount: '₹450',   status: 'Paid', date: '2026-05-05 13:45' },
    { id: 'BILL_DEMO003', customer: 'CUST_E5F6', amount: '₹2,100', status: 'Paid', date: '2026-05-05 12:10' },
  ]

  const txData = stats?.recent_transactions?.length > 0 ? stats.recent_transactions : fallbackTx

  // ── Metric values ──────────────────────────────────────────────────────────
  const revenue   = loading ? null : `₹${fmt(stats?.total_revenue)}`
  const orders    = loading ? null : String(stats?.total_orders   ?? 0)
  const customers = loading ? null : String(stats?.total_customers ?? 0)
  const lowStock  = loading ? null : String(stats?.low_stock_items ?? 0)

  return (
    <div className="bg-bg-0 min-h-screen relative overflow-hidden pb-12">
      <Header />

      <PageWrapper>
        <PageHeader title="Command Center." subtitle="Store performance and ML insights">
          <button onClick={fetchStats} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors" title="Refresh">
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
          <Button variant="outline" size="sm" className="hidden sm:flex rounded-xl bg-white border-bg-2">
            <Calendar size={16} className="mr-2" /> Last 30 Days
          </Button>
          <Button variant="primary" size="sm" className="rounded-xl">
            <Download size={16} className="mr-2" /> Export PDF
          </Button>
        </PageHeader>

        {/* ── METRICS ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="p-5"><Skeleton className="h-8 w-24 mb-2" /><Skeleton className="h-4 w-32" /></Card>
            ))
          ) : (
            <>
              <MetricCard label="Total Revenue (30d)" value={revenue}   icon={TrendingUp}    trend="+14.2%" trendUp={true}  />
              <MetricCard label="Total Orders (30d)"   value={orders}    icon={ShoppingCart}   trend="+8.1%"  trendUp={true}  />
              <MetricCard label="Active Customers"      value={customers} icon={Users}          trend="+12.4%" trendUp={true}  />
              <MetricCard label="Inventory Alert"       value={lowStock}  icon={AlertTriangle}  trend="Items low" trendUp={false}/>
            </>
          )}
        </div>

        {/* ── CHART + CATEGORY ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
          <div className="lg:col-span-8">
            <Card className="p-6 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-extrabold text-text-900 tracking-tight">Revenue Trajectory</h3>
                  <p className="text-sm text-text-400 font-medium">Daily performance · last 30 days</p>
                </div>
                <div className="flex bg-slate-100 p-1 rounded-lg">
                  <span className="px-3 py-1 text-xs font-bold bg-white shadow-sm rounded-md text-slate-800">Daily</span>
                </div>
              </div>
              <div className="flex-1">
                <PanelBoundary>
                  <SalesChart data={stats?.sales_chart_data || []} loading={loading} />
                </PanelBoundary>
              </div>
            </Card>
          </div>

          <div className="lg:col-span-4 space-y-6">
            <Card className="p-6">
              <h3 className="text-lg font-extrabold text-text-900 mb-3 flex items-center gap-2">
                <BarChart2 size={18} className="text-indigo-500" /> AI Insights
              </h3>
              <PanelBoundary>
                {loading
                  ? <><Skeleton className="h-4 w-full mb-2" /><Skeleton className="h-4 w-5/6 mb-2" /><Skeleton className="h-4 w-4/5" /></>
                  : <div className="space-y-2 text-sm text-slate-600">
                      <p>• <strong>{lowStock}</strong> products need restock</p>
                      <p>• <strong>{orders}</strong> total bills processed</p>
                      <p>• <strong>{customers}</strong> registered customers</p>
                      <p>• Revenue this period: <strong className="text-emerald-600">{revenue}</strong></p>
                    </div>
                }
              </PanelBoundary>
            </Card>
            <Card className="p-6">
              <h3 className="text-lg font-extrabold text-text-900 mb-2">Category Share</h3>
              <PanelBoundary>
                <CategoryDonut />
              </PanelBoundary>
            </Card>
          </div>
        </div>

        {/* ── HEATMAP + ESP ────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
          <div className="lg:col-span-7">
            <Card className="p-6 h-full">
              <h3 className="text-lg font-extrabold text-text-900 flex items-center gap-2 mb-1">
                <MapPin size={20} className="text-brand-500" /> Aisle Traffic Heatmap
              </h3>
              <p className="text-sm text-text-400 font-medium mb-4">Real-time conversion mapping</p>
              <PanelBoundary>
                <AisleHeatmap />
              </PanelBoundary>
            </Card>
          </div>
          <div className="lg:col-span-5">
            <Card className="p-6 h-full flex flex-col justify-between bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 bg-indigo-500/20 rounded-xl">
                    <Navigation2 size={20} className="text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-white">ESP32 Calibration</h3>
                    <p className="text-xs text-slate-400">Indoor beacon tuning</p>
                  </div>
                </div>
                <ul className="space-y-2 mb-6">
                  {['Per-beacon tx_power sliders', 'Corridor walkway length', 'Live fingerprint wizard', 'Path-loss & EMA tuning'].map(f => (
                    <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                      <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />{f}
                    </li>
                  ))}
                </ul>
              </div>
              <Link to="/admin"
                className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm transition-colors shadow-lg shadow-indigo-900/40">
                Open Admin Panel →
              </Link>
            </Card>
          </div>
        </div>

        {/* ── TABLES ───────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ads Table */}
          <Card className="p-0 overflow-hidden">
            <div className="p-5 border-b border-bg-2 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-brand-50 text-brand-500 rounded-xl"><Play size={18}/></div>
                <h3 className="text-lg font-extrabold text-text-900">Live Advertisements</h3>
              </div>
              <Button variant="primary" size="sm" onClick={() => { setEditingAd(null); setIsAdModalOpen(true) }}
                className="rounded-xl bg-brand-500 hover:bg-brand-600 border-none">
                <Plus size={15} className="mr-1"/> New Ad
              </Button>
            </div>
            <div className="p-5">
              <div className="max-h-72 overflow-y-auto">
                <PanelBoundary>
                  <DataTable columns={adColumns} data={Array.isArray(ads) ? ads.slice(0, 50) : []} loading={adsLoading} />
                </PanelBoundary>
              </div>
              {Array.isArray(ads) && ads.length > 50 && (
                <p className="text-xs text-slate-400 text-center mt-2 font-medium">{ads.length - 50} more ads not shown</p>
              )}
            </div>
          </Card>

          {/* Transactions Table */}
          <Card className="p-0 overflow-hidden">
            <div className="p-5 border-b border-bg-2 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-50 text-emerald-500 rounded-xl"><ShoppingCart size={18}/></div>
                <h3 className="text-lg font-extrabold text-text-900">Recent Transactions</h3>
              </div>
              <button onClick={fetchStats}
                className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors">
                <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/>
              </button>
            </div>
            <div className="p-5">
              <div className="max-h-72 overflow-y-auto">
                <PanelBoundary>
                  <DataTable columns={txColumns} data={txData.slice(0, 50)} loading={loading} />
                </PanelBoundary>
              </div>
              {txData.length > 50 && (
                <p className="text-xs text-slate-400 text-center mt-2 font-medium">{txData.length - 50} more not shown</p>
              )}
            </div>
          </Card>
        </div>
      </PageWrapper>

      <AdsCrudModal
        open={isAdModalOpen}
        onOpenChange={setIsAdModalOpen}
        adToEdit={editingAd}
        onSuccess={fetchAds}
      />
    </div>
  )
}
