import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '@/store/authStore'
import type { QueryStatsResponse, TopQuery, UnansweredQuery } from '@/types'

export function useQueryStats(tenantId: string | undefined, days: string = '30') {
  const session = useAuthStore((state) => state.session)
  
  // Calculate start_date based on days
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - parseInt(days))
  const endDate = new Date()
  
  return useQuery({
    queryKey: ['analytics', 'stats', tenantId, days],
    queryFn: async () => {
      if (!tenantId || !session) return { daily_stats: [] } as QueryStatsResponse
      const res = await apiClient.get<QueryStatsResponse>(`/v1/tenants/${tenantId}/analytics/queries`, {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
        },
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      return res.data
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}

export function useTopQueries(tenantId: string | undefined, limit = 10) {
  const session = useAuthStore((state) => state.session)
  return useQuery({
    queryKey: ['analytics', 'top', tenantId, limit],
    queryFn: async () => {
      if (!tenantId || !session) return [] as TopQuery[]
      const res = await apiClient.get<{ queries: TopQuery[] }>(
        `/v1/tenants/${tenantId}/analytics/top-queries`,
        {
          params: { limit },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return res.data.queries
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}

export function useUnansweredQueries(tenantId: string | undefined, limit = 20) {
  const session = useAuthStore((state) => state.session)
  return useQuery({
    queryKey: ['analytics', 'unanswered', tenantId, limit],
    queryFn: async () => {
      if (!tenantId || !session) return [] as UnansweredQuery[]
      const res = await apiClient.get<{ queries: UnansweredQuery[] }>(
        `/v1/tenants/${tenantId}/analytics/unanswered`,
        {
          params: { limit },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return res.data.queries
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 15000,
  })
}


