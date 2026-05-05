import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Radio, Zap, Save, RotateCcw, CheckCircle, AlertCircle,
  ChevronRight, Activity, Wifi, WifiOff, ArrowLeft, Settings,
  Shield, MapPin, BarChart2, Users, Sliders, RefreshCw
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { getCalibStatus, captureSignal, saveCalibration, getEspStatus, getTrackerConfig, updateTrackerConfig } from '../services/api'
import { useToast } from '../hooks/useToast'
import { useAppStore } from '../store/useAppStore'

// ── Helpers ──────────────────────────────────────────────────────────────────
const CORRIDORS = ['L', '12', '23', 'R']
const CORR_LABELS = { L: 'Left Corridor', '12': 'Aisle 1–2', '23': 'Aisle 2–3', R: 'Right Corridor' }
const POSITIONS = ['start', 'middle', 'end']
const POS_LABELS = { start: 'Start (Nearest to ESP)', middle: 'Middle', end: 'End (Farthest from ESP)' }
const ESP_NAMES = ['ESP32_AISLE_1', 'ESP32_AISLE_2', 'ESP32_AISLE_3', 'ESP32_AISLE_4']
const ESP_SHORT = { ESP32_AISLE_1: 'A1 – Left Wall', ESP32_AISLE_2: 'A1–A2 Gap', ESP32_AISLE_3: 'A2–A3 Gap', ESP32_AISLE_4: 'A4 – Right Wall' }

