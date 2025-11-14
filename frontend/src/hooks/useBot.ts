import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import type { BotConfig } from '../types'

export function useBotConfig(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)

  return useQuery({
    queryKey: ['botConfig', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) return null
      const res = await apiClient.get<BotConfig>(`/v1/tenants/${tenantId}/bot`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return res.data
    },
    enabled: !!tenantId && !!session,
  })
}

export function useGenerateSystemPrompt(tenantId: string) {
  const session = useAuthStore((state) => state.session)

  return useMutation({
    mutationFn: async (businessInfo: {
      businessName: string
      industry: string
      description: string
      tone: string
      primaryGoal: string
      specialInstructions?: string
    }) => {
      if (!session) throw new Error('Not authenticated')
      
      const response = await apiClient.post(
        `/v1/tenants/${tenantId}/bot/generate-prompt`,
        {
          business_name: businessInfo.businessName,
          industry: businessInfo.industry,
          description: businessInfo.description,
          tone: businessInfo.tone,
          primary_goal: businessInfo.primaryGoal,
          special_instructions: businessInfo.specialInstructions,
        },
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
  })
}

export function useUpdateBotConfig(tenantId: string) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: { system_prompt: string | null; business_info?: any }) => {
      if (!session) throw new Error('Not authenticated')
      
      const response = await apiClient.put(
        `/v1/tenants/${tenantId}/bot`,
        data,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate bot config cache
      queryClient.invalidateQueries({ queryKey: ['botConfig', tenantId] })
    },
  })
}


