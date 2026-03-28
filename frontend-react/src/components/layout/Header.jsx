import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ShoppingCart, User, Bell, Menu, X, Terminal, Search, LogOut } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'
import { useCart } from '../../hooks/useCart'
import { twMerge } from 'tailwind-merge'
import Button from '../ui/Button'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const { user, clearUser } = useAppStore()
  const { cartItems } = useCart()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { name: 'Shop', path: '/' },
    { name: 'Dashboard', path: '/dashboard', adminOnly: true },
    { name: 'Inventory', path: '/inventory', adminOnly: true },
    { name: 'Restock', path: '/restock' },
  ]

  const filteredLinks = navLinks.filter(link => !link.adminOnly || user?.is_admin)

  return (
    <header 
      className={twMerge(
        'fixed top-0 left-0 right-0 z-[100] transition-all duration-300',
        scrolled ? 'bg-white/80 backdrop-blur-xl border-b border-bg-2 shadow-sm py-3' : 'bg-transparent py-5'
      )}
    >
      <div className="max-w-[1440px] mx-auto px-6 h-12 flex items-center justify-between">
        {/* Left: Branding */}
        <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-brand-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-brand-500/20 group-hover:rotate-12 transition-transform">
                <Terminal size={22} />
            </div>
            <span className="text-xl font-black text-text-900 tracking-tighter">SMART<span className="text-brand-500">RETAIL</span>X</span>
        </Link>

        {/* Center: Desktop Nav */}
        <nav className="hidden md:flex items-center space-x-1 bg-bg-1 p-1 rounded-2xl border border-bg-2">
            {filteredLinks.map((item) => (
                <Link 
                    key={item.path} 
                    to={item.path}
                    className={twMerge(
                        "px-6 py-2 rounded-xl text-sm font-bold transition-all",
                        location.pathname === item.path 
                            ? "bg-white text-text-900 shadow-sm" 
                            : "text-text-400 hover:text-text-600"
                    )}
                >
                    {item.name}
                </Link>
            ))}
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 mr-4">
                <button className="p-2 text-text-400 hover:text-brand-500 transition-colors" aria-label="Search">
                    <Search size={20} />
                </button>
                <div className="relative">
                    <button className="p-2 text-text-400 hover:text-brand-500 transition-colors" aria-label="Notifications">
                        <Bell size={20} />
                    </button>
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 border-2 border-white rounded-full" />
                </div>
            </div>

            <Link to="/billing" aria-label="View Cart" className="relative p-2.5 bg-brand-50 text-brand-600 rounded-xl hover:bg-brand-100 transition-colors">
                <ShoppingCart size={20} />
                {cartItems.length > 0 && (
                    <motion.span 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-1 -right-1 w-5 h-5 bg-brand-500 text-white text-[10px] font-black flex items-center justify-center rounded-full border-2 border-white"
                    >
                        {cartItems.length}
                    </motion.span>
                )}
            </Link>

            <button 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 text-text-900 font-bold"
                aria-label="Toggle Navigation Menu"
            >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <Link to="/account" aria-label="User Profile" className="hidden sm:block">
                <div className="w-10 h-10 bg-bg-2 rounded-xl flex items-center justify-center text-text-400 border border-bg-3 hover:border-brand-300 transition-all cursor-pointer overflow-hidden">
                    {(user?.name || user?.username) ? (
                        <span className="font-bold text-sm text-text-900">{(user.name || user.username).charAt(0).toUpperCase()}</span>
                    ) : <User size={20} />}
                </div>
            </Link>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
            <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="absolute top-full left-0 w-full bg-white border-b border-bg-2 p-6 shadow-2xl z-50 overflow-hidden md:hidden"
            >
                <div className="flex flex-col space-y-4">
                    {filteredLinks.map((item) => (
                        <Link 
                            key={item.path}
                            to={item.path}
                            onClick={() => setMobileMenuOpen(false)}
                            className="text-lg font-bold text-text-900 hover:text-brand-500 py-2 border-b border-bg-1 last:border-none"
                        >
                            {item.name}
                        </Link>
                    ))}
                    <Button 
                        variant="danger" 
                        size="md" 
                        className="w-full rounded-2xl mt-4"
                        onClick={() => {
                            clearUser()
                            setMobileMenuOpen(false)
                        }}
                    >
                        <LogOut size={18} className="mr-2" />
                        Logout Session
                    </Button>
                </div>
            </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
