import { useState } from 'react'
import { useAPIKeys, useCreateAPIKey, useRevokeAPIKey } from '@/hooks/useAPIKeys'
import { Button } from '@/components/ui/button'
import { Copy, Check, Trash2 } from 'lucide-react'
import { API_URL } from '@/lib/axios'

interface APIKeysTabProps {
  tenantId: string
}

export default function APIKeysTab({ tenantId }: APIKeysTabProps) {
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const { data: keys = [], isLoading } = useAPIKeys(tenantId)
  const createMutation = useCreateAPIKey(tenantId)
  const revokeMutation = useRevokeAPIKey(tenantId)

  const handleCreateKey = async () => {
    try {
      const result = await createMutation.mutateAsync(`Key ${new Date().toISOString()}`)
      setNewKey(result.key)
    } catch (error) {
      console.error('Error creating key:', error)
    }
  }

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return
    }
    try {
      await revokeMutation.mutateAsync(keyId)
    } catch (error) {
      console.error('Error revoking key:', error)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold mb-2">API Keys</h2>
        <p className="text-gray-600">
          Manage API keys for programmatic access to your bot
        </p>
      </div>

      {/* API Endpoint Information */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold mb-2 text-blue-900">Bot API Endpoint</h3>
        <p className="text-sm text-gray-700 mb-2">Use this endpoint to query your bot:</p>
        <code className="block p-3 bg-white rounded font-mono text-sm mb-3 border">
          POST {API_URL}/v1/tenants/{tenantId}/query
        </code>
        <details className="text-sm">
          <summary className="cursor-pointer text-blue-700 hover:text-blue-900 font-medium mb-2">
            Show example code
          </summary>
          <div className="mt-2 p-3 bg-white rounded border">
            <pre className="text-xs overflow-x-auto">
              {`curl -X POST ${API_URL}/v1/tenants/${tenantId}/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is your product about?"}'`}
            </pre>
          </div>
        </details>
      </div>

      {/* Create New Key */}
      <div>
        <Button onClick={handleCreateKey} disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Creating...' : 'Create New API Key'}
        </Button>
      </div>

      {/* New Key Display */}
      {newKey && (
        <div className="p-4 bg-yellow-50 border border-yellow-300 rounded-lg">
          <p className="font-semibold mb-2 text-yellow-900">
            New API Key (save this, it won't be shown again):
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 p-3 bg-white rounded font-mono text-sm border">
              {newKey}
            </code>
            <Button
              onClick={() => copyToClipboard(newKey)}
              variant="secondary"
              size="icon"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
          <Button
            onClick={() => setNewKey(null)}
            variant="ghost"
            size="sm"
            className="mt-2"
          >
            Dismiss
          </Button>
        </div>
      )}

      {/* Keys List */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Your API Keys</h3>
        {keys.length === 0 ? (
          <p className="text-gray-600">No API keys yet. Create one above!</p>
        ) : (
          <div className="space-y-3">
            {keys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex-1">
                  <p className="font-medium">{key.name || 'Unnamed Key'}</p>
                  <div className="text-sm text-gray-600 space-y-1 mt-1">
                    <p>Created: {new Date(key.created_at).toLocaleDateString()}</p>
                    {key.last_used_at && (
                      <p>Last used: {new Date(key.last_used_at).toLocaleDateString()}</p>
                    )}
                    <p>Rate limit: {key.rate_limit_rpm} rpm</p>
                  </div>
                </div>
                <Button
                  onClick={() => handleRevokeKey(key.id)}
                  disabled={key.revoked || revokeMutation.isPending}
                  variant={key.revoked ? 'secondary' : 'destructive'}
                  size="sm"
                >
                  {key.revoked ? (
                    'Revoked'
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Revoke
                    </>
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

