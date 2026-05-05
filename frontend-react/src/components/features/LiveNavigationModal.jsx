import React, { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, MapPin, Navigation2, Loader2, Sparkles, ChevronRight, ShoppingCart, TrendingUp, Tag } from 'lucide-react'
import { searchProducts, getEspStatus, getPathSuggestions } from '../../services/api'
import { useAppStore } from '../../store/useAppStore'

// ─── Store Layout Constants ───────────────────────────────────────────────────
// Physical layout (left → right):
//   [Corr-L] [A1-Left][A1-Right] [Corr-A1A2] [A2-Left][A2-Right] [Corr-A2A3] [A3-Left][A3-Right] [Corr-R]
//
// Which wall corridor accesses each side:
//   A1-Left  (P101–106) → Corr-L
//   A1-Right (P107–112) / A2-Left (P113–118) → Corr-A1A2
//   A2-Right (P119–124) / A3-Left (P125–130) → Corr-A2A3
//   A3-Right (P131–136) → Corr-R

const AISLE_CONFIG = [
  { id: 1, leftStart: 101, rightStart: 107 },
  { id: 2, leftStart: 113, rightStart: 119 },
  { id: 3, leftStart: 125, rightStart: 131 },
]
const PARTITIONS_PER_SIDE = 6

function getPartitionInfo(p) {
  if (!p) return null
  const n = parseInt(p)
  for (const a of AISLE_CONFIG) {
    if (n >= a.leftStart  && n < a.leftStart  + PARTITIONS_PER_SIDE)
      return { aisleId: a.id, side: 'Left',  indexInSide: n - a.leftStart  }
    if (n >= a.rightStart && n < a.rightStart + PARTITIONS_PER_SIDE)
      return { aisleId: a.id, side: 'Right', indexInSide: n - a.rightStart }
  }
  return null
}

function getAccessCorridor(p) {
  const n = parseInt(p)
  if (n >= 101 && n <= 106) return 'L'
  if (n >= 107 && n <= 118) return '12'
  if (n >= 119 && n <= 130) return '23'
  return 'R'
}

// ─── Build canvas geometry ────────────────────────────────────────────────────
function buildLayout(W, H) {
  const TOP    = 32   // aisle labels
  const BOT    = 72   // bottom corridor + ENTER space
  const PAD    = 12   // left/right padding
  const CORRW  = 26   // corridor column width

  const usableH = H - TOP - BOT
  const cellH   = usableH / PARTITIONS_PER_SIDE
  const stripW  = (W - 2 * PAD - 4 * CORRW) / 6

  // X positions of corridor left edges
  const corrL_x  = PAD
  const A1L_x    = corrL_x  + CORRW
  const A1R_x    = A1L_x   + stripW
  const corr12_x = A1R_x   + stripW
  const A2L_x    = corr12_x + CORRW
  const A2R_x    = A2L_x   + stripW
  const corr23_x = A2R_x   + stripW
  const A3L_x    = corr23_x + CORRW
  const A3R_x    = A3L_x   + stripW
  const corrR_x  = A3R_x   + stripW

  // Centre X of each corridor
  const corrCx = {
    L:  corrL_x  + CORRW / 2,
    12: corr12_x + CORRW / 2,
    23: corr23_x + CORRW / 2,
    R:  corrR_x  + CORRW / 2,
  }

  // Strip X lookup
  const stripX = {
    A1L: A1L_x, A1R: A1R_x,
    A2L: A2L_x, A2R: A2R_x,
    A3L: A3L_x, A3R: A3R_x,
  }

  // ENTER is centred at the bottom
  const enterX = W / 2
  const enterY = H - 18           // dot centre
  const botCorrY = H - BOT + 10   // horizontal corridor at bottom

  return { TOP, BOT, PAD, CORRW, stripW, cellH, usableH,
           corrL_x, corr12_x, corr23_x, corrR_x,
           corrCx, stripX, enterX, enterY, botCorrY }
}

