import { useState } from 'react'
import { useBotConfig } from '@/hooks/useBot'
import { useQueryStats, useTopQueries, useUnansweredQueries } from '@/hooks/useAnalytics'
import { Skeleton } from '@/components/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { BarChart3, TrendingUp, Clock, AlertCircle } from 'lucide-react'
import type { DailyStat, TopQuery, UnansweredQuery } from '@/types'

interface AnalyticsTabProps {
  tenantId: string
}

export default function AnalyticsTab({ tenantId }: AnalyticsTabProps) {
  const [timeRange, setTimeRange] = useState<'7' | '30' | '90'>('30')
  
  const { data: botConfig, isLoading: botLoading } = useBotConfig(tenantId)
  const { data: stats, isLoading: statsLoading } = useQueryStats(tenantId, timeRange)
  const { data: topQueries, isLoading: topLoading } = useTopQueries(tenantId)
  const { data: unanswered, isLoading: unansweredLoading } = useUnansweredQueries(tenantId)

  const isLoading = botLoading || statsLoading

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const totalQueries =
    stats?.daily_stats?.reduce((sum: number, day: DailyStat) => sum + day.total_queries, 0) || 0

  const avgLatency = stats?.daily_stats?.length
    ? Math.round(
        stats.daily_stats.reduce(
          (sum: number, day: DailyStat) => sum + day.avg_latency_ms,
          0
        ) / stats.daily_stats.length
      )
    : 0

  const lowConfidenceCount =
    stats?.daily_stats?.reduce(
      (sum: number, day: DailyStat) => sum + day.low_confidence_count,
      0
    ) || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Analytics</h2>
          {botConfig && (
            <p className="text-gray-600">
              Bot: <span className="font-medium">{botConfig.name}</span>
            </p>
          )}
        </div>
        <div className="w-48">
          <Select value={timeRange} onValueChange={(value: any) => setTimeRange(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Total Queries</h3>
            <BarChart3 className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalQueries.toLocaleString()}</p>
          <p className="text-xs text-gray-500 mt-1">Last {timeRange} days</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Avg Latency</h3>
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{avgLatency}ms</p>
          <p className="text-xs text-gray-500 mt-1">Response time</p>
        </div>

        <div className="p-6 bg-white border rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Low Confidence</h3>
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{lowConfidenceCount}</p>
          <p className="text-xs text-gray-500 mt-1">
            {totalQueries > 0 ? `${Math.round((lowConfidenceCount / totalQueries) * 100)}%` : '0%'} of
            total
          </p>
        </div>
      </div>

      {/* Query Volume Chart */}
      {stats?.daily_stats && stats.daily_stats.length > 0 && (
        <div className="p-6 bg-white border rounded-lg">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Query Volume
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={stats.daily_stats}>
              <defs>
                <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e5e7eb', borderRadius: '6px' }}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="total_queries"
                stroke="#6366F1"
                strokeWidth={2}
                fill="url(#colorQueries)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Top Queries</h3>
        {topLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : topQueries && topQueries.length > 0 ? (
          <div className="space-y-2">
            {topQueries.map((item: TopQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {item.count} {item.count === 1 ? 'time' : 'times'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No queries yet</p>
        )}
      </div>

      {/* Unanswered/Low Confidence Queries */}
      <div className="p-6 bg-white border rounded-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          Low Confidence Queries
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          These queries received low-confidence answers. Consider adding more relevant documents.
        </p>
        {unansweredLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12" />
            ))}
          </div>
        ) : unanswered && unanswered.length > 0 ? (
          <div className="space-y-2">
            {unanswered.map((item: UnansweredQuery, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
              >
                <p className="text-sm text-gray-700 flex-1">{item.query}</p>
                <span className="ml-4 text-xs text-gray-500">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No low-confidence queries — great job! 🎉
          </p>
        )}
      </div>
    </div>
  )
}

