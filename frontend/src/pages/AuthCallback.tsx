import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { apiClient } from '@/lib/axios'
import { toast } from 'sonner' // Add toast for better UX

export default function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const queryParams = new URLSearchParams(window.location.search)
        
        const accessToken = hashParams.get('access_token')
        const code = queryParams.get('code')

        if (accessToken) {
          console.log('Handling implicit flow callback')
          // Give Supabase client a moment to persist session
          await new Promise(resolve => setTimeout(resolve, 200))
          
          const { data: { session }, error } = await supabase.auth.getSession()
          
          if (error) throw error

          if (session) {
            // FIX: Await this call!
            try {
              await apiClient.post(
                '/v1/auth/complete-signup',
                {},
                { headers: { Authorization: `Bearer ${session.access_token}` } }
              )
            } catch (err) {
              console.error('Signup completion error:', err)
              // Even if it fails (e.g. already exists), we try to proceed
            }
          }
        } else if (code) {
          console.log('Handling PKCE flow callback')
          const { data, error } = await supabase.auth.exchangeCodeForSession(code)

          if (error) throw error

          if (data.session) {
            // FIX: Await this call!
            try {
              await apiClient.post(
                '/v1/auth/complete-signup',
                {},
                { headers: { Authorization: `Bearer ${data.session.access_token}` } }
              )
            } catch (err) {
              console.error('Signup completion error:', err)
            }
          }
        }

        // Only navigate AFTER the backend work is done
        navigate('/dashboard', { replace: true })
        
      } catch (error: any) {
        console.error('Error in auth callback:', error)
        toast.error('Authentication failed. Please try again.')
        navigate('/', { replace: true })
      }
    }

    handleCallback()
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-gray-500">Setting up your workspace...</p>
      </div>
    </div>
  )
}

