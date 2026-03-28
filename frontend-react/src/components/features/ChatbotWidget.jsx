import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, Send, X, ChefHat, User } from 'lucide-react'
import { chatWithRecipeBot } from '../../services/api'
import Button from '../ui/Button'
import { twMerge } from 'tailwind-merge'

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hi! I'm your SmartRetailX Recipe Assistant. Ask me for recipes based on what's in your cart!" }
  ])
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, loading])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }])
    setInput('')
    setLoading(true)

    const { data, error } = await chatWithRecipeBot(userMsg)
    
    if (data) {
      setMessages((prev) => [...prev, { role: 'bot', text: data.response }])
    } else {
      setMessages((prev) => [...prev, { role: 'bot', text: "Sorry, I'm having trouble connecting right now." }])
    }
    setLoading(false)
  }

  return (
    <>
      {/* FAB */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-brand-500 text-white rounded-2xl shadow-xl shadow-brand-500/30 flex items-center justify-center z-[90]"
      >
        <MessageSquare size={28} />
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 w-full max-w-[360px] bg-white rounded-2xl shadow-2xl border border-bg-2 z-[100] flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="bg-brand-500 p-4 text-white flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <ChefHat size={20} />
                </div>
                <div>
                  <h4 className="font-bold text-sm">Recipe Assistant</h4>
                  <p className="text-[10px] opacity-80">Online & ready to help</p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-white/10 rounded-lg">
                <X size={20} />
              </button>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 h-[400px] overflow-y-auto p-4 space-y-4 bg-bg-1/30 custom-scrollbar">
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: m.role === 'user' ? 10 : -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={twMerge(
                    "flex items-end space-x-2 max-w-[85%]",
                    m.role === 'user' ? "ml-auto flex-row-reverse space-x-reverse" : ""
                  )}
                >
                  <div className={twMerge(
                    "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border border-bg-2",
                    m.role === 'user' ? "bg-white text-text-400" : "bg-brand-50 text-brand-500"
                  )}>
                    {m.role === 'user' ? <User size={16} /> : <ChefHat size={16} />}
                  </div>
                  <div className={twMerge(
                    "p-3 rounded-2xl text-sm leading-relaxed",
                    m.role === 'user' 
                        ? "bg-brand-500 text-white rounded-tr-none" 
                        : "bg-white text-text-900 shadow-sm border border-bg-2 rounded-tl-none whitespace-pre-wrap"
                  )}>
                    {m.text}
                  </div>
                </motion.div>
              ))}
              
              {loading && (
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-brand-50 rounded-lg flex items-center justify-center border border-bg-2">
                    <ChefHat size={16} className="text-brand-500" />
                  </div>
                  <div className="bg-white p-3 rounded-2xl rounded-tl-none border border-bg-2 flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-text-400 rounded-full animate-bounce" />
                    <div className="w-1.5 h-1.5 bg-text-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-1.5 h-1.5 bg-text-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-bg-2 flex items-center space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask for a recipe..."
                className="flex-1 bg-bg-1 border-none rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-500/20 outline-none"
              />
              <Button
                variant="primary"
                className="w-10 h-10 p-0 rounded-xl"
                onClick={handleSend}
                loading={loading}
              >
                {!loading && <Send size={18} />}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
