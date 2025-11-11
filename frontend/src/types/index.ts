export interface User {
  id: string
  email: string
  tenant_id: string
  role: string
}

export interface Document {
  id: string
  filename: string
  size_bytes: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  updated_at: string
}

export interface APIKey {
  id: string
  name: string
  created_at: string
  last_used_at?: string
  rate_limit_rpm: number
  revoked: boolean
}

export interface CreateAPIKeyResponse {
  key: string
  id: string
}

