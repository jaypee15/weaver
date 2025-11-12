'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { Upload, Key, BarChart3, LogOut } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function Dashboard() {
  const router = useRouter()
  const supabase = createClientComponentClient()
  const [user, setUser] = useState<any>(null)
  const [tenantId, setTenantId] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/')
        return
      }
      setUser(session.user)
      
      try {
        const response = await axios.get(`${API_URL}/v1/users/me`, {
          headers: { Authorization: `Bearer ${session.access_token}` }
        })
        setTenantId(response.data.tenant_id)
      } catch (error: any) {
        console.error('Error fetching user data:', error)
        // If user not found, try to complete signup
        if (error.response?.status === 404) {
          try {
            const signupResponse = await axios.post(
              `${API_URL}/v1/auth/complete-signup`,
              {},
              { headers: { Authorization: `Bearer ${session.access_token}` } }
            )
            setTenantId(signupResponse.data.tenant_id)
          } catch (signupError) {
            console.error('Error completing signup:', signupError)
          }
        }
      }
      
      setLoading(false)
    }
    getUser()
  }, [router, supabase])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold">Weaver</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <LogOut size={20} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'upload'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Upload size={20} />
            Upload Documents
          </button>
          <button
            onClick={() => setActiveTab('keys')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'keys'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Key size={20} />
            API Keys
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              activeTab === 'analytics'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <BarChart3 size={20} />
            Analytics
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'upload' && <UploadTab tenantId={tenantId} />}
          {activeTab === 'keys' && <APIKeysTab tenantId={tenantId} />}
          {activeTab === 'analytics' && <AnalyticsTab tenantId={tenantId} />}
        </div>
      </div>
    </div>
  )
}

