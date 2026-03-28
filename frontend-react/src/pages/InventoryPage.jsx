import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Package, Search, Plus, Filter, MoreVertical, Edit, Trash2 } from 'lucide-react'
import { twMerge } from 'tailwind-merge'
import { getInventory } from '../services/api'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import DataTable from '../components/ui/DataTable'
import Badge from '../components/ui/Badge'

export default function InventoryPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    setLoading(true)
    const { data } = await getInventory()
    if (data) setItems(data.inventory || [])
    setLoading(false)
  }

  const columns = [
    { key: 'barcode', label: 'Barcode', sortable: true },
    { key: 'name', label: 'Product Name', sortable: true },
    { key: 'category', label: 'Category', sortable: true },
    { key: 'price', label: 'Price', sortable: true },
    { key: 'stock', label: 'Stock', sortable: true },
    { key: 'actions', label: '' },
  ]

  const filteredItems = items.filter(i => 
    i.name.toLowerCase().includes(search.toLowerCase()) || 
    i.barcode.includes(search)
  ).map(item => ({
    ...item,
    price: `₹${item.price}`,
    stock: (
        <div className="flex items-center space-x-2">
            <div className={twMerge(
                "w-2 h-2 rounded-full",
                item.stock > 20 ? "bg-green-500" : item.stock > 5 ? "bg-amber-500" : "bg-red-500"
            )} />
            <span className="font-bold">{item.stock}</span>
        </div>
    ),
    category: <Badge variant="gray">{item.category}</Badge>,
    actions: (
        <div className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" className="p-2 text-text-400 hover:text-brand-500">
                <Edit size={16} />
            </Button>
            <Button variant="ghost" size="sm" className="p-2 text-text-400 hover:text-red-500">
                <Trash2 size={16} />
            </Button>
        </div>
    )
  }))

  return (
    <div className="bg-bg-0 min-h-screen">
      <Header />
      
      <PageWrapper>
        <PageHeader title="Inventory." subtitle="Manage and track your store stock levels">
            <Button variant="primary" className="rounded-xl">
                <Plus size={18} className="mr-2" />
                Add New Product
            </Button>
        </PageHeader>

        <Card className="p-6 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex-1 w-full max-w-md">
                <Input 
                    placeholder="Search by name or barcode..." 
                    icon={Search}
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="bg-bg-1 border-none px-4 py-2"
                />
            </div>
            <div className="flex items-center gap-3">
                <Button variant="outline" size="sm" className="rounded-xl px-4">
                    <Filter size={16} className="mr-2" />
                    Filters
                </Button>
                <div className="h-8 w-px bg-bg-2" />
                <p className="text-sm font-bold text-text-400">Total: {items.length} Products</p>
            </div>
        </Card>

        <DataTable 
            columns={columns} 
            data={filteredItems} 
            loading={loading}
        />
      </PageWrapper>
    </div>
  )
}
