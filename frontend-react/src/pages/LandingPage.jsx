import React, { Suspense, lazy } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, Terminal, BarChart3, ShieldCheck, Zap } from 'lucide-react'
import Button from '../components/ui/Button'
import { twMerge } from 'tailwind-merge'

const HeroScene = React.lazy(() => import('../components/three/HeroScene'))

const features = [
  {
    title: 'AI Swarm Intelligence',
    desc: 'Personalized product suggestions driven by advanced market basket analysis running in the neural core.',
    icon: Zap,
    color: 'text-amber-400'
  },
  {
    title: 'Global Telemetry',
    desc: 'Live spatial tracking and inventory performance at your fingertips, streamed securely.',
    icon: BarChart3,
    color: 'text-brand-400'
  },
  {
    title: 'Cryptographic Checkout',
    desc: 'Encrypted billing and instant off-chain transaction history for total peace of mind.',
    icon: ShieldCheck,
    color: 'text-green-400'
  }
]

// Splitting text animation utility
const letterAnimation = {
  hidden: { opacity: 0, y: 50 },
  visible: { opacity: 1, y: 0 }
}

export default function LandingPage() {
  return (
    <div className="bg-[#030305] text-white overflow-x-hidden selection:bg-brand-500/30 selection:text-white">
      {/* Cinematic Film Grain Noise Overlay */}
      <div 
        className="pointer-events-none fixed inset-0 z-50 opacity-[0.03] mix-blend-overlay"
        style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }}
      />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden isolate">
        
        {/* Absolute 3D Backdrop */}
        <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-gradient-to-b from-[#030305]/0 via-[#030305]/60 to-[#030305] z-10 pointer-events-none" />
            <Suspense fallback={<div className="absolute inset-0 bg-[#030305] animate-pulse" />}>
                <HeroScene />
            </Suspense>
        </div>

        <div className="max-w-[1440px] mx-auto px-6 relative z-20 w-full flex flex-col items-center text-center mt-[-5vh]">
            <motion.div
                initial={{ opacity: 0, scale: 0.9, filter: 'blur(10px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="space-y-10 flex flex-col items-center"
            >
                <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md">
                    <span className="flex h-2 w-2 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
                    </span>
                    <span className="text-xs font-bold tracking-[0.2em] text-white/80 uppercase">SmartRetailX v2.0 Operational</span>
                </div>
                
                <h1 className="text-6xl md:text-8xl lg:text-9xl font-black tracking-tighter leading-[0.95] mix-blend-lighten text-transparent bg-clip-text bg-gradient-to-br from-white via-white/90 to-white/40">
                    RETAIL<br/>
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-400 via-indigo-600 to-purple-600">EVOLVED.</span>
                </h1>
                
                <motion.p 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 0.8 }}
                    className="text-lg md:text-2xl text-white/60 font-medium max-w-2xl leading-relaxed font-sans"
                >
                    A hyper-spatial shopping interface powered by deep neural heuristics. Experience immersive visual commerce.
                </motion.p>

                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, delay: 1 }}
                    className="flex flex-col sm:flex-row items-center gap-6 pt-8"
                >
                    <Link to="/login">
                        <button className="relative group px-10 py-5 bg-white text-[#030305] rounded-full font-black text-lg hover:scale-105 transition-all duration-300 ease-out flex items-center shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)]">
                            Initialize Sequence
                            <ArrowRight size={24} className="ml-3 group-hover:translate-x-2 transition-transform" />
                        </button>
                    </Link>
                </motion.div>
            </motion.div>
        </div>
      </section>

      {/* Features Strip (Dark Glassmorphism) */}
      <section className="py-32 relative z-20 bg-[#030305]">
        <div className="max-w-[1440px] mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {features.map((f, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.95, y: 40 }}
                        whileInView={{ opacity: 1, scale: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8, delay: i * 0.15, ease: [0.22, 1, 0.36, 1] }}
                        className="p-10 rounded-[32px] bg-white/[0.02] border border-white/[0.05] hover:bg-white/[0.04] transition-colors relative overflow-hidden group"
                    >
                        {/* Dynamic glow effect */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/20 rounded-full blur-[60px] group-hover:bg-brand-500/40 transition-colors" />
                        
                        <div className={twMerge("mb-8", f.color)}>
                            <f.icon size={40} className="drop-shadow-[0_0_15px_currentColor]" />
                        </div>
                        <h3 className="text-2xl font-black text-white mb-4 tracking-tight">{f.title}</h3>
                        <p className="text-white/50 font-medium leading-relaxed text-lg">{f.desc}</p>
                    </motion.div>
                ))}
            </div>
        </div>
      </section>

      {/* Holographic Product Showcase */}
      <section className="py-40 relative z-20 overflow-hidden">
        <div className="absolute left-[-20%] top-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-brand-500/10 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="max-w-[1440px] mx-auto px-6">
            <div className="flex flex-col lg:flex-row items-center gap-24">
                <motion.div 
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 1 }}
                    className="flex-1 space-y-8"
                >
                    <h2 className="text-5xl md:text-6xl font-black text-white tracking-tighter leading-[1.1]">
                        Holographic <br/> 
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-indigo-600">Inventory Sync.</span>
                    </h2>
                    <p className="text-xl text-white/50 font-medium leading-relaxed max-w-lg">
                        Interact with products in a spatially consistent cinematic environment. Total awareness of your retail ecosystem.
                    </p>
                    <ul className="space-y-6 pt-4 border-l border-white/10 pl-6">
                        {['Volumetric Light Interaction', 'High-Detail Mesh Rendering', 'Spatial Awareness Engine'].map((item) => (
                            <li key={item} className="flex items-center space-x-4 text-white/80 font-bold text-lg">
                                <div className="w-8 h-8 rounded-full border border-white/20 flex items-center justify-center shrink-0">
                                    <div className="w-2 h-2 bg-brand-500 rounded-full shadow-[0_0_10px_#6366f1]" />
                                </div>
                                <span>{item}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>
                
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9, rotateY: 15 }}
                    whileInView={{ opacity: 1, scale: 1, rotateY: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="flex-1 w-full relative"
                >
                    <div className="aspect-square max-w-[600px] mx-auto relative rounded-[40px] border border-white/10 bg-white/[0.01] backdrop-blur-3xl overflow-hidden shadow-[0_0_100px_-20px_rgba(99,102,241,0.3)] flex items-center justify-center">
                        <div className="absolute inset-0 bg-gradient-to-tr from-brand-500/20 via-transparent to-transparent opacity-50" />
                        <Terminal size={120} className="text-white/20" />
                        <div className="absolute top-6 left-6 right-6 flex items-center space-x-2">
                            <div className="w-3 h-3 rounded-full bg-red-500/80" />
                            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                            <div className="w-3 h-3 rounded-full bg-green-500/80" />
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-32 relative z-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-brand-900/40 to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
            <motion.div
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 1 }}
                className="space-y-12"
            >
                <h2 className="text-5xl md:text-7xl font-black tracking-tight text-white mix-blend-screen">
                    Enter the Grid.
                </h2>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                    <Link to="/login" className="w-full sm:w-auto">
                        <button className="w-full sm:w-auto px-12 py-5 rounded-full bg-brand-500 hover:bg-brand-400 text-white font-black text-lg transition-all shadow-[0_0_30px_rgba(99,102,241,0.5)]">
                            Boot System
                        </button>
                    </Link>
                    <Link to="/register" className="w-full sm:w-auto">
                        <button className="w-full sm:w-auto px-12 py-5 rounded-full border border-white/20 hover:bg-white/10 text-white font-bold text-lg transition-colors">
                            Request Clearance
                        </button>
                    </Link>
                </div>
            </motion.div>
        </div>
      </section>
    </div>
  )
}
