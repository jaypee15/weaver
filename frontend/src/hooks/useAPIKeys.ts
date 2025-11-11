import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '@/store/authStore'
import { APIKey, CreateAPIKeyResponse } from '@/types'

export function useAPIKeys(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)

  return useQuery({
    queryKey: ['apiKeys', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) return []
      
      const response = await apiClient.get<{ keys: APIKey[] }>(
        `/v1/tenants/${tenantId}/api-keys`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data.keys
    },
    enabled: !!tenantId && !!session,
  })
}

export function useCreateAPIKey(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (name: string) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      const response = await apiClient.post<CreateAPIKeyResponse>(
        `/v1/tenants/${tenantId}/api-keys`,
        { name },
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', tenantId] })
    },
  })
}

export function useRevokeAPIKey(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (keyId: string) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      await apiClient.delete(
        `/v1/tenants/${tenantId}/api-keys/${keyId}`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys', tenantId] })
    },
  })
}

