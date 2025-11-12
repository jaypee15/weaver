import { useState, useRef, useEffect } from 'react'
import { useAPIKeys, useCreateAPIKey, useRevokeAPIKey } from '@/hooks/useAPIKeys'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Check, Trash2, Play, Square } from 'lucide-react'
import { API_URL } from '@/lib/axios'
import { toast } from 'sonner'

interface APIKeysTabProps {
  tenantId: string
}

export default function APIKeysTab({ tenantId }: APIKeysTabProps) {
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [keyName, setKeyName] = useState('')
  
  // Test panel state
  const [testKey, setTestKey] = useState<string>('')
  const [testQuery, setTestQuery] = useState<string>('')
  const [stream, setStream] = useState<boolean>(true)
  const [testing, setTesting] = useState<boolean>(false)
  const [testOutput, setTestOutput] = useState<string>('')
  const [testError, setTestError] = useState<string>('')
  const abortControllerRef = useRef<AbortController | null>(null)

  const { data: keys = [], isLoading } = useAPIKeys(tenantId)
  const createMutation = useCreateAPIKey(tenantId)
  const revokeMutation = useRevokeAPIKey(tenantId)

  // Load test panel state from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem('wvr_test_key')
    const savedQuery = localStorage.getItem('wvr_test_query')
    if (savedKey) setTestKey(savedKey)
    if (savedQuery) setTestQuery(savedQuery)
  }, [])

  // Save test panel state to localStorage
  useEffect(() => {
    localStorage.setItem('wvr_test_key', testKey)
  }, [testKey])

  useEffect(() => {
    localStorage.setItem('wvr_test_query', testQuery)
  }, [testQuery])

  const handleCreateKey = async () => {
    if (!keyName.trim()) {
      toast.error('Please enter a key name')
      return
    }
    
    try {
      const result = await createMutation.mutateAsync(keyName)
      setNewKey(result.key)
      setKeyName('')
      setDialogOpen(false)
      toast.success('API key created successfully!')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to create API key')
    }
  }

  const handleRevokeKey = async (keyId: string) => {
    try {
      await revokeMutation.mutateAsync(keyId)
      toast.success('API key revoked successfully')
    } catch (error: any) {
      toast.error(error?.message || 'Failed to revoke API key')
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy')
    }
  }

  const handleRunTest = async () => {
    if (!testKey || !testQuery) {
      toast.error('Please provide both API key and query')
      return
    }

    setTesting(true)
    setTestOutput('')
    setTestError('')
    abortControllerRef.current = new AbortController()

    try {
      if (stream) {
        // Streaming SSE
        const response = await fetch(
          `${API_URL}/v1/tenants/${tenantId}/query/stream?query=${encodeURIComponent(testQuery)}`,
          {
            headers: {
              'Authorization': `Bearer ${testKey}`,
              'Accept': 'text/event-stream',
            },
            signal: abortControllerRef.current.signal,
          }
        )

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) throw new Error('No response body')

        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') continue
              
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  setTestOutput((prev) => prev + parsed.content)
                } else if (parsed.sources) {
                  setTestOutput((prev) => prev + `\n\n📊 Confidence: ${parsed.confidence}\n📚 Sources: ${parsed.sources.length}`)
                }
              } catch (e) {
                // Ignore parse errors
              }
            }
          }
        }
      } else {
        // Non-streaming POST
        const response = await fetch(`${API_URL}/v1/tenants/${tenantId}/query`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${testKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: testQuery }),
          signal: abortControllerRef.current.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const result = await response.json()
        setTestOutput(
          `${result.answer}\n\n📊 Confidence: ${result.confidence}\n⏱️ Latency: ${result.latency_ms}ms\n📚 Sources: ${result.sources.length}`
        )
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        setTestError('Request cancelled')
        toast.info('Test cancelled')
      } else {
        setTestError(error.message)
        toast.error(error.message)
      }
    } finally {
      setTesting(false)
      abortControllerRef.current = null
    }
  }

  const handleStopTest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  const handleUseNewKey = () => {
    if (newKey) {
      setTestKey(newKey)
      toast.success('API key added to test panel')
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
        <h3 className="font-semibold mb-2 text-blue-900">Bot API Endpoints</h3>
        
        <Tabs defaultValue="curl" className="w-full">
          <TabsList>
            <TabsTrigger value="curl">cURL</TabsTrigger>
            <TabsTrigger value="javascript">JavaScript</TabsTrigger>
            <TabsTrigger value="python">Python</TabsTrigger>
          </TabsList>
          
          <TabsContent value="curl" className="space-y-4">
            <div>
              <p className="text-sm text-gray-700 mb-2 font-medium">Non-streaming (POST):</p>
              <code className="block p-3 bg-white rounded font-mono text-xs border overflow-x-auto">
                POST {API_URL}/v1/tenants/{tenantId}/query
              </code>
              <pre className="mt-2 p-3 bg-white rounded border text-xs overflow-x-auto">
{`curl -X POST ${API_URL}/v1/tenants/${tenantId}/query \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is your product about?"}'`}
              </pre>
            </div>
            
            <div>
              <p className="text-sm text-gray-700 mb-2 font-medium">Streaming (SSE):</p>
              <code className="block p-3 bg-white rounded font-mono text-xs border overflow-x-auto">
                GET {API_URL}/v1/tenants/{tenantId}/query/stream?query=...
              </code>
              <pre className="mt-2 p-3 bg-white rounded border text-xs overflow-x-auto">
{`curl -N -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Accept: text/event-stream" \\
  "${API_URL}/v1/tenants/${tenantId}/query/stream?query=What+is+your+product+about"`}
              </pre>
            </div>
          </TabsContent>
          
          <TabsContent value="javascript" className="space-y-4">
            <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`// Non-streaming
const response = await fetch('${API_URL}/v1/tenants/${tenantId}/query', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ query: 'What is your product about?' }),
});
const data = await response.json();
console.log(data.answer);

// Streaming
const response = await fetch(
  '${API_URL}/v1/tenants/${tenantId}/query/stream?query=' + 
  encodeURIComponent('What is your product about?'),
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Accept': 'text/event-stream',
    },
  }
);

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.content) console.log(data.content);
    }
  }
}`}
            </pre>
          </TabsContent>
          
          <TabsContent value="python" className="space-y-4">
            <pre className="p-3 bg-white rounded border text-xs overflow-x-auto">
{`import requests

# Non-streaming
response = requests.post(
    '${API_URL}/v1/tenants/${tenantId}/query',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={'query': 'What is your product about?'}
)
data = response.json()
print(data['answer'])

# Streaming
import json

response = requests.get(
    '${API_URL}/v1/tenants/${tenantId}/query/stream',
    params={'query': 'What is your product about?'},
    headers={
        'Authorization': 'Bearer YOUR_API_KEY',
        'Accept': 'text/event-stream'
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        if 'content' in data:
            print(data['content'], end='', flush=True)`}
            </pre>
          </TabsContent>
        </Tabs>
      </div>

      {/* Create New Key */}
      <div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Create New API Key</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create API Key</DialogTitle>
              <DialogDescription>
                Give your API key a descriptive name to help you identify it later.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label htmlFor="keyName" className="block text-sm font-medium mb-2">
                  Key Name
                </label>
                <Input
                  id="keyName"
                  placeholder="e.g., Production API, Test Environment"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateKey()}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateKey} disabled={createMutation.isPending || !keyName.trim()}>
                {createMutation.isPending ? 'Creating...' : 'Create Key'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* New Key Display */}
      {newKey && (
        <div className="p-4 bg-yellow-50 border border-yellow-300 rounded-lg">
          <p className="font-semibold mb-2 text-yellow-900">
            New API Key (save this, it won't be shown again):
          </p>
          <div className="flex items-center gap-2 mb-3">
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
          <div className="flex gap-2">
            <Button
              onClick={handleUseNewKey}
              variant="secondary"
              size="sm"
            >
              Add to Test Panel
            </Button>
            <Button
              onClick={() => setNewKey(null)}
              variant="ghost"
              size="sm"
            >
              Dismiss
            </Button>
          </div>
        </div>
      )}

      {/* Keys List */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Your API Keys</h3>
        {keys.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed rounded-lg">
            <p className="text-gray-600 mb-4">No API keys yet.</p>
            <Button onClick={() => setDialogOpen(true)}>Create your first key</Button>
          </div>
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

      {/* Test Your Bot Panel */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold mb-4">Test Your Bot</h3>
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg border">
          <div>
            <label htmlFor="testKey" className="block text-sm font-medium mb-2">
              API Key
            </label>
            <Input
              id="testKey"
              type="password"
              placeholder="Paste your API key here"
              value={testKey}
              onChange={(e) => setTestKey(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="testQuery" className="block text-sm font-medium mb-2">
              Query
            </label>
            <textarea
              id="testQuery"
              className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Ask your bot a question..."
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
            />
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={stream}
                onChange={(e) => setStream(e.target.checked)}
                className="rounded"
              />
              Stream response (SSE)
            </label>
          </div>

          <div className="flex gap-2">
            {!testing ? (
              <Button onClick={handleRunTest} disabled={!testKey || !testQuery}>
                <Play className="w-4 h-4 mr-2" />
                Run Test
              </Button>
            ) : (
              <Button onClick={handleStopTest} variant="destructive">
                <Square className="w-4 h-4 mr-2" />
                Stop
              </Button>
            )}
          </div>

          {/* Output */}
          {(testOutput || testError || testing) && (
            <div>
              <label className="block text-sm font-medium mb-2">Response</label>
              <div 
                className="p-4 bg-white border rounded-md min-h-[200px] max-h-[400px] overflow-y-auto font-mono text-sm whitespace-pre-wrap"
                aria-live="polite"
              >
                {testing && !testOutput && (
                  <span className="text-gray-400">Streaming response...</span>
                )}
                {testOutput && <div>{testOutput}</div>}
                {testError && (
                  <div className="text-red-600">Error: {testError}</div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

