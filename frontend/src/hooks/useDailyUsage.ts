import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'

interface DailyUsage {
  current: number
  limit: number
  remaining: number
  redis_available: boolean
}

export const useDailyUsage = (tenantId: string | undefined) => {
  const session = useAuthStore((state) => state.session)

  return useQuery<DailyUsage>({
    queryKey: ['daily-usage', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) {
        return {
          current: 0,
          limit: 50,
          remaining: 50,
          redis_available: false
        }
      }
      
      const { data } = await apiClient.get(`/v1/tenants/${tenantId}/usage/daily`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return data
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 20000, // Consider data stale after 20 seconds
  })
}