// ─── Path points (corridor-only routing) ─────────────────────────────────────
function makePath(lay, info, partitionNo, currentPartition) {
  const { corrCx, TOP, cellH, enterX, enterY, botCorrY } = lay
  const corrKey = getAccessCorridor(partitionNo)
  const cx      = corrCx[corrKey]
  const rowCY   = TOP + info.indexInSide * cellH + cellH / 2

  if (currentPartition) {
    const pNum = parseInt(currentPartition.replace('P', ''))
    const sInfo = getPartitionInfo(pNum)
    if (sInfo) {
      const sCorr = getAccessCorridor(pNum)
      const sx = corrCx[sCorr]
      const sy = TOP + sInfo.indexInSide * cellH + cellH / 2
      
      if (sx === cx) {
        return [ { x: sx, y: sy }, { x: cx, y: rowCY } ]
      } else {
        return [ { x: sx, y: sy }, { x: sx, y: botCorrY }, { x: cx, y: botCorrY }, { x: cx, y: rowCY } ]
      }
    }
  }

  // ENTER → drop to bottom corridor → slide to the right corridor → climb up
  return [
    { x: enterX, y: enterY - 10 },  // from ENTER dot
    { x: enterX, y: botCorrY  },    // drop into bottom corridor
    { x: cx,     y: botCorrY  },    // slide sideways to corridor
    { x: cx,     y: rowCY     },    // climb up to row
  ]
}

// ─── Polyline utilities ───────────────────────────────────────────────────────
function polyLen(pts) {
  let d = 0
  for (let i = 0; i < pts.length - 1; i++) {
    const dx = pts[i+1].x - pts[i].x, dy = pts[i+1].y - pts[i].y
    d += Math.sqrt(dx*dx + dy*dy)
  }
  return d
}

function lerp(pts, t) {
  if (t <= 0) return { ...pts[0] }
  if (t >= 1) return { ...pts[pts.length-1] }
  const total = polyLen(pts)
  let rem = t * total
  for (let i = 0; i < pts.length - 1; i++) {
    const dx = pts[i+1].x-pts[i].x, dy = pts[i+1].y-pts[i].y
    const seg = Math.sqrt(dx*dx + dy*dy)
    if (rem <= seg) {
      const f = rem / seg
      return { x: pts[i].x + f*dx, y: pts[i].y + f*dy }
    }
    rem -= seg
  }
  return { ...pts[pts.length-1] }
}

function strokePoly(ctx, pts, t) {
  const total = polyLen(pts)
  let rem = t * total
  ctx.beginPath()
  ctx.moveTo(pts[0].x, pts[0].y)
  for (let i = 0; i < pts.length - 1; i++) {
    if (rem <= 0) break
    const dx = pts[i+1].x-pts[i].x, dy = pts[i+1].y-pts[i].y
    const seg = Math.sqrt(dx*dx + dy*dy)
    if (rem >= seg) { ctx.lineTo(pts[i+1].x, pts[i+1].y); rem -= seg }
    else { const f=rem/seg; ctx.lineTo(pts[i].x+f*dx, pts[i].y+f*dy); break }
  }
  ctx.stroke()
}

