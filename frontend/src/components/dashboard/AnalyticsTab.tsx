interface AnalyticsTabProps {
  tenantId: string
}

export default function AnalyticsTab({ tenantId: _tenantId }: AnalyticsTabProps) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-2">Analytics</h2>
      <p className="text-gray-600">
        Analytics dashboard coming soon. This will show query volume, latency, top queries,
        and more.
      </p>
      <div className="mt-6 p-8 border-2 border-dashed border-gray-300 rounded-lg text-center">
        <p className="text-gray-500">📊 Coming Soon</p>
      </div>
    </div>
  )
}

