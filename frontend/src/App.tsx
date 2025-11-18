import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { Toaster } from '@/components/ui/sonner'
import Login from '@/pages/Login'
import AuthCallback from '@/pages/AuthCallback'
import Dashboard from '@/pages/Dashboard'
import { pageview } from '@/lib/gtag'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, loading } = useAuthStore()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  const initialize = useAuthStore((state) => state.initialize)
  const location = useLocation()

  useEffect(() => {
    initialize()
  }, [initialize])

  useEffect(() => {
    pageview(location.pathname)
  }, [location])

  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

