import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '@/store/authStore'
import type { BotConfig } from '@/types'

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


