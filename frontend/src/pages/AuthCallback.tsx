import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { apiClient } from '../lib/axios'

export default function AuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check if we have a hash (implicit flow) or code (PKCE flow)
        const hashParams = new URLSearchParams(window.location.hash.substring(1))
        const queryParams = new URLSearchParams(window.location.search)
        
        const accessToken = hashParams.get('access_token')
        const code = queryParams.get('code')

        if (accessToken) {
          // Implicit flow - tokens are in the hash
          // Supabase client will automatically handle this via onAuthStateChange
          console.log('Handling implicit flow callback')
          
          // Wait briefly for Supabase to process the session (reduced from 500ms to 200ms)
          await new Promise(resolve => setTimeout(resolve, 200))
          
          // Get the current session
          const { data: { session }, error } = await supabase.auth.getSession()
          
          if (error) {
            console.error('Error getting session:', error)
            navigate('/', { replace: true })
            return
          }

          // Complete signup on backend (creates tenant/user/bot if needed)
          // Don't wait for this - let it happen in background
          if (session) {
            apiClient.post(
              '/v1/auth/complete-signup',
              {},
              {
                headers: {
                  Authorization: `Bearer ${session.access_token}`,
                },
              }
            ).catch((error: unknown) => {
              console.error('Error completing signup:', error)
              // Dashboard will handle this fallback
            })
          }
        } else if (code) {
          // PKCE flow - exchange code for session
          console.log('Handling PKCE flow callback')
          const { data, error } = await supabase.auth.exchangeCodeForSession(code)

          if (error) {
            console.error('Error exchanging code for session:', error)
            navigate('/')
            return
          }

          // Complete signup on backend (creates tenant/user/bot if needed)
          if (data.session) {
            try {
              await apiClient.post(
                '/v1/auth/complete-signup',
                {},
                {
                  headers: {
                    Authorization: `Bearer ${data.session.access_token}`,
                  },
                }
              )
            } catch (error) {
              console.error('Error completing signup:', error)
              // Continue anyway - the dashboard will handle this
            }
          }
        }

        // Redirect to dashboard immediately (replace history to avoid back button issues)
        navigate('/dashboard', { replace: true })
      } catch (error: unknown) {
        console.error('Error in auth callback:', error)
        navigate('/', { replace: true })
      }
    }

    handleCallback()
  }, [navigate])

  // Minimal UI - just show nothing or a subtle indicator
  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      {/* Invisible loading - processing happens in background */}
      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  )
}