// ─── Main canvas draw ─────────────────────────────────────────────────────────
function drawMap(canvas, targetPartition, animT, pulseT, suggestions = [], currentPartition = null, userPos = null, targetedAds = []) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width, H = canvas.height
  ctx.clearRect(0, 0, W, H)

  // Reset context state
  ctx.globalAlpha = 1
  ctx.setLineDash([])
  ctx.shadowBlur = 0
  ctx.shadowColor = 'transparent'

  const lay = buildLayout(W, H)
  const { TOP, CORRW, stripW, cellH, usableH,
          corrL_x, corr12_x, corr23_x, corrR_x,
          corrCx, stripX, enterX, enterY, botCorrY } = lay

  const info    = targetPartition ? getPartitionInfo(targetPartition)   : null
  const corrKey = targetPartition ? getAccessCorridor(targetPartition)  : null

  // ── 1. Background ────────────────────────────────────────────────────
  ctx.fillStyle = '#f0f4ff'
  ctx.fillRect(0, 0, W, H)
  ctx.strokeStyle = '#c7d2fe'
  ctx.lineWidth = 1.5
  ctx.strokeRect(6, 6, W-12, H-12)

  // ── 2. Corridor columns ──────────────────────────────────────────────
  const corrDefs = [
    { x: corrL_x,  key: 'L'  },
    { x: corr12_x, key: '12' },
    { x: corr23_x, key: '23' },
    { x: corrR_x,  key: 'R'  },
  ]
  corrDefs.forEach(({ x, key }) => {
    const active = key === corrKey
    ctx.fillStyle = active ? 'rgba(99,102,241,0.10)' : 'rgba(255,255,255,0.6)'
    ctx.fillRect(x, TOP, CORRW, usableH)
    ctx.strokeStyle = active ? 'rgba(99,102,241,0.3)' : 'rgba(203,213,225,0.5)'
    ctx.lineWidth = active ? 1.5 : 0.8
    ctx.strokeRect(x, TOP, CORRW, usableH)
  })

  // ── 3. Aisle shelf strips ────────────────────────────────────────────
  const strips = [
    { k:'A1L', start:101 }, { k:'A1R', start:107 },
    { k:'A2L', start:113 }, { k:'A2R', start:119 },
    { k:'A3L', start:125 }, { k:'A3R', start:131 },
  ]

  // Aisle labels (once per aisle)
  ;[1,2,3].forEach(ai => {
    const cx = stripX[`A${ai}L`] + stripW
    ctx.fillStyle = '#818cf8'
    ctx.font = 'bold 10px Inter, system-ui, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(`A${ai}`, cx, TOP - 10)
  })

  strips.forEach(({ k, start }) => {
    const sx = stripX[k]
    for (let i = 0; i < PARTITIONS_PER_SIDE; i++) {
      const pno = start + i
      const cy  = TOP + i * cellH
      const isTgt = pno === targetPartition
      const isSugg = !isTgt && suggestions.some(s => parseInt(s.partition_no) === pno)
      const isAd = !isTgt && targetedAds.some(a => parseInt(a.partition_no) === pno)

      ctx.fillStyle = isTgt ? 'rgba(99,102,241,0.18)' : (i%2===0 ? '#eef2ff' : '#e8edfa')
      if (isSugg || isAd) ctx.fillStyle = 'rgba(245,158,11,0.1)' // faint amber for suggestions/ads
      
      ctx.beginPath()
      if (ctx.roundRect) ctx.roundRect(sx+1, cy+1, stripW-2, cellH-3, 4)
      else ctx.rect(sx+1, cy+1, stripW-2, cellH-3)
      ctx.fill()

      ctx.strokeStyle = isTgt ? '#6366f1' : ((isSugg || isAd) ? 'rgba(245,158,11,0.5)' : 'rgba(148,163,184,0.3)')
      ctx.lineWidth = isTgt || isSugg || isAd ? 2 : 0.7
      ctx.stroke()

      ctx.fillStyle = isTgt ? '#4338ca' : ((isSugg || isAd) ? '#d97706' : '#94a3b8')
      ctx.font = `${isTgt || isSugg || isAd ? 'bold' : 'normal'} 8px Inter, system-ui, sans-serif`
      ctx.textAlign = 'center'
      ctx.fillText(`P${pno}`, sx + stripW/2, cy + cellH/2 + 3)

      if (isSugg && !isAd) {
        // Draw small amber dot for suggestion
        ctx.beginPath()
        ctx.arc(sx + stripW/2 + 14, cy + cellH/2, 2.5, 0, Math.PI*2)
        ctx.fillStyle = '#f59e0b'
        ctx.fill()
      }

      if (isAd) {
        // Draw a star/tag for the targeted ad
        ctx.fillStyle = '#f59e0b'
        ctx.font = '10px sans-serif'
        ctx.fillText('★', sx + stripW/2 + 14, cy + cellH/2 + 3)
      }

      // Target pulsing halo
      if (isTgt && pulseT > 0) {
        ctx.beginPath()
        ctx.arc(sx + stripW/2, cy + cellH/2 - 5, 5 + pulseT*9, 0, Math.PI*2)
        ctx.fillStyle = `rgba(99,102,241,${0.35*(1-pulseT)})`
        ctx.fill()
      }
      if (isTgt) {
        ctx.beginPath()
        ctx.arc(sx + stripW/2, cy + cellH/2 - 5, 5, 0, Math.PI*2)
        ctx.fillStyle = '#6366f1'
        ctx.fill()
      }
    }
  })

  // Thin divider between each aisle's L/R strips
  ;[1,2,3].forEach(ai => {
    const dx = stripX[`A${ai}L`] + stripW
    ctx.strokeStyle = 'rgba(148,163,184,0.35)'
    ctx.lineWidth = 0.8
    ctx.setLineDash([3, 4])
    ctx.beginPath()
    ctx.moveTo(dx, TOP)
    ctx.lineTo(dx, TOP + usableH)
    ctx.stroke()
    ctx.setLineDash([])
  })

  // ── 4. Bottom corridor area ──────────────────────────────────────────
  ctx.fillStyle = 'rgba(99,102,241,0.03)'
  ctx.fillRect(6, TOP + usableH, W-12, H - TOP - usableH - 6)

  ctx.strokeStyle = 'rgba(148,163,184,0.4)'
  ctx.lineWidth = 1
  ctx.setLineDash([4, 5])
  ctx.beginPath()
  ctx.moveTo(10, botCorrY)
  ctx.lineTo(W-10, botCorrY)
  ctx.stroke()
  ctx.setLineDash([])

  // ── 5. User marker ──────────────────────────────────────────────────
  // Use pre-computed interpolated position passed in from component
  const userX = userPos ? userPos.x : enterX;
  const userY = userPos ? userPos.y : enterY;
  const userLabel = userPos ? 'YOU' : 'ENTER';

  // Outer ring (animated pulse)
  ctx.beginPath()
  ctx.arc(userX, userY, 13 + pulseT * 4, 0, Math.PI*2)
  ctx.fillStyle = `rgba(16,185,129,${0.25 * (1 - pulseT)})`
  ctx.fill()
  
  // Inner dot
  ctx.beginPath()
  ctx.arc(userX, userY, 8, 0, Math.PI*2)
  ctx.fillStyle = '#10b981'
  ctx.fill()
  
  // White centre
  ctx.beginPath()
  ctx.arc(userX, userY, 4, 0, Math.PI*2)
  ctx.fillStyle = '#fff'
  ctx.fill()
  
  // Label
  ctx.fillStyle = '#065f46'
  ctx.font = 'bold 10px Inter, system-ui, sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(userLabel, userX, userY + 20)

  // ── 6. Animated path ─────────────────────────────────────────────────
  if (info && animT > 0) {
    const pts = makePath(lay, info, targetPartition, currentPartition)

    // Glow halo
    ctx.strokeStyle = 'rgba(99,102,241,0.25)'
    ctx.lineWidth = 8
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    strokePoly(ctx, pts, animT)

    // Core dashed line
    ctx.strokeStyle = '#6366f1'
    ctx.lineWidth = 2.5
    ctx.setLineDash([9, 5])
    strokePoly(ctx, pts, animT)
    ctx.setLineDash([])

    // Moving dot along the path
    if (animT < 0.995) {
      const pos = lerp(pts, animT)
      // White outline
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, 8, 0, Math.PI*2)
      ctx.fillStyle = '#fff'
      ctx.fill()
      // Indigo fill
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, 5.5, 0, Math.PI*2)
      ctx.fillStyle = '#6366f1'
      ctx.fill()
    }
  }
}

