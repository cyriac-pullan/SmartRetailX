import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CreditCard, ShieldCheck, CheckCircle2, Package, ArrowLeft, Receipt } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../hooks/useCart'
import { useToast } from '../hooks/useToast'
import { processCheckout } from '../services/api'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'

export default function BillingPage() {
  const { cartItems, cartTotal, clearCart } = useCart()
  const { toast } = useToast()
  const navigate = useNavigate()
  
  const [loading, setLoading] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [orderId, setOrderId] = useState('')

  const handleCheckout = async () => {
    if (cartItems.length === 0) return
    
    setLoading(true)
    const { data, error } = await processCheckout(cartItems)
    
    if (data) {
      setOrderId(data.order_id)
      setCompleted(true)
      clearCart()
      toast('Payment successful! Your order has been placed.', 'success')
    } else {
      toast(error?.message || 'Checkout failed', 'error')
    }
    setLoading(false)
  }

  if (completed) {
    return (
      <div className="bg-bg-0 min-h-screen">
        <Header />
        <PageWrapper className="flex flex-col items-center justify-center pt-32">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-xl text-center space-y-8"
          >
            <div className="relative inline-block">
                <div className="absolute inset-0 bg-green-500/20 blur-3xl rounded-full" />
                <div className="relative w-24 h-24 bg-green-500 text-white rounded-[32px] flex items-center justify-center mx-auto shadow-2xl">
                    <CheckCircle2 size={48} />
                </div>
            </div>
            
            <div className="space-y-3">
                <h1 className="text-4xl font-extrabold text-text-900 tracking-tight">Order Confirmed!</h1>
                <p className="text-lg text-text-600 font-medium">Your items are being prepared for pickup/delivery.</p>
                <div className="inline-block px-4 py-2 bg-bg-1 border border-bg-2 rounded-xl mt-4 font-mono text-sm font-bold text-text-900">
                    ORDER ID: {orderId}
                </div>
            </div>

            <Card className="p-8 text-left space-y-6">
                <h3 className="font-bold text-text-900 flex items-center gap-2">
                    <Receipt size={20} className="text-brand-500" />
                    Transaction Details
                </h3>
                <div className="space-y-3 border-t border-bg-2 pt-4">
                    <div className="flex justify-between text-sm">
                        <span className="text-text-400">Payment Status</span>
                        <Badge variant="green">Success</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-text-400">Total Amount</span>
                        <span className="font-bold text-text-900">₹{cartTotal.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-text-400">Time</span>
                        <span className="font-medium">{new Date().toLocaleTimeString()}</span>
                    </div>
                </div>
            </Card>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/landing">
                    <Button variant="ghost" className="font-bold">Return Home</Button>
                </Link>
                <Link to="/">
                    <Button size="lg" className="rounded-2xl px-12">Continue Shopping</Button>
                </Link>
            </div>
          </motion.div>
        </PageWrapper>
      </div>
    )
  }

  return (
    <div className="bg-bg-0 min-h-screen">
      <Header />
      <PageWrapper className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        
        {/* Left: Summary */}
        <div className="lg:col-span-1" />
        <div className="lg:col-span-6 space-y-8">
            <Link to="/" className="flex items-center space-x-2 text-text-400 hover:text-brand-500 transition-colors w-fit">
                <ArrowLeft size={18} />
                <span className="text-sm font-bold uppercase tracking-widest">Back to Shop</span>
            </Link>

            <PageHeader title="Checkout." subtitle="Review your items and complete payment" />

            <div className="space-y-4">
                {cartItems.map((item) => (
                    <div key={item.barcode} className="flex items-center justify-between p-4 bg-white rounded-2xl border border-bg-2 shadow-sm">
                        <div className="flex items-center space-x-4">
                            <div className="w-12 h-12 bg-bg-1 rounded-xl flex items-center justify-center">
                                <Package size={20} className="text-text-400" />
                            </div>
                            <div>
                                <h4 className="font-bold text-text-900 text-sm">{item.name}</h4>
                                <p className="text-[11px] text-text-400 uppercase font-bold">Qty: {item.quantity}</p>
                            </div>
                        </div>
                        <span className="font-bold text-text-900">₹{(item.price * item.quantity).toLocaleString()}</span>
                    </div>
                ))}

                {cartItems.length === 0 && (
                    <div className="py-20 text-center space-y-4 bg-white rounded-3xl border-2 border-dashed border-bg-2">
                        <p className="font-bold text-text-400">No items selected</p>
                        <Link to="/">
                            <Button size="sm" variant="outline">Go Shopping</Button>
                        </Link>
                    </div>
                )}
            </div>
        </div>

        {/* Right: Payment */}
        <div className="lg:col-span-4 mt-12 lg:mt-24">
            <Card elevated className="p-8 space-y-8 rounded-[40px] sticky top-32">
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-extrabold text-text-900">Payment.</h3>
                        <CreditCard size={24} className="text-brand-500" />
                    </div>
                    
                    {/* Simulated Card Select */}
                    <div className="p-4 bg-bg-1 rounded-2xl border border-bg-2 flex items-center justify-between cursor-pointer hover:border-brand-300 transition-colors">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-6 bg-text-900 rounded flex items-center justify-center px-1">
                                <div className="w-2 h-2 bg-amber-500 rounded-full mr-1" />
                                <div className="w-2 h-2 bg-orange-500 rounded-full" />
                            </div>
                            <span className="text-sm font-bold text-text-900">•••• 4242</span>
                        </div>
                        <Badge variant="indigo">Default</Badge>
                    </div>

                    <div className="space-y-4 border-t border-bg-2 pt-6">
                        <div className="flex justify-between text-sm">
                            <span className="text-text-400">Estimated Total</span>
                            <span className="font-extrabold text-2xl text-text-900">₹{cartTotal.toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                <div className="space-y-4">
                    <Button 
                        size="lg" 
                        className="w-full h-16 rounded-2xl shadow-2xl shadow-brand-500/20"
                        onClick={handleCheckout}
                        loading={loading}
                        disabled={cartItems.length === 0}
                    >
                        Confirm Transaction
                    </Button>
                    <div className="flex items-center justify-center space-x-2 text-text-400">
                        <ShieldCheck size={14} />
                        <span className="text-[11px] font-bold uppercase tracking-widest">Secure 256-bit Encryption</span>
                    </div>
                </div>
            </Card>
        </div>
        <div className="lg:col-span-1" />
      </PageWrapper>
    </div>
  )
}
