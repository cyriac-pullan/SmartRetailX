import React, { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { useAppStore } from './store/useAppStore'
import ToastContainer from './components/ui/Toast' // Will create in Phase 5

// Lazy load pages for performance
const LandingPage = lazy(() => import('./pages/LandingPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const ShopPage = lazy(() => import('./pages/ShopPage'))
const BillingPage = lazy(() => import('./pages/BillingPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const InventoryPage = lazy(() => import('./pages/InventoryPage'))
const RestockPage = lazy(() => import('./pages/RestockPage'))
const UserAccountPage = lazy(() => import('./pages/UserAccountPage'))

// Loading Fallback
const PageLoader = () => (
  <div className="flex items-center justify-center min-vh-100 bg-bg-0">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-500"></div>
  </div>
)

function PrivateRoute({ children }) {
  const user = useAppStore((state) => state.user)
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AdminRoute({ children }) {
  const user = useAppStore((state) => state.user)
  if (!user || !user.is_admin) return <Navigate to="/" replace />
  return children
}

const PageTransition = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    className="w-full min-h-screen"
  >
    {children}
  </motion.div>
)

function AnimatedRoutes() {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/landing" element={<PageTransition><LandingPage /></PageTransition>} />
        <Route path="/login" element={<PageTransition><LoginPage /></PageTransition>} />
        <Route path="/register" element={<PageTransition><RegisterPage /></PageTransition>} />
        
        <Route path="/" element={
          <PrivateRoute>
            <PageTransition><ShopPage /></PageTransition>
          </PrivateRoute>
        } />
        
        <Route path="/billing" element={
          <PrivateRoute>
            <PageTransition><BillingPage /></PageTransition>
          </PrivateRoute>
        } />
        
        <Route path="/restock" element={
          <PrivateRoute>
            <PageTransition><RestockPage /></PageTransition>
          </PrivateRoute>
        } />
        
        <Route path="/account" element={
          <PrivateRoute>
            <PageTransition><UserAccountPage /></PageTransition>
          </PrivateRoute>
        } />
        
        <Route path="/dashboard" element={
          <AdminRoute>
            <PageTransition><DashboardPage /></PageTransition>
          </AdminRoute>
        } />
        
        <Route path="/inventory" element={
          <AdminRoute>
            <PageTransition><InventoryPage /></PageTransition>
          </AdminRoute>
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="relative overflow-x-hidden selection:bg-brand-200">
        <Suspense fallback={<PageLoader />}>
          <AnimatedRoutes />
        </Suspense>
        <ToastContainer />
      </div>
    </BrowserRouter>
  )
}
