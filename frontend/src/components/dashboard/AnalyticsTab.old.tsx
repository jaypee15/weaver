import { useMemo } from 'react'
import { useQueryStats, useTopQueries, useUnansweredQueries } from '@/hooks/useAnalytics'
import { useBotConfig } from '@/hooks/useBot'

interface AnalyticsTabProps {
  tenantId: string
}

export default function AnalyticsTab({ tenantId }: AnalyticsTabProps) {
  const { data: stats, isLoading: loadingStats } = useQueryStats(tenantId)
  const { data: top, isLoading: loadingTop } = useTopQueries(tenantId, 10)
  const { data: unanswered, isLoading: loadingUnanswered } = useUnansweredQueries(tenantId, 10)
  const { data: bot } = useBotConfig(tenantId)

  const totals = useMemo(() => {
    const daily = stats?.daily_stats ?? []
    const totalQueries = daily.reduce((sum, d) => sum + d.total_queries, 0)
    const avgLatency =
      daily.length > 0
        ? Math.round(daily.reduce((sum, d) => sum + d.avg_latency_ms, 0) / daily.length)
        : 0
    const lowConfidence = daily.reduce((sum, d) => sum + d.low_confidence_count, 0)
    return { totalQueries, avgLatency, lowConfidence }
  }, [stats])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-1">Analytics</h2>
        {bot && (
          <p className="text-gray-600">
            Bot: <span className="font-medium">{bot.name}</span>
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Total Queries (30d)" value={loadingStats ? '—' : totals.totalQueries.toString()} />
        <StatCard label="Avg Latency (ms)" value={loadingStats ? '—' : totals.avgLatency.toString()} />
        <StatCard label="Low Confidence (30d)" value={loadingStats ? '—' : totals.lowConfidence.toString()} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Panel title="Top Queries" loading={loadingTop}>
          {top && top.length > 0 ? (
            <ul className="space-y-2">
              {top.map((q, i) => (
                <li key={i} className="flex items-center justify-between">
                  <span className="truncate pr-4">{q.query}</span>
                  <span className="text-sm text-gray-600">{q.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <Empty message="No queries yet" />
          )}
        </Panel>

        <Panel title="Unanswered / Low-Confidence" loading={loadingUnanswered}>
          {unanswered && unanswered.length > 0 ? (
            <ul className="space-y-2">
              {unanswered.map((q, i) => (
                <li key={i} className="truncate">{q.query}</li>
              ))}
            </ul>
          ) : (
            <Empty message="All good! No unanswered queries." />
          )}
        </Panel>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-4 bg-white">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
    </div>
  )
}

function Panel({
  title,
  loading,
  children,
}: {
  title: string
  loading?: boolean
  children: React.ReactNode
}) {
  return (
    <div className="rounded-lg border bg-white">
      <div className="p-4 border-b">
        <h3 className="font-medium">{title}</h3>
      </div>
      <div className="p-4">
        {loading ? <div className="text-gray-500 text-sm">Loading…</div> : children}
      </div>
    </div>
  )
}

function Empty({ message }: { message: string }) {
  return <div className="text-gray-500 text-sm">{message}</div>
}


