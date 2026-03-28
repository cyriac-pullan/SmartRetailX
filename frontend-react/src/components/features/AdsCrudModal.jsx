import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Save, AlertCircle } from 'lucide-react'
import Button from '../ui/Button'
import { createAd, updateAd } from '../../services/api'
import { useToast } from '../../hooks/useToast'

export default function AdsCrudModal({ open, onOpenChange, adToEdit, onSuccess }) {
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    image_url: '',
    product_barcode: '',
    aisle: '',
    position_tag: '',
    priority: 0,
    rev_per_view: 0,
    is_compulsory: false
  })

  useEffect(() => {
    if (open) {
      if (adToEdit) {
        setFormData({
          title: adToEdit.title || '',
          description: adToEdit.description || '',
          image_url: adToEdit.image_url || '',
          product_barcode: adToEdit.product_barcode || '',
          aisle: adToEdit.target_location?.aisle || '',
          position_tag: adToEdit.target_location?.position_tag || '',
          priority: adToEdit.priority || 0,
          rev_per_view: adToEdit.rev_per_view || 0,
          is_compulsory: adToEdit.is_compulsory || false
        })
      } else {
        setFormData({
          title: '', description: '', image_url: '', product_barcode: '',
          aisle: '', position_tag: '', priority: 0, rev_per_view: 0, is_compulsory: false
        })
      }
    }
  }, [open, adToEdit])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const payload = {
      title: formData.title,
      description: formData.description,
      image_url: formData.image_url,
      product_barcode: formData.product_barcode,
      target_location: {
        aisle: formData.aisle ? parseInt(formData.aisle) : null,
        position_tag: formData.position_tag || null
      },
      priority: parseInt(formData.priority) || 0,
      rev_per_view: parseFloat(formData.rev_per_view) || 0,
      is_compulsory: formData.is_compulsory
    }

    const { error } = adToEdit ? await updateAd(adToEdit.id, payload) : await createAd(payload)
    
    setLoading(false)
    if (error) {
      toast(`Error saving ad: ${error.message}`, 'error')
    } else {
      toast(adToEdit ? 'Ad updated successfully' : 'Ad created successfully', 'success')
      onSuccess?.()
      onOpenChange(false)
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[200] flex items-center justify-center p-4"
          onClick={(e) => e.target === e.currentTarget && onOpenChange(false)}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            className="bg-white rounded-3xl shadow-xl w-full max-w-lg overflow-hidden"
          >
            <div className="flex items-center justify-between p-6 border-b border-bg-2">
              <h2 className="text-xl font-extrabold text-text-900">{adToEdit ? 'Edit Ad' : 'Create Advertisement'}</h2>
              <button onClick={() => onOpenChange(false)} className="p-2 hover:bg-bg-1 rounded-xl transition-colors">
                <X size={20} className="text-text-400" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Title *</label>
                <input required type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" placeholder="e.g. 50% Off Coke" />
              </div>
              
              <div>
                <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Description</label>
                <textarea rows={2} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none resize-none" placeholder="Subtitle or details" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Image URL</label>
                  <input type="text" value={formData.image_url} onChange={e => setFormData({...formData, image_url: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" placeholder="https://..." />
                </div>
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Product Barcode</label>
                  <input type="text" value={formData.product_barcode} onChange={e => setFormData({...formData, product_barcode: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" placeholder="Target item" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Target Aisle</label>
                  <input type="number" value={formData.aisle} onChange={e => setFormData({...formData, aisle: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" placeholder="Any" />
                </div>
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Location Tag</label>
                  <input type="text" value={formData.position_tag} onChange={e => setFormData({...formData, position_tag: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" placeholder="e.g. ENDCAP" />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 items-end">
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Priority</label>
                  <input type="number" value={formData.priority} onChange={e => setFormData({...formData, priority: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" />
                </div>
                <div>
                  <label className="text-xs font-bold text-text-400 uppercase tracking-widest mb-1 block">Rev/View (₹)</label>
                  <input type="number" step="0.1" value={formData.rev_per_view} onChange={e => setFormData({...formData, rev_per_view: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500 outline-none" />
                </div>
                <div className="flex h-10 items-center justify-center bg-slate-50 border border-slate-200 rounded-xl group cursor-pointer" onClick={() => setFormData({...formData, is_compulsory: !formData.is_compulsory})}>
                  <label className="flex items-center gap-2 cursor-pointer text-sm font-bold text-text-900 pointer-events-none">
                    <input type="checkbox" checked={formData.is_compulsory} readOnly className="w-4 h-4 text-brand-500 rounded border-slate-300 focus:ring-brand-500" />
                    Compulsory
                  </label>
                </div>
              </div>

              {formData.is_compulsory && (
                <div className="flex items-center gap-2 p-3 bg-red-50 text-red-600 rounded-xl text-xs font-medium">
                  <AlertCircle size={16} /> Compulsory ads show to all users regardless of location.
                </div>
              )}

              <div className="pt-4 border-t border-bg-2 flex justify-end gap-3">
                <Button variant="ghost" type="button" onClick={() => onOpenChange(false)}>Cancel</Button>
                <Button variant="primary" type="submit" loading={loading}>
                  <Save size={16} className="mr-2" />
                  {adToEdit ? 'Save Changes' : 'Create Ad'}
                </Button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
