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

export interface BotConfig {
  id: string
  tenant_id: string
  name: string
  config: Record<string, any>
  created_at: string
}

export interface DailyStat {
  date: string
  total_queries: number
  avg_latency_ms: number
  low_confidence_count: number
}

export interface QueryStatsResponse {
  daily_stats: DailyStat[]
}

export interface TopQuery {
  query: string
  count: number
}

export interface UnansweredQuery {
  query: string
  created_at: string
}