// ─── Component ────────────────────────────────────────────────────────────────
export default function LiveNavigationModal({ open, onOpenChange, productName }) {
  const canvasRef = useRef(null)
  const user = useAppStore(state => state.user)
  const [locationData, setLocationData] = useState(null)
  const [loading, setLoading]   = useState(false)
  const [espPos,   setEspPos]   = useState('Scanning...')
  const [suggestions, setSuggestions] = useState([])
  const [targetedAds, setTargetedAds] = useState([])
  const addToCart = useAppStore(state => state.addToCart)
  const animRef   = useRef(null)
  const pollRef   = useRef(null)
  const stateRef  = useRef({ animT: 0, pulseT: 0, pulsing: false, currentPartition: null, userX: undefined, userY: undefined, suggs: [], ads: [] })

  const startAnim = useCallback((partitionNo) => {
    if (animRef.current) cancelAnimationFrame(animRef.current)
    const curP = stateRef.current?.currentPartition
    const prevUserX = stateRef.current?.userX
    const prevUserY = stateRef.current?.userY
    const curSuggs = stateRef.current?.suggs || []
    const curAds = stateRef.current?.ads || []
    stateRef.current = { animT: 0, pulseT: 0, pulsing: false, currentPartition: curP, userX: prevUserX, userY: prevUserY, suggs: curSuggs, ads: curAds }
    let last = null
    const tick = (ts) => {
      if (!last) last = ts
      const dt = Math.min((ts - last) / 1000, 0.05)
      last = ts
      const s = stateRef.current
      if (!s.pulsing) {
        s.animT = Math.min(s.animT + dt * 0.9, 1)
        if (s.animT >= 1) s.pulsing = true
      } else {
        s.pulseT = (s.pulseT + dt * 1.8) % 1
      }

      // Compute target user position from currentPartition
      const canvas = canvasRef.current
      if (canvas) {
        const lay = buildLayout(canvas.width, canvas.height)
        let targetUX = lay.enterX
        let targetUY = lay.enterY
        if (s.currentPartition) {
          const pn = parseInt(s.currentPartition.replace('P', ''))
          const si = getPartitionInfo(pn)
          if (si) {
            const sc = getAccessCorridor(pn)
            targetUX = lay.corrCx[sc]
            targetUY = lay.TOP + si.indexInSide * lay.cellH + lay.cellH / 2
          }
        }
        if (s.userX === undefined) { s.userX = targetUX; s.userY = targetUY }
        s.userX += (targetUX - s.userX) * 0.08
        s.userY += (targetUY - s.userY) * 0.08
      }

      const userPos = s.userX !== undefined ? { x: s.userX, y: s.userY } : null
      drawMap(canvasRef.current, partitionNo, s.animT, s.pulseT, s.suggs, s.currentPartition, userPos, s.ads)
      animRef.current = requestAnimationFrame(tick)
    }
    animRef.current = requestAnimationFrame(tick)
  }, [])

  // Draw initial empty map whenever the modal opens
  useEffect(() => {
    if (open) {
      const id = setTimeout(() => {
        const s = stateRef.current
        const userPos = s.userX !== undefined ? { x: s.userX, y: s.userY } : null
        drawMap(canvasRef.current, null, 0, 0, [], s?.currentPartition, userPos)
      }, 30)
      return () => clearTimeout(id)
    }
  }, [open])

  useEffect(() => {
    if (!open || !productName) return
    setLocationData(null)
    setSuggestions([])
    setTargetedAds([])
    setLoading(true)
    const curP = stateRef.current?.currentPartition
    stateRef.current = { animT: 0, pulseT: 0, pulsing: false, currentPartition: curP, suggs: [], ads: [] }

    searchProducts(productName).then(({ data }) => {
      const results = Array.isArray(data) ? data : (data?.results || [])
      const product = results.find(r =>
        r.name?.toLowerCase().includes(productName.toLowerCase())
      ) || results[0]

      if (product?.partition_no) {
        const pno = parseInt(product.partition_no)
        const loc = {
          aisle:        product.aisle,
          partition_no: pno,
          position_tag: product.position_tag || `P${pno}`,
          side:         product.side,
        }
        setLocationData(loc)
        setLoading(false)

        // Fetch targeted ads (Market Basket Analysis)
        fetch('http://127.0.0.1:5000/api/nav/targeted-ad', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_name: productName, category: product.category || '' })
        }).then(r => r.json()).then(d => {
          if (d?.ads?.length) {
            setTargetedAds(d.ads)
            stateRef.current.ads = d.ads
          }
        }).catch(() => {})
        
        // Fetch path suggestions if user is logged in
        if (user?.customer_id) {
          getPathSuggestions(user.customer_id, pno).then(({ data: suggs }) => {
            if (Array.isArray(suggs) && suggs.length > 0) {
              setSuggestions(suggs)
              stateRef.current.suggs = suggs
              startAnim(pno)
            } else {
              startAnim(pno)
            }
          }).catch(() => startAnim(pno))
        } else {
          startAnim(pno)
        }
      } else {
        setLocationData(product?.aisle ? { aisle: product.aisle } : null)
        setLoading(false)
        setTimeout(() => drawMap(canvasRef.current, null, 1, 0, [], stateRef.current?.currentPartition), 60)
      }
    })

    const poll = () => getEspStatus().then(({ data }) => {
      if (data?.position) setEspPos(data.position)
      if (data?.partition) {
        stateRef.current.currentPartition = data.partition
        // If no animation is running (no product searched yet), redraw the idle map with updated position
        if (!animRef.current) {
          const s = stateRef.current
          // Compute new target
          const canvas = canvasRef.current
          if (canvas) {
            const lay = buildLayout(canvas.width, canvas.height)
            const pn = parseInt(data.partition.replace('P', ''))
            const si = getPartitionInfo(pn)
            let targetUX = lay.enterX, targetUY = lay.enterY
            if (si) {
              const sc = getAccessCorridor(pn)
              targetUX = lay.corrCx[sc]
              targetUY = lay.TOP + si.indexInSide * lay.cellH + lay.cellH / 2
            }
            if (s.userX === undefined) { s.userX = targetUX; s.userY = targetUY }
            s.userX += (targetUX - s.userX) * 0.5
            s.userY += (targetUY - s.userY) * 0.5
            const userPos = { x: s.userX, y: s.userY }
            drawMap(canvas, null, 0, s.pulseT || 0, s.suggs, s.currentPartition, userPos, s.ads)
          }
        }
      }
    })
    poll()
    pollRef.current = setInterval(poll, 1500)

    return () => {
      clearInterval(pollRef.current)
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [open, productName, startAnim])

  const info    = locationData?.partition_no ? getPartitionInfo(locationData.partition_no)  : null
  const corr    = locationData?.partition_no ? getAccessCorridor(locationData.partition_no) : null
  const corrLbl = { L: 'Left Wall', '12': 'A1 – A2', '23': 'A2 – A3', R: 'Right Wall' }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[200] flex items-center justify-center p-4"
          onClick={(e) => e.target === e.currentTarget && onOpenChange(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 24 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 24 }}
            transition={{ type: 'spring', damping: 22, stiffness: 280 }}
            className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-indigo-50 rounded-xl">
                  <Navigation2 size={20} className="text-indigo-500" />
                </div>
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">Live Navigation</h2>
                  <p className="text-xs text-slate-400">Follow the path to your product</p>
                </div>
              </div>
              <button onClick={() => onOpenChange(false)} className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400">
                <X size={18} />
              </button>
            </div>

            {/* Status bar */}
            <div className="grid grid-cols-4 border-b border-slate-100 bg-slate-50 text-center divide-x divide-slate-100">
              <div className="px-3 py-2.5">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Product</p>
                <p className="font-extrabold text-indigo-600 text-xs truncate">{productName}</p>
              </div>
              <div className="px-3 py-2.5">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Your Location</p>
                <div className="flex items-center justify-center gap-1">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                  <p className="font-bold text-slate-700 text-xs">{espPos}</p>
                </div>
              </div>
              <div className="px-3 py-2.5">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Aisle · Partition</p>
                <p className="font-extrabold text-red-500 text-xs flex items-center justify-center gap-1">
                  <MapPin size={10} />
                  {locationData?.partition_no ? `A${locationData.aisle} · ${locationData.position_tag}` : '—'}
                </p>
              </div>
              <div className="px-3 py-2.5">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Via Corridor</p>
                <p className="font-extrabold text-indigo-500 text-xs">{corr ? corrLbl[corr] : '—'}</p>
              </div>
            </div>

            {/* Scrollable Body */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden p-5">
              
              {/* Canvas — always mounted */}
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 shadow-sm">
                <canvas ref={canvasRef} width={600} height={350} className="w-full block" />
                
                {/* Suggestions Overlay */}
                <AnimatePresence>
                  {suggestions.length > 0 && !loading && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 }}
                      className="absolute top-4 right-4 max-w-[200px] flex flex-col gap-2"
                    >
                      <div className="bg-amber-100/90 text-amber-800 text-[10px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full w-max flex items-center gap-1.5 shadow-sm backdrop-blur-md border border-amber-200/50">
                        <Sparkles size={12} className="text-amber-500" />
                        On Your Way
                      </div>
                      <div className="flex flex-col gap-1.5">
                        {suggestions.map((s, idx) => (
                          <div key={idx} className="bg-white/95 backdrop-blur-md border border-slate-200 p-2.5 rounded-xl shadow-lg shadow-slate-900/5 flex items-start gap-2 group cursor-pointer hover:border-amber-300 hover:bg-amber-50/50 transition-colors">
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-bold text-slate-800 truncate">{s.name}</p>
                              <p className="text-[10px] text-slate-500 mt-0.5 font-medium flex items-center gap-1">
                                P{s.partition_no} <span className="text-slate-300">•</span> ₹{s.price}
                              </p>
                            </div>
                            <div className="shrink-0 w-6 h-6 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600 group-hover:bg-amber-500 group-hover:text-white transition-colors">
                              <ChevronRight size={14} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {loading && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-white/90 rounded-2xl">
                    <Loader2 size={28} className="animate-spin text-indigo-500" />
                    <p className="text-sm font-medium text-slate-400">Locating product…</p>
                  </div>
                )}
                {!loading && !locationData && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <p className="text-xs text-slate-400 bg-white/90 px-3 py-1.5 rounded-lg shadow-sm">
                      Product location not found.
                    </p>
                  </div>
                )}
              </div>

              {/* Targeted MBA Ads */}
            <AnimatePresence>
              {targetedAds.length > 0 && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="px-5 pb-5"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg">
                      <TrendingUp size={13} className="text-white" />
                    </div>
                    <div>
                      <p className="text-xs font-extrabold text-slate-800">Smart Suggestions</p>
                      <p className="text-[10px] text-slate-400">Based on Market Basket Analysis</p>
                    </div>
                    <div className="ml-auto px-2 py-0.5 bg-amber-50 border border-amber-200 rounded-full">
                      <p className="text-[9px] font-bold text-amber-700">MBA Engine</p>
                    </div>
                  </div>

                  <div className="grid gap-2">
                    {targetedAds.map((ad, idx) => (
                      <motion.div
                        key={ad.barcode}
                        initial={{ opacity: 0, x: -12 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + idx * 0.15 }}
                        className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/70 rounded-xl p-3 flex items-center gap-3 group hover:border-amber-400 hover:shadow-lg hover:shadow-amber-500/10 transition-all"
                      >
                        <div className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white shadow-md shadow-amber-500/30">
                          <Tag size={18} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-extrabold text-slate-800 truncate">{ad.name}</p>
                          <p className="text-[10px] text-amber-700 font-semibold mt-0.5">{ad.tagline}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] font-bold text-slate-500">₹{ad.price}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-[10px] text-slate-400">A{ad.aisle} · {ad.position_tag}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-[9px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                              {Math.round(ad.confidence * 100)}% match
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => addToCart?.({ barcode: ad.barcode, name: ad.name, price: ad.price, quantity: 1 })}
                          className="shrink-0 p-2 rounded-xl bg-white border border-amber-200 text-amber-600 hover:bg-amber-500 hover:text-white hover:border-amber-500 transition-all shadow-sm"
                          title="Add to cart"
                        >
                          <ShoppingCart size={14} />
                        </button>
                      </motion.div>
                    ))}
                  </div>

                  <p className="text-[9px] text-slate-400 text-center mt-2 italic">
                    Powered by association rule mining · {targetedAds.length} complementary products found
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            </div> {/* End Scrollable Body */}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
