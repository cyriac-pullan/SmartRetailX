import React, { useState, useEffect, Suspense } from 'react'
import { motion } from 'framer-motion'
import { 
    LayoutDashboard, TrendingUp, Users, ShoppingCart, 
    Package, Calendar, Download, AlertTriangle, Play,
    Plus, Edit, Trash2, MapPin
} from 'lucide-react'
import { getDashboardStats, getAdminAds, deleteAd } from '../services/api'
import { useToast } from '../hooks/useToast'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import MetricCard from '../components/features/MetricCard'
import SalesChart from '../components/features/SalesChart'
import DataTable from '../components/ui/DataTable'
import Badge from '../components/ui/Badge'

// New Features
import AiInsightsPanel from '../components/features/AiInsightsPanel'
import CategoryDonut from '../components/features/CategoryDonut'
import AisleHeatmap from '../components/features/AisleHeatmap'
import CalibWizard from '../components/features/CalibWizard'
import AdsCrudModal from '../components/features/AdsCrudModal'

const DashboardScene = React.lazy(() => import('../components/three/DashboardScene'))

export default function DashboardPage() {
  const { toast } = useToast()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Ads Management State
  const [ads, setAds] = useState([])
  const [adsLoading, setAdsLoading] = useState(true)
  const [isAdModalOpen, setIsAdModalOpen] = useState(false)
  const [editingAd, setEditingAd] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchAds()
  }, [])

  const fetchStats = async () => {
    setLoading(true)
    const { data } = await getDashboardStats()
    if (data) setStats(data)
    setLoading(false)
  }

  const fetchAds = async () => {
    setAdsLoading(true)
    const { data } = await getAdminAds()
    if (data) setAds(data)
    setAdsLoading(false)
  }

  const handleDeleteAd = async (id) => {
    if (!window.confirm('Are you sure you want to delete this ad?')) return
    const { error } = await deleteAd(id)
    if (error) toast(`Failed to delete: ${error.message}`, 'error')
    else {
      toast('Ad deleted', 'success')
      fetchAds()
    }
  }

  const openEditAd = (ad) => {
    setEditingAd(ad)
    setIsAdModalOpen(true)
  }

  const openNewAd = () => {
    setEditingAd(null)
    setIsAdModalOpen(true)
  }

  // Define ad table columns
  const adColumns = [
    { key: 'title', label: 'Ad Title' },
    { key: 'aisle', label: 'Target Aisle', render: (row) => row.target_location?.aisle || 'Any' },
    { key: 'priority', label: 'Priority' },
    { key: 'views', label: 'Impressions', render: (row) => row.impressions || 0 },
    { key: 'rev', label: 'Revenue/View', render: (row) => `₹${row.rev_per_view || 0}` },
    { 
      key: 'actions', 
      label: 'Actions', 
      render: (row) => (
        <div className="flex items-center gap-2">
          <button onClick={() => openEditAd(row)} className="p-1.5 text-text-400 hover:text-brand-500 rounded-lg hover:bg-brand-50 transition-colors"><Edit size={16} /></button>
          <button onClick={() => handleDeleteAd(row.id)} className="p-1.5 text-text-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"><Trash2 size={16} /></button>
        </div>
      )
    }
  ]
  
  const transactionColumns = [
    { key: 'id', label: 'Order ID' },
    { key: 'customer', label: 'Customer' },
    { key: 'amount', label: 'Amount' },
    { key: 'status', label: 'Status' },
    { key: 'date', label: 'Date' },
  ]

  const sampleTransactions = [
    { id: 'ORD-7721', customer: 'John Doe', amount: '₹1,240', status: <Badge variant="green">Paid</Badge>, date: 'Today, 14:20' },
    { id: 'ORD-7720', customer: 'Sarah Smith', amount: '₹450', status: <Badge variant="green">Paid</Badge>, date: 'Today, 13:45' },
    { id: 'ORD-7719', customer: 'Mike Ross', amount: '₹2,100', status: <Badge variant="amber">Pending</Badge>, date: 'Today, 12:10' },
  ]

  return (
    <div className="bg-bg-0 min-h-screen relative overflow-hidden pb-12">
      <Suspense fallback={null}><DashboardScene /></Suspense>
      <Header />
      
      <PageWrapper>
        <PageHeader title="Command Center." subtitle="Store performance and ML insights">
            <Button variant="outline" size="sm" className="hidden sm:flex rounded-xl bg-white border-bg-2">
                <Calendar size={16} className="mr-2" /> Last 30 Days
            </Button>
            <Button variant="primary" size="sm" className="rounded-xl">
                <Download size={16} className="mr-2" /> Export PDF
            </Button>
        </PageHeader>

        {/* TOP METRICS ROW */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <MetricCard 
                label="Total Revenue (30d)" 
                value={stats ? `₹${stats.total_revenue.toLocaleString()}` : "₹0"} 
                icon={TrendingUp} trend="+14.2%" trendUp={true}
            />
            <MetricCard 
                label="Total Orders (30d)" 
                value={stats?.total_orders || "0"} 
                icon={ShoppingCart} trend="+8.1%" trendUp={true}
            />
            <MetricCard 
                label="Active Customers" 
                value={stats?.total_customers || "0"} 
                icon={Users} trend="+12.4%" trendUp={true}
            />
            <MetricCard 
                label="Inventory Alert" 
                value={stats?.low_stock_items || "0"} 
                icon={AlertTriangle} trend="Items low" trendUp={false}
            />
        </div>

        {/* MAIN VISUALIZATIONS ROW */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
            
            {/* Sales Line Chart */}
            <div className="lg:col-span-8">
                <Card className="p-6 h-full flex flex-col hidden-scroll">
                    <div className="flex items-center justify-between mb-2">
                        <div>
                            <h3 className="text-xl font-extrabold text-text-900 tracking-tight">Revenue Trajectory</h3>
                            <p className="text-sm text-text-400 font-medium">Daily performance context</p>
                        </div>
                        <div className="flex bg-slate-100 p-1 rounded-lg">
                             <button className="px-3 py-1 text-xs font-bold bg-white shadow-sm rounded-md text-slate-800">Daily</button>
                             <button className="px-3 py-1 text-xs font-bold text-slate-500 hover:text-slate-800">Weekly</button>
                        </div>
                    </div>
                    <div className="flex-1 mt-4">
                      <SalesChart data={stats?.sales_chart_data || []} loading={loading} />
                    </div>
                </Card>
            </div>

            {/* AI Insights & Donut */}
            <div className="lg:col-span-4 space-y-6">
                <Card className="p-6">
                  <AiInsightsPanel />
                </Card>

                <Card className="p-6">
                    <h3 className="text-lg font-extrabold text-text-900 mb-2">Category Share</h3>
                    <CategoryDonut />
                </Card>
            </div>
        </div>

        {/* SECONDARY ROW: HEATMAP & CALIBRATION */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
            <div className="lg:col-span-7">
               <Card className="p-6 h-full">
                  <h3 className="text-lg font-extrabold text-text-900 flex items-center gap-2">
                     <MapPin size={20} className="text-brand-500" /> Aisle Traffic Heatmap
                  </h3>
                  <p className="text-sm text-text-400 font-medium mb-4">Real-time conversion mapping</p>
                  <AisleHeatmap />
               </Card>
            </div>
            
            <div className="lg:col-span-5">
               <CalibWizard />
            </div>
        </div>

        {/* TABLES ROW: ADS & TRANSACTIONS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Ad Management Table */}
            <Card className="p-0 overflow-hidden">
                <div className="p-6 border-b border-bg-2 flex items-center justify-between bg-slate-50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-brand-50 text-brand-500 rounded-xl"><Play size={20} /></div>
                        <h3 className="text-xl font-extrabold text-text-900">Live Advertisements</h3>
                    </div>
                    <Button variant="primary" size="sm" onClick={openNewAd} className="rounded-xl bg-brand-500 hover:bg-brand-600 border-none">
                        <Plus size={16} className="mr-1" /> New Ad
                    </Button>
                </div>
                <div className="p-6">
                  <DataTable columns={adColumns} data={ads} loading={adsLoading} />
                </div>
            </Card>

            {/* Recent Transactions */}
            <Card className="p-0 overflow-hidden">
                <div className="p-6 border-b border-bg-2 flex items-center justify-between bg-slate-50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-50 text-emerald-500 rounded-xl"><ShoppingCart size={20} /></div>
                        <h3 className="text-xl font-extrabold text-text-900">Recent Transactions</h3>
                    </div>
                </div>
                <div className="p-6">
                  <DataTable columns={transactionColumns} data={stats?.recent_transactions?.length > 0 ? stats.recent_transactions : sampleTransactions} loading={loading} />
                </div>
            </Card>
        </div>

      </PageWrapper>

      {/* Models & Overlays */}
      <AdsCrudModal 
         open={isAdModalOpen} 
         onOpenChange={setIsAdModalOpen} 
         adToEdit={editingAd} 
         onSuccess={fetchAds} 
      />
    </div>
  )
}
