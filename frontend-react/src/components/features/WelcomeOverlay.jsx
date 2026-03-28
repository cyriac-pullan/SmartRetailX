import React, { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function WelcomeOverlay({ name, onDone }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    // Starfield
    const stars = Array.from({ length: 160 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.4 + 0.3,
      a: Math.random(),
      d: (Math.random() - 0.5) * 0.015,
    }))

    let raf
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      stars.forEach(s => {
        s.a = Math.max(0.05, Math.min(1, s.a + s.d))
        if (s.a <= 0.05 || s.a >= 1) s.d *= -1
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(200,200,255,${s.a})`
        ctx.fill()
      })
      raf = requestAnimationFrame(draw)
    }
    draw()

    // Auto-dismiss after 3.2s
    const timer = setTimeout(() => {
      cancelAnimationFrame(raf)
      onDone?.()
    }, 3200)

    return () => {
      cancelAnimationFrame(raf)
      clearTimeout(timer)
    }
  }, [])

  // Typewriter characters
  const chars = (name || 'Customer').split('')

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed inset-0 z-[9500] flex items-center justify-center flex-col overflow-hidden"
    >
      {/* Deep space bg */}
      <div className="absolute inset-0" style={{
        background: 'radial-gradient(ellipse at 50% 40%, #1e1048 0%, #0a0720 60%, #000 100%)'
      }} />

      {/* Star canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />

      {/* Content */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
        className="relative z-10 text-center"
      >
        {/* Logo ring */}
        <div className="w-28 h-28 rounded-full mx-auto mb-5 flex items-center justify-center"
          style={{
            background: 'radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)',
            border: '1.5px solid rgba(129,140,248,0.5)',
            boxShadow: '0 0 40px rgba(99,102,241,0.25), inset 0 0 20px rgba(99,102,241,0.1)',
            animation: 'wlPulse 2s ease-in-out infinite'
          }}
        >
          <div className="w-14 h-14 bg-brand-500 rounded-2xl flex items-center justify-center text-white font-black text-2xl shadow-2xl">
            S
          </div>
        </div>

        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.55 }}
          className="text-xs font-bold uppercase tracking-[0.25em] mb-1"
          style={{ color: 'rgba(129,140,248,0.8)' }}
        >
          Welcome back
        </motion.p>

        {/* Typewriter name */}
        <div className="text-5xl font-black text-white" style={{
          textShadow: '0 0 30px rgba(99,102,241,0.8), 0 0 60px rgba(99,102,241,0.4)',
          letterSpacing: '-2px',
          minHeight: '4rem'
        }}>
          {chars.map((char, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 + i * 0.07, duration: 0.15 }}
              style={{ color: '#a78bfa' }}
            >
              {char}
            </motion.span>
          ))}
        </div>

        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8 }}
          className="mt-4 text-sm"
          style={{ color: 'rgba(255,255,255,0.45)' }}
        >
          ✨ Ready to shop smart — let's go!
        </motion.p>

        {/* Progress bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="w-44 h-0.5 mx-auto mt-7 rounded-full overflow-hidden"
          style={{ background: 'rgba(255,255,255,0.08)' }}
        >
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ duration: 2.4, delay: 0.9, ease: 'easeInOut' }}
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #6366f1, #a78bfa, #ec4899)' }}
          />
        </motion.div>
      </motion.div>

      <style>{`
        @keyframes wlPulse {
          0%, 100% { box-shadow: 0 0 40px rgba(99,102,241,.25), inset 0 0 20px rgba(99,102,241,.1); }
          50% { box-shadow: 0 0 70px rgba(129,140,248,.45), inset 0 0 35px rgba(129,140,248,.2); }
        }
      `}</style>
    </motion.div>
  )
}