// ── Sub-components ────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color = 'indigo' }) {
  const colors = {
    indigo: 'bg-indigo-50 text-indigo-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
  }
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 flex items-center gap-4 shadow-sm">
      <div className={`p-3 rounded-xl ${colors[color]}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{label}</p>
        <p className="text-xl font-extrabold text-slate-900 mt-0.5">{value}</p>
      </div>
    </div>
  )
}

function EspSignalBar({ name, rssi }) {
  const strength = rssi ? Math.max(0, Math.min(100, ((rssi + 100) / 60) * 100)) : 0
  const color = strength > 60 ? 'bg-emerald-500' : strength > 30 ? 'bg-amber-500' : 'bg-rose-500'
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs font-bold text-slate-500 w-32 shrink-0">{name.replace('ESP32_', '')}</span>
      <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${strength}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
      <span className="text-xs font-mono text-slate-600 w-16 text-right">
        {rssi ? `${rssi} dBm` : '—'}
      </span>
    </div>
  )
}

// ── ESP Live Monitor ──────────────────────────────────────────────────────────
function EspMonitor() {
  const [espData, setEspData] = useState(null)
  const [connected, setConnected] = useState(false)
  const pollRef = useRef(null)

  useEffect(() => {
    const poll = () => getEspStatus().then(({ data }) => {
      if (data) { setEspData(data); setConnected(true) }
      else setConnected(false)
    }).catch(() => setConnected(false))
    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => clearInterval(pollRef.current)
  }, [])

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="font-extrabold text-slate-900">Live ESP32 Monitor</h3>
          <p className="text-xs text-slate-400 mt-0.5">Real-time beacon signal strengths</p>
        </div>
        <div className={`flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-full ${
          connected ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-600'
        }`}>
          {connected ? <Wifi size={12}/> : <WifiOff size={12}/>}
          {connected ? 'Connected' : 'Offline'}
        </div>
      </div>

      <div className="space-y-3">
        {espData?.all_smoothed
          ? Object.entries(espData.all_smoothed).map(([name, rssi]) => (
              <EspSignalBar key={name} name={name} rssi={rssi} />
            ))
          : ESP_NAMES.map(n => <EspSignalBar key={n} name={n} rssi={null} />)
        }
      </div>

      {espData && (
        <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-3 gap-3 text-center">
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active ESP</p>
            <p className="font-bold text-indigo-600 text-sm mt-0.5">{espData.esp?.replace('ESP32_', '') || '—'}</p>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Corridor</p>
            <p className="font-bold text-slate-900 text-sm mt-0.5">{CORR_LABELS[espData.corridor] || espData.corridor || '—'}</p>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Distance</p>
            <p className="font-bold text-emerald-600 text-sm mt-0.5">{espData.distance_m ? `${espData.distance_m}m` : '—'}</p>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Tracker Config Panel ─────────────────────────────────────────────────────
function TrackerConfigPanel() {
  const { toast } = useToast()
  const [cfg, setCfg] = useState(null)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    getTrackerConfig().then(({ data, error }) => {
      if (data) setCfg({ ...data })
      else toast(error?.message || 'Could not load config', 'error')
      setLoading(false)
    })
  }

  useEffect(() => { load() }, [])

  const setTxPower = (esp, val) => setCfg(c => ({ ...c, tx_power: { ...c.tx_power, [esp]: parseFloat(val) } }))
  const setField   = (key, val) => setCfg(c => ({ ...c, [key]: parseFloat(val) }))

  const handleSave = async () => {
    setSaving(true)
    const { data, error } = await updateTrackerConfig(cfg)
    if (data?.success) toast(`Updated: ${data.updated.join(', ')}`, 'success')
    else toast(error?.message || 'Save failed', 'error')
    setSaving(false)
  }

  if (loading || !cfg) return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex items-center justify-center h-40">
      <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-indigo-500" />
    </div>
  )

  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 className="font-extrabold text-slate-900 flex items-center gap-2"><Sliders size={16} className="text-indigo-500"/>Tracker Parameters</h3>
          <p className="text-xs text-slate-400 mt-0.5">Tune live — no restart needed</p>
        </div>
        <button onClick={load} className="p-2 hover:bg-slate-100 rounded-xl text-slate-400 transition-colors"><RefreshCw size={15}/></button>
      </div>

      <div className="p-6 space-y-6">
        {/* tx_power per beacon */}
        <div>
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">TX Power at 1 m (dBm) per Beacon</p>
          <div className="grid grid-cols-1 gap-3">
            {ESP_NAMES.map(name => (
              <div key={name} className="flex items-center gap-3">
                <div className="flex-1">
                  <p className="text-xs font-bold text-slate-700">{ESP_SHORT[name]}</p>
                  <p className="text-[10px] text-slate-400">{name}</p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="range" min="-100" max="-30" step="1"
                    value={cfg.tx_power?.[name] ?? -82}
                    onChange={e => setTxPower(name, e.target.value)}
                    className="w-28 accent-indigo-500"
                  />
                  <input
                    type="number" min="-100" max="-30"
                    value={cfg.tx_power?.[name] ?? -82}
                    onChange={e => setTxPower(name, e.target.value)}
                    className="w-20 text-center text-sm font-mono font-bold border border-slate-200 rounded-lg py-1 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                  <span className="text-xs text-slate-400 w-8">dBm</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 p-3 bg-indigo-50 rounded-xl border border-indigo-100">
            <p className="text-[11px] text-indigo-700 font-medium">
              💡 <strong>How to measure:</strong> Stand <strong>exactly 1 meter</strong> from a beacon and run
              <code className="bg-indigo-100 px-1 rounded mx-1">python calibrate_esp32.py</code>.
              Use the averaged dBm reading for that beacon.
            </p>
          </div>
        </div>

        {/* Walkway length */}
        <div>
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Corridor / Walkway Length</p>
          <div className="flex items-center gap-3">
            <input
              type="range" min="0.5" max="3" step="0.25"
              value={cfg.walkway_length_m}
              onChange={e => setField('walkway_length_m', e.target.value)}
              className="flex-1 accent-indigo-500"
            />
            <input
              type="number" min="0.5" max="3" step="0.25"
              value={cfg.walkway_length_m}
              onChange={e => setField('walkway_length_m', e.target.value)}
              className="w-20 text-center text-sm font-mono font-bold border border-slate-200 rounded-lg py-1 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
            <span className="text-xs text-slate-400 w-4">m</span>
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 mt-1 px-1">
            <span>0.5 m (desk demo)</span><span>1.5 m (classroom)</span><span>3 m (small store)</span>
          </div>
          <div className="mt-2 p-2.5 bg-amber-50 border border-amber-100 rounded-xl">
            <p className="text-[11px] text-amber-800 font-medium">
              🏫 <strong>Classroom setup:</strong> Set to <strong>1.5 m</strong> with beacons spaced <strong>0.5 m apart</strong>
            </p>
          </div>
        </div>

        {/* Advanced */}
        <details className="group">
          <summary className="cursor-pointer text-xs font-bold text-slate-500 uppercase tracking-widest select-none group-open:text-indigo-600">Advanced Parameters ▾</summary>
          <div className="mt-3 space-y-3">
            {[
              { key: 'n_path_loss', label: 'Path Loss Exponent (n)', min: 1, max: 6, step: 0.1, hint: '2 = free space · 3–4 = indoor typical' },
              { key: 'ema_alpha', label: 'EMA Smoothing α', min: 0.01, max: 1, step: 0.01, hint: 'Lower = smoother but slower to react' },
              { key: 'hysteresis_threshold', label: 'Hysteresis Threshold (dBm)', min: 0, max: 20, step: 0.5, hint: 'Min signal lead before switching corridor' },
            ].map(({ key, label, min, max, step, hint }) => (
              <div key={key}>
                <p className="text-xs font-bold text-slate-700 mb-1">{label}</p>
                <div className="flex items-center gap-3">
                  <input type="range" min={min} max={max} step={step} value={cfg[key] ?? 0}
                    onChange={e => setField(key, e.target.value)} className="flex-1 accent-indigo-500" />
                  <input type="number" min={min} max={max} step={step} value={cfg[key] ?? 0}
                    onChange={e => setField(key, e.target.value)}
                    className="w-20 text-center text-sm font-mono font-bold border border-slate-200 rounded-lg py-1 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                </div>
                <p className="text-[10px] text-slate-400 mt-0.5">{hint}</p>
              </div>
            ))}
          </div>
        </details>

        <button onClick={handleSave} disabled={saving}
          className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm flex items-center justify-center gap-2 transition-colors shadow-lg shadow-indigo-500/20 disabled:opacity-60">
          {saving ? <><div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"/>Saving...</> : <><Save size={15}/>Apply to Live Tracker</>}
        </button>
      </div>
    </div>
  )
}

// ── Calibration Wizard ────────────────────────────────────────────────────────
function CalibrationWizard({ onDone }) {
  const { toast } = useToast()
  const [fingerprint, setFingerprint] = useState({})
  const [corrIdx, setCorrIdx] = useState(0)
  const [posIdx, setPosIdx]   = useState(0)
  const [capturing, setCapturing] = useState(false)
  const [countdown, setCountdown] = useState(7)
  const [lastRssi, setLastRssi]   = useState(null)
  const [done, setDone] = useState(false)
  const [saving, setSaving] = useState(false)
  const timerRef = useRef(null)

  const corr = CORRIDORS[corrIdx]
  const pos  = POSITIONS[posIdx]
  const totalSteps = CORRIDORS.length * POSITIONS.length
  const doneSteps  = corrIdx * POSITIONS.length + posIdx
  const progress   = Math.round((doneSteps / totalSteps) * 100)
  const isCaptured = (ci, pi) => !!(fingerprint[CORRIDORS[ci]]?.[POSITIONS[pi]])

  const capture = async () => {
    setCapturing(true)
    setCountdown(7)
    timerRef.current = setInterval(() => setCountdown(c => Math.max(0, c - 1)), 1000)
    const { data, error } = await captureSignal(corr, pos.toUpperCase())
    clearInterval(timerRef.current)
    setCapturing(false)
    setCountdown(7)
    if (data?.rssi) {
      setLastRssi(data.rssi)
      setFingerprint(prev => ({ ...prev, [corr]: { ...(prev[corr] || {}), [pos]: data.rssi } }))
      toast(`Saved: ${CORR_LABELS[corr]} – ${POS_LABELS[pos]}`, 'success')
      advance()
    } else {
      toast(`No signal. ${error?.message || 'Are ESP32s powered on?'}`, 'error')
    }
  }

  const advance = () => {
    if (posIdx < POSITIONS.length - 1) { setPosIdx(p => p + 1) }
    else if (corrIdx < CORRIDORS.length - 1) { setCorrIdx(c => c + 1); setPosIdx(0) }
    else { setDone(true) }
  }

  const handleSave = async () => {
    setSaving(true)
    const { error } = await saveCalibration({ corridors: fingerprint })
    setSaving(false)
    if (!error) { toast('Calibration saved!', 'success'); onDone() }
    else toast('Save failed — check backend', 'error')
  }

  // Visual top-down store map
  const corridorCX = { L: 42, '12': 147, '23': 247, R: 347 }
  const positionCY = { start: 35, middle: 80, end: 125 }

  const StoreMap = () => (
    <svg viewBox="0 0 390 190" className="w-full" style={{ maxHeight: 190 }}>
      {/* Store boundary */}
      <rect x="10" y="35" width="370" height="140" rx="8" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="1.5"/>

      {/* The physical table edge / wall where ESPs are mounted */}
      <rect x="10" y="20" width="370" height="15" fill="#e2e8f0" stroke="#cbd5e1" strokeWidth="1.5"/>
      <text x="195" y="30" textAnchor="middle" fontSize="7" fill="#64748b" fontWeight="black" letterSpacing="2">PHYSICAL TABLE EDGE / ENTRANCE WALL</text>

      {/* ENTRANCE arrow */}
      <rect x="10" y="2" width="90" height="14" rx="4" fill="#22c55e"/>
      <text x="55" y="12" textAnchor="middle" fontSize="7" fill="white" fontWeight="black">▼ START HERE</text>

      {/* Shelf blocks */}
      {[85, 185, 285].map((x,i) => (
        <g key={x}>
          <rect x={x} y="45" width="40" height="115" rx="4" fill="#f1f5f9" stroke="#cbd5e1" strokeWidth="1"/>
          <text x={x+20} y="105" textAnchor="middle" fontSize="8" fill="#94a3b8" fontWeight="bold">Shelf {i+1}</text>
        </g>
      ))}

      {/* Corridor labels at bottom */}
      {[{x:42,label:'L'},{x:147,label:'12'},{x:247,label:'23'},{x:347,label:'R'}].map(({x,label}) => (
        <text key={label} x={x} y="185" textAnchor="middle" fontSize="9" fill="#94a3b8" fontWeight="black">{label}</text>
      ))}

      {/* ESP32 beacons — placed exactly on the table edge */}
      {[42,147,247,347].map((x,i) => (
        <g key={i}>
          {/* Explicit ESP32 text label pointing to the board */}
          <rect x={x-12} y="11" width="24" height="9" rx="2" fill="#cbd5e1" opacity="0.8"/>
          <text x={x} y="18" textAnchor="middle" fontSize="5.5" fill="#0f172a" fontWeight="black">ESP32</text>
          
          {/* ESP board representation */}
          <rect x={x-14} y="22" width="28" height="16" rx="2" fill="#1e1b4b"/>
          <circle cx={x-8} cy={30} r="2" fill="#ef4444"/> {/* Little red power LED */}
          <text x={x+4} y="32" textAnchor="middle" fontSize="8" fill="white" fontWeight="bold">A{i+1}</text>
        </g>
      ))}

      {/* 0.5m spacing labels between beacons */}
      {[94,194,294].map(x => (
        <g key={x}>
          <line x1={x-15} y1="28" x2={x+15} y2="28" stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="2,2"/>
          <text x={x} y="24" textAnchor="middle" fontSize="7" fill="#b45309" fontWeight="black">0.5m gap</text>
        </g>
      ))}

      {/* Corridor highlight */}
      {!done && (
        <rect x={corridorCX[corr]-30} y="36" width="55" height="124" rx="4" fill="#6366f1" opacity="0.12"/>
      )}

      {/* Captured green dots */}
      {CORRIDORS.map(c => POSITIONS.map(p =>
        fingerprint[c]?.[p]
          ? <circle key={`${c}-${p}`} cx={corridorCX[c]} cy={positionCY[p]+8} r="5" fill="#10b981" opacity="0.8"/>
          : null
      ))}

      {/* YOU dot */}
      {!done && (
        <g>
          <circle cx={corridorCX[corr]} cy={positionCY[pos]+8} r="10" fill="#6366f1" opacity="0.25"/>
          <circle cx={corridorCX[corr]} cy={positionCY[pos]+8} r="7" fill="#6366f1"/>
          <text x={corridorCX[corr]} y={positionCY[pos]+11} textAnchor="middle" fontSize="6" fill="white" fontWeight="black">YOU</text>
        </g>
      )}
    </svg>
  )

  // Review/done screen
  if (done) return (
    <motion.div initial={{ opacity:0,y:16 }} animate={{ opacity:1,y:0 }}
      className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="bg-emerald-600 px-5 py-4 text-white">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-white/20 rounded-xl"><CheckCircle size={20}/></div>
          <div>
            <h3 className="font-extrabold">All {totalSteps} Points Captured!</h3>
            <p className="text-emerald-100 text-xs">Review below, then save to activate</p>
          </div>
        </div>
        <div className="bg-white/10 rounded-xl p-2"><StoreMap /></div>
      </div>
      <div className="p-5">
        <div className="grid grid-cols-2 gap-2 mb-4">
          {CORRIDORS.map(c => (
            <div key={c} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
              <p className="font-extrabold text-indigo-600 text-xs mb-1">{CORR_LABELS[c]}</p>
              {POSITIONS.map(p => {
                const rssiMap = fingerprint[c]?.[p] || {}
                return (
                  <div key={p} className="mb-1">
                    <p className="text-[9px] font-black text-slate-400 uppercase">{p}</p>
                    <div className="flex gap-1 flex-wrap">
                      {ESP_NAMES.map(e => (
                        <span key={e} className="text-[9px] font-mono bg-slate-200 px-1 rounded">
                          A{e.slice(-1)}:{rssiMap[e]??'—'}
                        </span>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
        <div className="flex gap-3">
          <button onClick={() => { setDone(false); setCorrIdx(0); setPosIdx(0); setFingerprint({}) }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-bold text-sm hover:bg-slate-50">
            <RotateCcw size={13}/> Redo
          </button>
          <button onClick={handleSave} disabled={saving}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-sm hover:bg-indigo-700 shadow-lg shadow-indigo-500/20 disabled:opacity-60">
            {saving ? <><div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"/>Saving...</> : <><Save size={13}/>Activate Calibration</>}
          </button>
        </div>
      </div>
    </motion.div>
  )

  // Active step UI
  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="h-1.5 bg-slate-100">
        <motion.div className="h-full bg-indigo-500" animate={{ width: `${progress}%` }} transition={{ duration: 0.4 }}/>
      </div>
      <div className="p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-black tracking-widest text-indigo-500 uppercase">Step {doneSteps+1} of {totalSteps}</p>
            <h3 className="text-base font-extrabold text-slate-900 mt-0.5">
              {CORR_LABELS[corr]} — <span className="text-indigo-600">{POS_LABELS[pos]}</span>
            </h3>
          </div>
          <div className="bg-indigo-50 px-3 py-1.5 rounded-xl text-center">
            <p className="text-[9px] font-bold text-indigo-400">CORRIDOR</p>
            <p className="font-black text-xl text-indigo-700">{corr}</p>
          </div>
        </div>

        {/* Store map */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100">
          <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">
            Move to the <span className="text-indigo-600">blue dot</span> on the map
          </p>
          <StoreMap />
        </div>

        {/* Step checklist grid */}
        <div className="grid grid-cols-4 gap-1">
          {CORRIDORS.map((c, ci) => (
            <div key={c}>
              <p className="text-[8px] font-black text-slate-400 text-center uppercase mb-1">{c}</p>
              {POSITIONS.map((p, pi) => {
                const captured = isCaptured(ci, pi)
                const active = ci === corrIdx && pi === posIdx
                return (
                  <div key={p} className={`h-5 rounded mb-0.5 flex items-center justify-center text-[8px] font-bold transition-all ${
                    captured ? 'bg-emerald-500 text-white' :
                    active   ? 'bg-indigo-600 text-white' :
                               'bg-slate-100 text-slate-400'
                  }`}>
                    {captured ? '✓' : active ? '→' : p[0].toUpperCase()}
                  </div>
                )
              })}
            </div>
          ))}
        </div>

        {/* Instructions */}
        <div className="bg-indigo-50 rounded-xl p-3 border border-indigo-100">
          <p className="font-bold text-indigo-900 text-xs mb-1">How to walk the grid:</p>
          <ol className="text-xs text-indigo-800 space-y-0.5 list-decimal list-inside">
            <li><strong>Start:</strong> Stand directly in front of the ESP32 (0m away)</li>
            <li><strong>Middle:</strong> Take 1 large step back from the ESP32 (0.75m away)</li>
            <li><strong>End:</strong> Take 2 large steps back from the ESP32 (1.5m away)</li>
            <li>Hold device at waist height, face the ESP32, and press Capture</li>
          </ol>
        </div>

        {/* Capture controls */}
        <div className="bg-slate-900 rounded-xl p-4 flex items-center gap-4">
          <div className="text-center shrink-0 w-14">
            <div className={`text-4xl font-black font-mono tabular-nums ${capturing ? 'text-indigo-300' : 'text-slate-600'}`}>
              {capturing ? countdown : '7'}
            </div>
            <p className="text-slate-500 text-[9px] mt-0.5">seconds</p>
          </div>
          <div className="flex-1 space-y-2">
            <button onClick={capture} disabled={capturing}
              className={`w-full py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                capturing ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-xl shadow-indigo-900/40'
              }`}>
              <Zap size={15}/>{capturing ? 'Scanning… stay still!' : 'Capture Signal'}
            </button>
            <button onClick={advance} disabled={capturing}
              className="w-full text-[11px] text-slate-500 hover:text-slate-300 transition-colors text-center">
              Skip this point →
            </button>
          </div>
        </div>

        {/* Last capture signal bars */}
        {lastRssi && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
            <p className="text-xs font-bold text-emerald-700 mb-2">Last capture — signal readings:</p>
            <div className="space-y-1.5">
              {ESP_NAMES.map(name => {
                const val = lastRssi[name]
                const pct = val ? Math.max(0, Math.min(100, ((val + 100) / 60) * 100)) : 0
                return (
                  <div key={name} className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-emerald-700 w-8">{name.replace('ESP32_AISLE_','A')}</span>
                    <div className="flex-1 h-1.5 bg-emerald-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${pct}%` }}/>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-900 w-14 text-right">{val ? `${val} dBm` : '—'}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main AdminPage ────────────────────────────────────────────────────────────
