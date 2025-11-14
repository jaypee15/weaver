import { create } from 'zustand'
import { User as SupabaseUser, Session, AuthChangeEvent } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { apiClient } from '../lib/axios'
import { User } from '../types'

interface AuthState {
  session: Session | null
  supabaseUser: SupabaseUser | null
  user: User | null
  loading: boolean
  initialized: boolean
  setSession: (session: Session | null) => void
  setUser: (user: User | null) => void
  fetchUserProfile: () => Promise<void>
  signOut: () => Promise<void>
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  session: null,
  supabaseUser: null,
  user: null,
  loading: true,
  initialized: false,

  setSession: (session) => {
    set({ session, supabaseUser: session?.user || null })
  },

  setUser: (user) => {
    set({ user })
  },

  fetchUserProfile: async () => {
    const { session } = get()
    if (!session) {
      set({ user: null, loading: false })
      return
    }

    try {
      const response = await apiClient.get<User>('/v1/users/me', {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      set({ user: response.data, loading: false })
    } catch (error: any) {
      console.error('Error fetching user profile:', error)
      
      // If user not found (404), try to complete signup
      if (error.response?.status === 404) {
        try {
          const signupResponse = await apiClient.post(
            '/v1/auth/complete-signup',
            {},
            { headers: { Authorization: `Bearer ${session.access_token}` } }
          )
          set({ user: signupResponse.data, loading: false })
        } catch (signupError) {
          console.error('Error completing signup:', signupError)
          set({ loading: false })
        }
      } else {
        set({ loading: false })
      }
    }
  },

  signOut: async () => {
    await supabase.auth.signOut()
    set({ session: null, supabaseUser: null, user: null })
  },

  initialize: async () => {
    if (get().initialized) return

    // Get initial session
    const { data: { session } } = await supabase.auth.getSession()
    set({ session, supabaseUser: session?.user || null })

    // Fetch user profile if session exists
    if (session) {
      await get().fetchUserProfile()
    } else {
      set({ loading: false })
    }

    // Listen for auth changes
    supabase.auth.onAuthStateChange(async (_event: AuthChangeEvent, session: Session | null) => {
      set({ session, supabaseUser: session?.user || null })
      
      if (session) {
        await get().fetchUserProfile()
      } else {
        set({ user: null, loading: false })
      }
    })

    set({ initialized: true })
  },
}))

