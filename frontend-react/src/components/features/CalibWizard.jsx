import React, { useState, useEffect } from 'react'
import { MapPin, Zap, RefreshCw, Layers } from 'lucide-react'
import { getCalibStatus, saveCalibration, captureSignal } from '../../services/api'
import { useToast } from '../../hooks/useToast'
import Button from '../ui/Button'

export default function CalibWizard() {
  const { toast } = useToast()
  const [step, setStep] = useState(0)
  const [numAisles, setNumAisles] = useState(3)
  
  // State for active capture
  const [currentAisle, setCurrentAisle] = useState(1)
  const [currentPos, setCurrentPos] = useState('START') // START -> MID -> END
  
  const [isCapturing, setIsCapturing] = useState(false)
  const [countdown, setCountdown] = useState(7)
  const [status, setStatus] = useState('Checking...')
  
  // Store all results here before save
  const [results, setResults] = useState([])

  useEffect(() => {
    getCalibStatus().then(({ data }) => {
      setStatus(data?.calibrated ? `Calibrated (${data.points} points)` : 'Uncalibrated')
    })
  }, [])

  const handleStart = () => {
    setNumAisles(parseInt(document.getElementById('aisleSelect').value) || 3)
    setStep(1)
    setCurrentAisle(1)
    setCurrentPos('START')
    setResults([])
  }

  const runCapture = async () => {
    setIsCapturing(true)
    setCountdown(7)
    
    // Simulate countdown UI
    const timer = setInterval(() => {
      setCountdown(c => {
        if (c <= 1) { clearInterval(timer); return 0 }
        return c - 1
      })
    }, 1000)

    // Call API (takes ~7s on backend)
    const { data, error } = await captureSignal(currentAisle, currentPos)
    clearInterval(timer)
    setIsCapturing(false)
    setCountdown(7)

    if (data?.success) {
      toast(`Captured Aisle ${currentAisle} - ${currentPos}`, 'success')
      setResults(r => [...r, { aisle: currentAisle, position: currentPos, ...data.data }])
      advanceWizard()
    } else {
      toast(`Capture failed: ${error?.message || 'timeout'}`, 'error')
    }
  }

  const advanceWizard = () => {
    if (currentPos === 'START') setCurrentPos('MID')
    else if (currentPos === 'MID') setCurrentPos('END')
    else {
      if (currentAisle < numAisles) {
        setCurrentAisle(currentAisle + 1)
        setCurrentPos('START')
      } else {
        setStep(2) // Done
      }
    }
  }

  const completeCalibration = async () => {
    const { error } = await saveCalibration({ points: results })
    if (!error) {
      toast('Calibration saved successfully!', 'success')
      setStep(0)
      setStatus(`Calibrated (${results.length} points)`)
    } else {
      toast('Failed to save calibration', 'error')
    }
  }

  if (step === 2) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center text-slate-200">
        <div className="text-5xl mb-4">✅</div>
        <h3 className="text-xl font-bold text-white mb-2">All positions captured!</h3>
        <p className="text-slate-400 text-sm mb-6">Click Save to permanently store the mapped store footprint to the database.</p>
        <div className="flex justify-center gap-4">
           <Button variant="ghost" onClick={() => setStep(0)} className="text-slate-400 hover:text-white">Start Over</Button>
           <Button variant="primary" onClick={completeCalibration} className="bg-emerald-500 hover:bg-emerald-600 border-none text-white">💾 Save Database</Button>
        </div>
      </div>
    )
  }

  if (step === 1) {
    const totalPoints = numAisles * 3
    const currentPointIdx = (currentAisle - 1) * 3 + (currentPos === 'START' ? 0 : currentPos === 'MID' ? 1 : 2)
    const progress = ((currentPointIdx) / totalPoints) * 100

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 text-slate-200 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-slate-800">
           <div className="h-full bg-brand-500 transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
               <div className="text-[10px] font-black tracking-widest text-brand-400 mb-2">AISLE {currentAisle} · {currentPos}</div>
               <h3 className="text-2xl font-bold text-white mb-4">Stand at the <span className="text-brand-300">{currentPos}</span> of Aisle {currentAisle}</h3>
               <div className="aspect-[2/1] bg-slate-800 rounded-xl border border-slate-700 flex items-center justify-center relative overflow-hidden">
                   <div className="text-slate-600 font-bold">Store Map View</div>
                   <div className={`absolute w-4 h-4 rounded-full bg-brand-500 shadow-[0_0_15px_#6366f1] top-1/2 -mt-2
                       ${currentPos === 'START' ? 'left-6' : currentPos === 'MID' ? 'left-1/2 -ml-2' : 'right-6'}
                   `} />
               </div>
            </div>

            <div className="text-center p-6 bg-slate-800/50 rounded-2xl border border-slate-700">
               <div className="text-7xl font-black text-brand-300 font-mono tracking-tighter mb-2 tabular-nums">
                 {isCapturing ? countdown : '7'}
               </div>
               <p className="text-slate-400 font-medium text-sm mb-6">Seconds to capture</p>
               
               <Button 
                 variant="primary" 
                 className={`w-full py-4 rounded-xl border-none transition-all ${isCapturing ? 'bg-slate-700 opacity-80 cursor-not-allowed text-white' : 'bg-brand-500 hover:bg-brand-600 text-white shadow-xl shadow-brand-500/20'}`}
                 onClick={runCapture}
                 disabled={isCapturing}
               >
                 <Zap size={18} className="mr-2" />
                 {isCapturing ? 'Scanning Environment...' : 'Capture Signal Network'}
               </Button>
               <button onClick={advanceWizard} disabled={isCapturing} className="text-xs text-slate-500 font-semibold mt-4 hover:text-slate-300 transition-colors">Skip this point</button>
            </div>
        </div>
      </div>
    )
  }

  // Step 0 Wrapper
  return (
    <div className="card p-8 bg-gradient-to-br from-slate-900 to-slate-800 text-slate-200 rounded-3xl relative overflow-hidden border border-slate-700">
       <div className="absolute -top-20 -right-20 w-64 h-64 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />
       
       <div className="flex justify-between items-start mb-6 border-b border-slate-700/50 pb-6">
           <div className="space-y-1">
               <h3 className="text-xl font-extrabold text-white flex items-center gap-2">
                   <MapPin className="text-brand-400" size={24} /> 
                   ESP Calibration Wizard
               </h3>
               <p className="text-slate-400 text-sm">One-time setup · Teach the neural network your exact store layout</p>
           </div>
           <div className="px-4 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-xs font-bold text-slate-300">
               Status: <span className={status.includes('Calibrated') ? 'text-emerald-400' : 'text-amber-400'}>{status}</span>
           </div>
       </div>

       <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
           <div className="bg-slate-800/80 border border-slate-700 p-4 rounded-2xl flex items-center gap-4">
               <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-xl text-brand-300">📍</div>
               <div><p className="text-xs text-brand-400 font-bold uppercase tracking-wider">Positions</p><p className="form-bold text-white text-sm">3 per aisle</p></div>
           </div>
           <div className="bg-slate-800/80 border border-slate-700 p-4 rounded-2xl flex items-center gap-4">
               <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-xl text-brand-300">📡</div>
               <div><p className="text-xs text-brand-400 font-bold uppercase tracking-wider">Networks</p><p className="form-bold text-white text-sm">ESP32 Beacons</p></div>
           </div>
           <div className="bg-slate-800/80 border border-slate-700 p-4 rounded-2xl flex items-center gap-4">
               <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-xl text-brand-300">⏱️</div>
               <div><p className="text-xs text-brand-400 font-bold uppercase tracking-wider">Duration</p><p className="form-bold text-white text-sm">7 sec per point</p></div>
           </div>
       </div>

       <div className="flex items-center gap-6 justify-center bg-slate-950/30 p-4 rounded-2xl border border-slate-800/50">
           <div className="flex items-center gap-3">
               <label className="text-sm font-bold text-slate-300">Aisles:</label>
               <select id="aisleSelect" defaultValue={3} className="bg-slate-800 border-none text-white rounded-lg py-2 pl-4 pr-8 font-bold focus:ring-2 focus:ring-brand-500 outline-none">
                   {[1,2,3,4,5,6].map(n => <option key={n} value={n}>{n}</option>)}
               </select>
           </div>
           <Button variant="primary" onClick={handleStart} className="px-8 rounded-xl bg-brand-500 hover:bg-brand-600 border-none text-white shadow-lg shadow-brand-500/20">
               Start Calibration →
           </Button>
       </div>
    </div>
  )
}
