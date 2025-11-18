import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '../store/authStore'
import type { DocumentListResponse } from '../types'

type DocumentQueryOptions = {
  limit?: number
  offset?: number
  status?: string | null
  enabled?: boolean
}

const buildEmptyResponse = (options: DocumentQueryOptions): DocumentListResponse => ({
  documents: [],
  total: 0,
  limit: options.limit ?? 50,
  offset: options.offset ?? 0,
  status_filter: options.status ?? null,
})

export function useDocuments(tenantId: string | undefined, options: DocumentQueryOptions = {}) {
  const session = useAuthStore((state) => state.session)
  const limit = options.limit ?? 50
  const offset = options.offset ?? 0
  const status = options.status ?? null

  return useQuery<DocumentListResponse>({
    queryKey: ['documents', tenantId, limit, offset, status],
    queryFn: async () => {
      if (!tenantId || !session) return buildEmptyResponse(options)
      
      const response = await apiClient.get<DocumentListResponse>(
        `/v1/tenants/${tenantId}/docs`,
        {
          params: {
            limit,
            offset,
            status: status || undefined,
          },
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data
    },
    enabled: !!tenantId && !!session && (options.enabled ?? true),
    refetchInterval: 5000, // Poll for status updates
    keepPreviousData: true,
  })
}

export function useUploadDocument(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      if (!tenantId || !session) {
        throw new Error('Tenant ID or session not available')
      }

      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post(
        `/v1/tenants/${tenantId}/docs:upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch documents list
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