export default function AdminPage() {
  const user = useAppStore(state => state.user)
  const [calibStatus, setCalibStatus] = useState(null)
  const [showWizard, setShowWizard] = useState(false)

  useEffect(() => {
    getCalibStatus().then(({ data }) => setCalibStatus(data))
  }, [])

  const handleWizardDone = () => {
    setShowWizard(false)
    getCalibStatus().then(({ data }) => setCalibStatus(data))
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400">
              <ArrowLeft size={18}/>
            </Link>
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-indigo-600 rounded-xl">
                <Shield size={18} className="text-white"/>
              </div>
              <div>
                <h1 className="font-extrabold text-slate-900 text-base">Admin Panel</h1>
                <p className="text-[11px] text-slate-400">SmartRetailX System Control</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
            <div className="w-2 h-2 bg-emerald-500 rounded-full"/>
            {user?.name || 'Admin'}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Radio} label="ESP Beacons" value="4 Active" color="indigo"/>
          <StatCard icon={Activity} label="Calibration" value={calibStatus?.calibrated ? '✓ Done' : 'Pending'} color={calibStatus?.calibrated ? 'emerald' : 'amber'}/>
          <StatCard icon={MapPin} label="Corridors" value={`${calibStatus?.corridor_count ?? 0} / 4`} color="indigo"/>
          <StatCard icon={Settings} label="System" value="Online" color="emerald"/>
        </div>

        {/* Three-column layout */}
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
          {/* Left: ESP Monitor */}
          <div className="space-y-6">
            <EspMonitor />

            {/* Quick Links */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
              <h3 className="font-extrabold text-slate-900 mb-4">Quick Links</h3>
              <div className="space-y-2">
                {[
                  { to: '/dashboard', icon: BarChart2, label: 'Analytics Dashboard', desc: 'Sales, revenue, trends' },
                  { to: '/inventory', icon: Settings, label: 'Inventory Manager', desc: 'Stock levels, reorder alerts' },
                ].map(({ to, icon: Icon, label, desc }) => (
                  <Link key={to} to={to}
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all group">
                    <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                      <Icon size={16}/>
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-slate-800 text-sm">{label}</p>
                      <p className="text-xs text-slate-400">{desc}</p>
                    </div>
                    <ChevronRight size={16} className="text-slate-300 group-hover:text-slate-500 transition-colors"/>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Middle: Tracker Config */}
          <div>
            <div className="mb-4">
              <h2 className="font-extrabold text-slate-900">Live Tracker Config</h2>
              <p className="text-xs text-slate-400 mt-0.5">Update calibration values without restarting</p>
            </div>
            <TrackerConfigPanel />
          </div>

          {/* Right: Calibration Wizard */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-extrabold text-slate-900">ESP32 Fingerprint Calibration</h2>
                <p className="text-xs text-slate-400 mt-0.5">Walk the store to map signal strengths</p>
              </div>
              <AnimatePresence mode="wait">
                {!showWizard ? (
                  <motion.button key="start" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    onClick={() => setShowWizard(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-bold text-sm rounded-xl hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/20">
                    <Zap size={14}/> {calibStatus?.calibrated ? 'Re-Calibrate' : 'Start'}
                  </motion.button>
                ) : (
                  <motion.button key="cancel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    onClick={() => setShowWizard(false)}
                    className="flex items-center gap-2 px-4 py-2 border border-slate-200 text-slate-600 font-bold text-sm rounded-xl hover:bg-slate-50 transition-colors">
                    <RotateCcw size={14}/> Cancel
                  </motion.button>
                )}
              </AnimatePresence>
            </div>

            <AnimatePresence mode="wait">
              {!showWizard ? (
                <motion.div key="status" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                  <div className={`flex items-center gap-3 p-4 rounded-xl mb-4 ${
                    calibStatus?.calibrated ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'
                  }`}>
                    {calibStatus?.calibrated
                      ? <CheckCircle size={20} className="text-emerald-600 shrink-0"/>
                      : <AlertCircle size={20} className="text-amber-600 shrink-0"/>
                    }
                    <div>
                      <p className={`font-bold text-sm ${calibStatus?.calibrated ? 'text-emerald-800' : 'text-amber-800'}`}>
                        {calibStatus?.calibrated ? 'Fingerprint Active' : 'Not Calibrated'}
                      </p>
                      <p className={`text-xs ${calibStatus?.calibrated ? 'text-emerald-700' : 'text-amber-700'}`}>
                        {calibStatus?.calibrated
                          ? `${calibStatus.corridor_count} corridors mapped`
                          : 'Walk through each corridor to map signal fingerprints'}
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {CORRIDORS.map(c => (
                      <div key={c} className="bg-slate-50 rounded-xl p-3 border border-slate-100">
                        <div className="flex items-center gap-2 mb-1">
                          <div className={`w-2 h-2 rounded-full ${calibStatus?.calibrated ? 'bg-emerald-500' : 'bg-slate-300'}`}/>
                          <p className="font-bold text-xs text-slate-700">{CORR_LABELS[c]}</p>
                        </div>
                        <p className="text-[10px] text-slate-400">Start · Mid · End</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ) : (
                <motion.div key="wizard" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <CalibrationWizard onDone={handleWizardDone} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  )
}
