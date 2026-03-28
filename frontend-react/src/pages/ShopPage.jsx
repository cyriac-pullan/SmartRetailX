import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShoppingCart, Sparkles, Store, Search, Navigation } from 'lucide-react'
import { useCart } from '../hooks/useCart'
import { useToast } from '../hooks/useToast'
import { useAppStore } from '../store/useAppStore'
import { lookupBarcode, getContextRecs, getGeneralRecs, searchProducts } from '../services/api'
import useDebounce from '../hooks/useDebounce'

import Header from '../components/layout/Header'
import { PageWrapper, PageHeader } from '../components/layout/PageWrapper'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import BarcodeInput from '../components/features/BarcodeInput'
import CartItem from '../components/features/CartItem'
import CrossSellPanel from '../components/features/CrossSellPanel'
import ProductCard from '../components/features/ProductCard'
import ChatbotWidget from '../components/features/ChatbotWidget'

// New Components
import WelcomeOverlay from '../components/features/WelcomeOverlay'
import LiveNavigationModal from '../components/features/LiveNavigationModal'
import AdsBanner from '../components/features/AdsBanner'
import AiCartPanel from '../components/features/AiCartPanel'
import MarketBasketPanel from '../components/features/MarketBasketPanel'

export default function ShopPage() {
  const user = useAppStore(state => state.user)
  const { cartItems, addItem, cartTotal } = useCart()
  const { toast } = useToast()
  
  // Scanners & Search
  const [scanLoading, setScanLoading] = useState(false)
  const [lastScanned, setLastScanned] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearch = useDebounce(searchQuery, 300)
  const [searchResults, setSearchResults] = useState([])
  
  // Recs
  const [contextRecs, setContextRecs] = useState([])
  const [generalRecs, setGeneralRecs] = useState([])
  const [recsLoading, setRecsLoading] = useState(false)
  
  // Modals & Overlays
  const [navOpen, setNavOpen] = useState(false)
  const [navTarget, setNavTarget] = useState('')
  const [showWelcome, setShowWelcome] = useState(false)

  // Welcome Overlay trigger
  useEffect(() => {
    if (sessionStorage.getItem('srx_login_event')) {
      setShowWelcome(true)
      sessionStorage.removeItem('srx_login_event')
    }
  }, [])

  // Initial load
  useEffect(() => {
    getGeneralRecs(6).then(({ data }) => setGeneralRecs(data?.recommendations || []))
  }, [])

  // Context Recs
  useEffect(() => {
    if (cartItems.length > 0) {
      setRecsLoading(true)
      const barcodes = cartItems.map(i => i.barcode)
      getContextRecs(barcodes, lastScanned?.barcode).then(({ data }) => {
        setContextRecs(data?.recommendations || [])
        setRecsLoading(false)
      })
    } else {
      setContextRecs([])
    }
  }, [cartItems])

  // AI Product Search
  useEffect(() => {
    if (debouncedSearch.length < 2) {
      setSearchResults([])
      return
    }
    searchProducts(debouncedSearch).then(({ data }) => {
      setSearchResults(Array.isArray(data) ? data : (data?.results || []))
    })
  }, [debouncedSearch])

  const handleScan = useCallback(async (barcode, isRemoval = false) => {
    setScanLoading(true)
    const { data, error } = await lookupBarcode(barcode)
    
    if (data?.product) {
      if (isRemoval) {
        // Find if in cart
        const inCart = cartItems.find(i => i.barcode === data.product.barcode)
        if (inCart) {
          useCart.getState().removeItem(data.product.barcode)
          toast(`Removed ${data.product.name}`, 'info')
        } else {
          toast('Item not in cart', 'error')
        }
      } else {
        addItem(data.product)
        setLastScanned(data.product)
        toast(`Added ${data.product.name} to cart.`, 'success')
      }
    } else {
      toast(error?.message || 'Product not found', 'error')
    }
    setScanLoading(false)
  }, [addItem, toast, cartItems])

  const triggerNav = useCallback((name) => {
    setNavTarget(name)
    setNavOpen(true)
  }, [])

  // Voice Search (Web Speech API)
  const [isListening, setIsListening] = useState(false)
  const startVoiceSearch = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      toast("Voice search not supported in this browser.", 'error')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    
    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      setSearchQuery(transcript)
      toast(`Heard: "${transcript}"`, 'success')
    }
    recognition.onerror = () => setIsListening(false)
    recognition.onend = () => setIsListening(false)
    recognition.start()
  }

  return (
    <div className="bg-slate-50 min-h-screen">
      <AnimatePresence>
        {showWelcome && <WelcomeOverlay name={user?.name} onDone={() => setShowWelcome(false)} />}
      </AnimatePresence>

      <Header />
      
      <PageWrapper className="grid grid-cols-1 lg:grid-cols-12 gap-8 my-6">
        
        {/* LEFT COLUMN (Search & Tools) */}
        <div className="lg:col-span-3 space-y-6">
          <PageHeader title="Find Products" subtitle="Search or navigate to items" />
          
          <div className="bg-white p-4 rounded-3xl border border-bg-2 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-text-900 text-sm">AI Search</h3>
              <span className="text-[10px] font-black uppercase text-brand-500 bg-brand-50 px-2 py-0.5 rounded-md">Beta</span>
            </div>
            
            <div className="relative">
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-3 pl-10 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <Search size={16} className="absolute left-4 top-3.5 text-slate-400" />
              <button 
                onClick={startVoiceSearch}
                className={`absolute right-2 top-2 p-1.5 rounded-lg transition-colors ${isListening ? 'bg-red-100 text-red-500 animate-pulse' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}`}
              >
                🎤
              </button>
            </div>

            <AnimatePresence>
              {searchResults.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <div
                    className="space-y-2 max-h-[260px] overflow-y-auto overscroll-y-contain custom-scrollbar pr-1 pt-0.5"
                    onWheel={e => e.stopPropagation()}
                  >
                    {searchResults.map(res => (
                      <div key={res.barcode} className="flex items-center justify-between p-2 rounded-xl border border-slate-100 hover:border-brand-200 hover:bg-brand-50 transition-colors cursor-default">
                        <div className="min-w-0 pr-2">
                          <p className="text-xs font-bold text-slate-900 truncate">{res.name}</p>
                          <p className="text-[10px] text-slate-500 truncate">₹{res.price}</p>
                        </div>
                        <button 
                          onClick={() => triggerNav(res.name)}
                          className="shrink-0 p-1.5 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors"
                          title="Navigate"
                        >
                          <Navigation size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <AdsBanner position="sidebar_left" />
        </div>

        {/* CENTER COLUMN (Scanner & Recs) */}
        <div className="lg:col-span-5 space-y-8">
          <div className="space-y-6">
            <h2 className="text-3xl font-extrabold text-text-900 tracking-tight">Smart Scanner.</h2>
            <BarcodeInput onScan={handleScan} loading={scanLoading} success={!!lastScanned} />

            {/* Market Basket Integration */}
            <MarketBasketPanel lastAddedBarcode={lastScanned?.barcode} />
          </div>

          <div className="space-y-6 pt-6 border-t border-slate-200">
             <CrossSellPanel recommendations={contextRecs} loading={recsLoading} onAddToCart={addItem} />

             <div className="space-y-4">
                <div className="flex items-center justify-between">
                     <h3 className="text-lg font-extrabold text-text-900 tracking-tight flex items-center gap-2">
                        <Store size={20} className="text-brand-500" /> Recommended For You
                     </h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <AnimatePresence>
                        {generalRecs.slice(0, 4).map((product) => (
                            <ProductCard key={product.barcode} product={product} onAddToCart={addItem} />
                        ))}
                    </AnimatePresence>
                </div>
             </div>
          </div>
        </div>

        {/* RIGHT COLUMN (Cart) */}
        <div className="lg:col-span-4 space-y-4 lg:sticky lg:top-24 h-fit pb-12">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-bold text-text-900">Current Cart</h2>
            <span className="text-xs font-black bg-brand-100 text-brand-600 px-2 py-1 rounded-full">{cartItems.length} items</span>
          </div>
          
          <AiCartPanel cartItems={cartItems} />

          <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-2 custom-scrollbar">
            <AnimatePresence mode="popLayout">
              {cartItems.length > 0 ? (
                cartItems.map((item) => <CartItem key={item.barcode} product={item} />)
              ) : (
                <motion.div 
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-12 text-center space-y-4 bg-white rounded-3xl border border-dashed border-slate-300"
                >
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-slate-300">
                        <ShoppingCart size={32} />
                    </div>
                    <div>
                        <p className="font-bold text-slate-400">Your cart is empty</p>
                    </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <Card elevated className="bg-brand-500 text-white rounded-[24px] p-6 space-y-4 shadow-xl shadow-brand-500/20">
            <div className="flex justify-between items-end">
                <span className="text-xs font-bold uppercase tracking-widest opacity-80">Total Value</span>
                <span className="text-3xl font-extrabold tracking-tighter">₹{cartTotal.toLocaleString()}</span>
            </div>
            <Button 
                variant="outline" 
                className="w-full bg-white text-brand-500 border-none rounded-2xl h-14 font-bold text-base hover:bg-slate-50 mt-4"
                disabled={cartItems.length === 0}
                onClick={() => window.location.href = '/billing'}
            >
                Proceed to Checkout
            </Button>
          </Card>
        </div>

      </PageWrapper>

      <LiveNavigationModal open={navOpen} onOpenChange={setNavOpen} productName={navTarget} />
      <ChatbotWidget />
    </div>
  )
}
