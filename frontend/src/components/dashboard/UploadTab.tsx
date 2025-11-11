import { useState, useRef } from 'react'
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatFileSize, formatDate } from '@/lib/utils'
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react'

interface UploadTabProps {
  tenantId: string
}

export default function UploadTab({ tenantId }: UploadTabProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: documents = [], isLoading } = useDocuments(tenantId)
  const uploadMutation = useUploadDocument(tenantId)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    try {
      await uploadMutation.mutateAsync(selectedFile)
      setSelectedFile(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error: any) {
      console.error('Upload error:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      processing: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200',
      failed: 'bg-red-100 text-red-800 border-red-200',
    }
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'pending' || status === 'processing') {
      return <Loader2 className="w-4 h-4 animate-spin" />
    }
    if (status === 'completed') {
      return <CheckCircle className="w-4 h-4" />
    }
    if (status === 'failed') {
      return <XCircle className="w-4 h-4" />
    }
    return <Clock className="w-4 h-4" />
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Upload Documents</h2>
        <p className="text-gray-600 mb-6">
          Upload PDF, DOCX, TXT, or HTML files to train your bot (max 200MB)
        </p>

        {/* Upload Area */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
          <Input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.doc,.txt,.html,.htm"
            className="mb-4"
          />

          {selectedFile && (
            <div className="mb-4 p-3 bg-gray-50 rounded-md">
              <p className="text-sm font-medium text-gray-700">Selected: {selectedFile.name}</p>
              <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
            </div>
          )}

          <Button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            size="lg"
          >
            {uploadMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              'Upload'
            )}
          </Button>
        </div>

        {/* Success/Error Messages */}
        {uploadMutation.isSuccess && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            Document uploaded successfully! Processing in background...
          </div>
        )}

        {uploadMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            Error: {uploadMutation.error?.message || 'Failed to upload document'}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Your Documents</h3>

        {isLoading ? (
          <p className="text-gray-600">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="text-gray-600">
            No documents uploaded yet. Upload your first document above!
          </p>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium border inline-flex items-center gap-1 ${getStatusBadge(
                          doc.status
                        )}`}
                      >
                        {getStatusIcon(doc.status)}
                        {doc.status}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>{formatFileSize(doc.size_bytes)}</span>
                      <span>Uploaded: {formatDate(doc.created_at)}</span>
                    </div>
                    {doc.error_message && (
                      <p className="mt-2 text-sm text-red-600">
                        Error: {doc.error_message}
                      </p>
                    )}
                    {doc.status === 'completed' && (
                      <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        Ready for querying! Your bot can now answer questions about this
                        document.
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

