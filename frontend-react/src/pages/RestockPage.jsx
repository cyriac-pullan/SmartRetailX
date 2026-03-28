import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Package, ArrowRight, AlertTriangle, Plus, Minus, Search } from 'lucide-react'
import { getInventory, updateStock } from '../services/api'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import { useToast } from '../hooks/useToast'

export default function RestockPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [updates, setUpdates] = useState({}) // { barcode: quantity }
  const { toast } = useToast()

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    setLoading(true)
    const { data } = await getInventory()
    if (data) setItems(data.inventory || [])
    setLoading(false)
  }

  const handleUpdateQty = (barcode, delta) => {
    setUpdates(prev => ({
        ...prev,
        [barcode]: Math.max(0, (prev[barcode] || 0) + delta)
    }))
  }

  const submitRestock = async (item) => {
    const qtyToAdd = updates[item.barcode] || 0
    if (qtyToAdd <= 0) return

    const { data, error } = await updateStock(item.barcode, qtyToAdd)
    if (data) {
        toast(`Successfully restocked ${item.name}!`, 'success')
        setUpdates(prev => ({ ...prev, [item.barcode]: 0 }))
        fetchInventory()
    } else {
        toast(error?.message || 'Update failed', 'error')
    }
  }

  const restockItems = items.filter(i => 
    i.name.toLowerCase().includes(search.toLowerCase()) || 
    i.barcode.includes(search)
  ).sort((a, b) => a.stock - b.stock)

  return (
    <div className="bg-bg-0 min-h-screen">
      <Header />
      
      <PageWrapper>
        <PageHeader title="Restock." subtitle="Monitor and replenish inventory stock" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Search & Stats */}
            <div className="lg:col-span-12">
                <div className="flex flex-col md:flex-row gap-6 items-center">
                    <Card className="flex-1 p-6 w-full">
                        <Input 
                            placeholder="Find product to restock..." 
                            icon={Search}
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </Card>
                    <Card className="p-6 bg-amber-50 border-amber-100 flex items-center space-x-4">
                        <div className="p-3 bg-amber-500 text-white rounded-2xl">
                            <AlertTriangle size={24} />
                        </div>
                        <div>
                            <p className="text-xl font-extrabold text-amber-700">
                                {items.filter(i => i.stock < 10).length}
                            </p>
                            <p className="text-xs font-bold text-amber-600 uppercase tracking-widest">Low Stock Items</p>
                        </div>
                    </Card>
                </div>
            </div>

            {/* Restock List */}
            <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {restockItems.map((item) => (
                    <motion.div
                        key={item.barcode}
                        layout
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                    >
                        <Card hoverable className="p-6 space-y-6 flex flex-col justify-between h-full bg-white">
                            <div className="space-y-4">
                                <div className="flex justify-between items-start">
                                    <Badge variant={item.stock < 10 ? 'red' : 'green'}>
                                        {item.stock < 10 ? 'Critically Low' : 'In Stock'}
                                    </Badge>
                                    <span className="text-[10px] font-bold text-text-400 uppercase tracking-widest">#{item.barcode}</span>
                                </div>
                                
                                <div>
                                    <h4 className="text-lg font-extrabold text-text-900 group-hover:text-brand-500 transition-colors uppercase leading-tight pt-3">
                                        {item.name}
                                    </h4>
                                    <p className="text-xs font-bold text-text-400 mt-1">{item.category}</p>
                                </div>

                                <div className="flex items-end justify-between">
                                    <div className="space-y-1">
                                        <p className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Current Level</p>
                                        <div className="flex items-baseline space-x-1">
                                            <span className="text-2xl font-extrabold text-text-900">{item.stock}</span>
                                            <span className="text-sm font-bold text-text-400">Items</span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-[10px] font-bold text-text-400 uppercase tracking-widest">Unit Price</p>
                                        <p className="font-bold text-text-900">₹{item.price}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-bg-2 space-y-4">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-bold text-text-900">Add to Stock</p>
                                    <div className="flex items-center space-x-4 bg-bg-1 p-1 rounded-xl">
                                        <button 
                                            onClick={() => handleUpdateQty(item.barcode, -1)}
                                            className="p-1.5 hover:bg-white rounded-lg transition-colors text-text-400 hover:text-text-900"
                                        >
                                            <Minus size={16} />
                                        </button>
                                        <span className="text-lg font-extrabold text-brand-500 w-8 text-center">
                                            {updates[item.barcode] || 0}
                                        </span>
                                        <button 
                                            onClick={() => handleUpdateQty(item.barcode, 1)}
                                            className="p-1.5 hover:bg-white rounded-lg transition-colors text-text-400 hover:text-text-900"
                                        >
                                            <Plus size={16} />
                                        </button>
                                    </div>
                                </div>

                                <Button 
                                    variant="primary" 
                                    className="w-full rounded-2xl font-bold"
                                    disabled={!updates[item.barcode]}
                                    onClick={() => submitRestock(item)}
                                >
                                    Confirm Restock
                                    <RefreshCw size={16} className="ml-2" />
                                </Button>
                            </div>
                        </Card>
                    </motion.div>
                ))}
            </div>
        </div>
      </PageWrapper>
    </div>
  )
}
