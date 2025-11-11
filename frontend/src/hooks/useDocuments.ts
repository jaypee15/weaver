import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/axios'
import { useAuthStore } from '@/store/authStore'
import { Document } from '@/types'

export function useDocuments(tenantId: string | undefined) {
  const session = useAuthStore((state) => state.session)

  return useQuery({
    queryKey: ['documents', tenantId],
    queryFn: async () => {
      if (!tenantId || !session) return []
      
      const response = await apiClient.get<{ documents: Document[] }>(
        `/v1/tenants/${tenantId}/docs`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      )
      return response.data.documents
    },
    enabled: !!tenantId && !!session,
    refetchInterval: 5000, // Poll every 5 seconds for status updates
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
      queryClient.invalidateQueries({ queryKey: ['documents', tenantId] })
    },
  })
}

