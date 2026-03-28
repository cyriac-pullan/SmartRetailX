import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, ArrowRight, Store, ShieldCheck } from 'lucide-react'
import { loginUser } from '../services/api'
import { useAppStore } from '../store/useAppStore'
import { useToast } from '../hooks/useToast'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  
  const setUser = useAppStore((state) => state.setUser)
  const { toast } = useToast()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    if (!identifier || !password) {
      toast('Please fill in all fields', 'warning')
      return
    }

    setLoading(true)
    const { data, error } = await loginUser(identifier, password)
    
    if (data) {
      setUser(data)
      toast(`Welcome back, ${data.name || data.username || 'User'}!`, 'success')
      navigate('/')
    } else {
      toast(error?.message || 'Invalid credentials', 'error')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 bg-white selection:bg-brand-200">
      {/* Left Panel - Visual */}
      <div className="hidden lg:flex flex-col items-center justify-center p-20 relative overflow-hidden bg-bg-1">
        <div className="absolute top-0 left-0 w-full h-full opacity-60">
            <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-[-5%] left-[-5%] w-[400px] h-[400px] bg-indigo-500/10 rounded-full blur-[100px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 w-full max-w-lg space-y-12"
        >
          <div className="w-16 h-16 bg-brand-500 rounded-2xl flex items-center justify-center text-white shadow-xl rotate-6">
            <Store size={32} />
          </div>
          
          <div className="space-y-4">
             <h2 className="text-5xl font-extrabold text-text-900 tracking-tight leading-tight">
                Secure access to your <br/> Retail Portal.
             </h2>
             <p className="text-xl text-text-600 font-medium leading-relaxed">
                Log in with your customer ID or registered email to manage orders and track analytics.
             </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-6 bg-white rounded-3xl border border-bg-2 shadow-sm space-y-3 hover:translate-y-[-4px] transition-transform">
                <div className="p-2 bg-green-50 text-green-600 w-fit rounded-lg"><ShieldCheck size={20}/></div>
                <p className="font-bold text-sm">Enterprise Grade <br/> Security</p>
            </div>
            <div className="p-6 bg-white rounded-3xl border border-bg-2 shadow-sm space-y-3 hover:translate-y-[-4px] transition-transform">
                <div className="p-2 bg-brand-50 text-brand-500 w-fit rounded-lg"><ArrowRight size={20}/></div>
                <p className="font-bold text-sm">Real-time <br/> Context Sync</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 md:p-12 relative overflow-hidden">
        <motion.div
           initial={{ opacity: 0, x: 20 }}
           animate={{ opacity: 1, x: 0 }}
           className="w-full max-w-sm space-y-10"
        >
          <div className="space-y-2">
            <h1 className="text-3xl font-extrabold text-text-900 tracking-tight">Login.</h1>
            <p className="text-text-600 font-medium">Enter your credentials to continue</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <Input
              label="Email or Customer ID"
              icon={Mail}
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="id_123 or name@mail.com"
            />
            <Input
              label="Password"
              type="password"
              icon={Lock}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />

            <Button
              type="submit"
              size="lg"
              className="w-full rounded-2xl shadow-xl shadow-brand-500/20"
              loading={loading}
            >
              Sign In
            </Button>
          </form>

          <footer className="pt-4 text-center">
            <p className="text-sm font-medium text-text-600">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-brand-600 hover:text-brand-500 font-bold transition-colors"
              >
                Create one now
              </Link>
            </p>
          </footer>
        </motion.div>
      </div>
    </div>
  )
}