function UploadTab({ tenantId }: { tenantId: string }) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClientComponentClient()

  // Load documents on mount and setup polling
  useEffect(() => {
    if (tenantId) {
      loadDocuments()
      // Poll for document status updates every 5 seconds
      const interval = setInterval(loadDocuments, 5000)
      return () => clearInterval(interval)
    }
  }, [tenantId])

  const loadDocuments = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.get(
        `${API_URL}/v1/tenants/${tenantId}/docs`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` }
        }
      )
      setDocuments(response.data.documents)
    } catch (error) {
      console.error('Error loading documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return
    if (!tenantId) {
      setMessage('Workspace not ready yet. Please wait...')
      return
    }

    setUploading(true)
    setMessage('')

    try {
      const { data: { session } } = await supabase.auth.getSession()
      const formData = new FormData()
      formData.append('file', file)

      await axios.post(
        `${API_URL}/v1/tenants/${tenantId}/docs:upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setMessage('Document uploaded successfully! Processing in background...')
      setFile(null)
      // Clear file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      // Reload documents immediately
      loadDocuments()
    } catch (error: any) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'pending' || status === 'processing') {
      return (
        <svg className="animate-spin h-4 w-4 inline mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )
    }
    if (status === 'completed') {
      return <span className="mr-1">✓</span>
    }
    if (status === 'failed') {
      return <span className="mr-1">✗</span>
    }
    return null
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  if (!tenantId) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
        <p className="text-gray-600">Loading your workspace...</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
      <p className="text-gray-600 mb-6">
        Upload PDF, DOCX, TXT, or HTML files to train your bot (max 200MB)
      </p>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-8">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          accept=".pdf,.docx,.doc,.txt,.html,.htm"
          className="mb-4"
        />
        
        {file && (
          <div className="mb-4">
            <p className="text-sm text-gray-600">Selected: {file.name}</p>
            <p className="text-xs text-gray-500">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        )}
        
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded-lg"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {/* Documents List */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Your Documents</h3>
        
        {loading ? (
          <p className="text-gray-600">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-600">No documents uploaded yet. Upload your first document above!</p>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(doc.status)}`}>
                        {getStatusIcon(doc.status)}
                        {doc.status}
                      </span>
                    </div>
                    <div className="mt-1 flex gap-4 text-sm text-gray-600">
                      <span>{formatFileSize(doc.size_bytes)}</span>
                      <span>Uploaded: {formatDate(doc.created_at)}</span>
                    </div>
                    {doc.error_message && (
                      <p className="mt-2 text-sm text-red-600">Error: {doc.error_message}</p>
                    )}
                    {doc.status === 'completed' && (
                      <p className="mt-2 text-sm text-green-600">
                        ✓ Ready for querying! Your bot can now answer questions about this document.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function APIKeysTab({ tenantId }: { tenantId: string }) {
  const [keys, setKeys] = useState<any[]>([])
  const [newKey, setNewKey] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const supabase = createClientComponentClient()

  useEffect(() => {
    if (tenantId) {
      loadKeys()
    }
  }, [tenantId])

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const loadKeys = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.get(
        `${API_URL}/v1/tenants/${tenantId}/api-keys`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      setKeys(response.data.keys)
    } catch (error) {
      console.error('Error loading keys:', error)
    } finally {
      setLoading(false)
    }
  }

  const createKey = async () => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const response = await axios.post(
        `${API_URL}/v1/tenants/${tenantId}/api-keys`,
        { name: `Key ${new Date().toISOString()}` },
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      setNewKey(response.data.key)
      loadKeys()
    } catch (error) {
      console.error('Error creating key:', error)
    }
  }

  const revokeKey = async (keyId: string) => {
    if (!tenantId) return
    try {
      const { data: { session } } = await supabase.auth.getSession()
      await axios.delete(
        `${API_URL}/v1/tenants/${tenantId}/api-keys/${keyId}`,
        {
          headers: { Authorization: `Bearer ${session?.access_token}` },
        }
      )
      loadKeys()
    } catch (error) {
      console.error('Error revoking key:', error)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">API Keys</h2>
      
      {/* API Endpoint Information */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold mb-2 text-blue-900">Bot API Endpoint</h3>
        <p className="text-sm text-gray-700 mb-2">Use this endpoint to query your bot:</p>
        <code className="block p-2 bg-white rounded font-mono text-sm mb-3">
          POST {API_URL}/v1/tenants/{tenantId}/query
        </code>
        <details className="text-sm">
          <summary className="cursor-pointer text-blue-700 hover:text-blue-900 font-medium mb-2">
            Show example code
          </summary>
          <div className="mt-2 p-3 bg-white rounded">
            <pre className="text-xs overflow-x-auto">
{`curl -X POST ${API_URL}/v1/tenants/${tenantId}/query \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "What is your product about?"}'`}
            </pre>
          </div>
        </details>
      </div>
      
      <button
        onClick={createKey}
        className="mb-6 bg-blue-900 hover:bg-blue-950 text-white font-semibold py-2 px-6 rounded-lg"
      >
        Create New API Key
      </button>
      
      {newKey && (
        <div className="mb-6 p-4 bg-yellow-100 border border-yellow-300 rounded-lg">
          <p className="font-semibold mb-2">New API Key (save this, it won't be shown again):</p>
          <div className="flex items-center gap-2">
            <code className="flex-1 p-2 bg-white rounded font-mono text-sm">{newKey}</code>
            <button
              onClick={() => copyToClipboard(newKey)}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </span>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          </div>
          <button
            onClick={() => setNewKey(null)}
            className="mt-2 text-sm text-gray-600 hover:text-gray-900"
          >
            Dismiss
          </button>
        </div>
      )}
      
      <div className="space-y-4">
        {keys.map((key) => (
          <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
            <div>
              <p className="font-medium">{key.name || 'Unnamed Key'}</p>
              <p className="text-sm text-gray-600">
                Created: {new Date(key.created_at).toLocaleDateString()}
              </p>
              {key.last_used_at && (
                <p className="text-sm text-gray-600">
                  Last used: {new Date(key.last_used_at).toLocaleDateString()}
                </p>
              )}
              <p className="text-sm text-gray-600">
                Rate limit: {key.rate_limit_rpm} rpm
              </p>
            </div>
            <button
              onClick={() => revokeKey(key.id)}
              disabled={key.revoked}
              className={`px-4 py-2 rounded-lg ${
                key.revoked
                  ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
            >
              {key.revoked ? 'Revoked' : 'Revoke'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function AnalyticsTab({ tenantId }: { tenantId: string }) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Analytics</h2>
      <p className="text-gray-600">
        Analytics dashboard coming soon. This will show query volume, latency, top queries, and more.
      </p>
    </div>
  )
}

