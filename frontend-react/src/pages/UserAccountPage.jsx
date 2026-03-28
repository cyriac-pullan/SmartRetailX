import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Mail, Fingerprint, Receipt, Shield, LogOut, Package, ArrowRight, RefreshCw, ShoppingCart } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { getTransactions, getRestockRecs } from '../services/api'
import { useCart } from '../hooks/useCart'
import { useToast } from '../hooks/useToast'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import ProductCard from '../components/features/ProductCard'

export default function UserAccountPage() {
  const { user, clearUser } = useAppStore()
  const { addItem } = useCart()
  const { toast } = useToast()
  
  const [orders, setOrders] = useState([])
  const [restocks, setRestocks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    const fetchData = async () => {
      setLoading(true)
      const [{ data: txData }, { data: rsData }] = await Promise.all([
        getTransactions(user.id),
        getRestockRecs(user.id)
      ])
      if (txData?.transactions) setOrders(txData.transactions)
      if (rsData?.recommendations) setRestocks(rsData.recommendations)
      setLoading(false)
    }
    fetchData()
  }, [user])

  if (!user) return null

  const totalSpent = orders.reduce((sum, ord) => sum + ord.total_amount, 0)

  return (
    <div className="bg-bg-0 min-h-screen pb-12">
      <Header />
      
      <PageWrapper>
        <PageHeader title="Account." subtitle="Manage your profile and order settings" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Sidebar Profile Card */}
            <div className="lg:col-span-4 space-y-6">
                <Card elevated className="p-10 text-center space-y-6 rounded-[40px]">
                    <div className="relative inline-block">
                        <div className="w-32 h-32 bg-gradient-to-br from-brand-500 to-indigo-600 rounded-full flex items-center justify-center text-white shadow-2xl mx-auto">
                            <span className="text-4xl font-black">{(user.name || user.username || '?').charAt(0).toUpperCase()}</span>
                        </div>
                        <div className="absolute bottom-1 right-1 w-8 h-8 bg-green-500 border-4 border-white rounded-full" />
                    </div>
                    
                    <div>
                        <h2 className="text-2xl font-extrabold text-text-900">{user.name || user.username}</h2>
                        <p className="text-sm font-medium text-text-400">{user.email || '—'}</p>
                        <Badge variant="indigo" className="mt-4 px-4">Member Plus</Badge>
                    </div>

                    <div className="pt-6 border-t border-bg-2 grid grid-cols-2 gap-4">
                        <div className="text-center">
                            <p className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Total Orders</p>
                            <p className="text-xl font-extrabold text-text-900">{loading ? '—' : orders.length}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Spent</p>
                            <p className="text-xl font-extrabold text-text-900">{loading ? '—' : `₹${Math.round(totalSpent).toLocaleString()}`}</p>
                        </div>
                    </div>

                    <Button 
                        variant="danger" 
                        size="md" 
                        className="w-full rounded-2xl mt-4"
                        onClick={clearUser}
                    >
                        <LogOut size={18} className="mr-2" />
                        Logout Session
                    </Button>
                </Card>

                <Card className="p-8 space-y-4">
                    <h3 className="font-bold text-text-900 flex items-center gap-2">
                        <Shield size={18} className="text-brand-500" />
                        Security Settings
                    </h3>
                    <div className="space-y-3">
                        <Button variant="outline" size="sm" className="w-full justify-start rounded-xl text-xs font-bold uppercase transition-transform hover:translate-x-1">Change Password</Button>
                        <Button variant="outline" size="sm" className="w-full justify-start rounded-xl text-xs font-bold uppercase transition-transform hover:translate-x-1">2FA Verification</Button>
                    </div>
                </Card>

                {/* Restock Reminders Panel */}
                {restocks.length > 0 && (
                  <Card className="p-6 bg-brand-50 border-brand-200">
                      <h3 className="font-bold text-brand-900 flex items-center gap-2 mb-4">
                          <RefreshCw size={18} className="text-brand-500" />
                          Buy Again
                      </h3>
                      <div className="space-y-3">
                          {restocks.slice(0,3).map(item => (
                              <div key={item.barcode} className="flex items-center justify-between p-3 bg-white rounded-xl shadow-sm border border-brand-100">
                                  <div>
                                      <p className="text-sm font-bold text-text-900">{item.name}</p>
                                      <p className="text-xs text-text-400">₹{item.price}</p>
                                  </div>
                                  <button 
                                      onClick={() => { addItem(item); toast(`${item.name} added`, 'success') }}
                                      className="p-2 bg-brand-500 text-white rounded-xl hover:bg-brand-600 transition-colors"
                                  >
                                      <ShoppingCart size={16} />
                                  </button>
                              </div>
                          ))}
                      </div>
                  </Card>
                )}
            </div>

            {/* Main Content: Order History */}
            <div className="lg:col-span-8 space-y-8">
                <div className="flex items-center justify-between">
                    <h3 className="text-xl font-extrabold text-text-900 flex items-center gap-3">
                        <Receipt size={22} className="text-brand-500" />
                        Recent Purchases
                    </h3>
                </div>

                <div className="space-y-4">
                    {loading ? (
                        <div className="text-center p-12 text-text-400 font-medium animate-pulse">Loading orders...</div>
                    ) : orders.length === 0 ? (
                        <div className="text-center p-12 bg-bg-1 rounded-3xl border border-dashed border-bg-2">
                            <p className="text-text-400 font-medium">No previous orders found.</p>
                        </div>
                    ) : (
                        orders.map((order, i) => (
                            <motion.div
                                key={order.id}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.05 }}
                            >
                                <Card hoverable className="p-6 flex flex-col sm:flex-row sm:items-center justify-between group gap-4">
                                    <div className="flex items-center space-x-6">
                                        <div className="w-12 h-12 shrink-0 bg-bg-1 rounded-2xl flex items-center justify-center text-text-400 group-hover:bg-brand-50 group-hover:text-brand-500 transition-colors">
                                            <Package size={24} />
                                        </div>
                                        <div className="space-y-1">
                                            <h4 className="font-extrabold text-text-900 tracking-tight">Order #{order.id}</h4>
                                            <p className="text-xs font-bold text-text-400">{new Date(order.timestamp).toLocaleString()}</p>
                                            <p className="text-xs text-text-500">{order.items.length} items</p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-6 sm:space-x-12">
                                        <div className="text-right">
                                            <p className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Total</p>
                                            <p className="font-bold text-text-900">₹{order.total_amount.toLocaleString()}</p>
                                        </div>
                                        <Badge variant="green">Delivered</Badge>
                                        <Button variant="ghost" size="sm" className="hidden sm:flex p-2">
                                            <ArrowRight size={20} className="text-text-400" />
                                        </Button>
                                    </div>
                                </Card>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
      </PageWrapper>
    </div>
  )
}
