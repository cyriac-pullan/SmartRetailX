import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { User, Mail, Lock, Fingerprint, Store, ArrowLeft } from 'lucide-react'
import { registerUser } from '../services/api'
import { useToast } from '../hooks/useToast'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    barcode: '',
    password: '',
    confirmPassword: '',
  })
  const [loading, setLoading] = useState(false)
  
  const { toast } = useToast()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      toast('Passwords do not match', 'error')
      return
    }

    setLoading(true)
    const { data, error } = await registerUser(formData)
    
    if (data) {
      toast('Account created successfully!', 'success')
      navigate('/login')
    } else {
      toast(error?.message || 'Registration failed', 'error')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-bg-0 flex flex-col md:flex-row">
      {/* Visual Panel */}
      <div className="md:w-1/3 bg-text-900 p-12 text-white flex flex-col justify-between overflow-hidden relative">
        <div className="absolute inset-0 bg-brand-500 opacity-20 blur-[100px] translate-y-20 translate-x-[-20%]" />
        
        <Link to="/landing" className="relative z-10 flex items-center space-x-2 text-white/60 hover:text-white transition-colors">
            <ArrowLeft size={20} />
            <span className="font-bold text-sm tracking-tight uppercase">Home</span>
        </Link>

        <div className="relative z-10 space-y-6">
            <div className="w-16 h-16 bg-white text-text-900 rounded-2xl flex items-center justify-center shadow-2xl">
                <Store size={32} />
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight leading-tight">
                Join the <br/> <span className="text-brand-500">Retail Revolution.</span>
            </h1>
            <p className="text-white/60 font-medium max-w-[240px]">
                Create your smart account to get started with 3D shopping and analytics.
            </p>
        </div>

        <div className="relative z-10 pt-12">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/30">SmartRetailX v2.0</p>
        </div>
      </div>

      {/* Form Panel */}
      <div className="flex-1 bg-white p-8 md:p-24 flex items-center justify-center">
        <motion.div
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           className="w-full max-w-sm space-y-8"
        >
          <div className="space-y-1">
            <h2 className="text-3xl font-extrabold text-text-900 tracking-tight">Create Account.</h2>
            <p className="text-text-600 font-medium text-sm">Fill in the details to get started</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            <Input
              name="name"
              label="Full Name"
              icon={User}
              value={formData.name}
              onChange={handleChange}
              placeholder="John Doe"
              required
            />
            <Input
              name="email"
              label="Email Address"
              type="email"
              icon={Mail}
              value={formData.email}
              onChange={handleChange}
              placeholder="john@example.com"
              required
            />
            <Input
              name="barcode"
              label="Customer ID / Barcode"
              icon={Fingerprint}
              value={formData.barcode}
              onChange={handleChange}
              placeholder="Unique identifier"
              required
            />
            <Input
              name="password"
              label="Password"
              type="password"
              icon={Lock}
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
            <Input
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              icon={Lock}
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />

            <Button
              type="submit"
              size="lg"
              className="w-full rounded-2xl shadow-xl shadow-brand-500/10 mt-4"
              loading={loading}
            >
              Register Account
            </Button>
          </form>

          <footer className="text-center">
            <p className="text-sm font-medium text-text-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-brand-600 hover:text-brand-500 font-bold transition-colors"
              >
                Sign In
              </Link>
            </p>
          </footer>
        </motion.div>
      </div>
    </div>
  )
}
