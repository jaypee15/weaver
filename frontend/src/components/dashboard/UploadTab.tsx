import { useState, useCallback } from 'react'
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { formatFileSize, formatDate } from '@/lib/utils'
import { Loader2, CheckCircle, XCircle, Clock, Upload, FileText } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'
import type { Document as DocumentType } from '@/types'

interface UploadTabProps {
  tenantId: string
}

export default function UploadTab({ tenantId }: UploadTabProps) {
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

  const { data: documents = [], isLoading } = useDocuments(tenantId)
  const uploadMutation = useUploadDocument(tenantId)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const fileId = `${file.name}-${Date.now()}`
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }))
      
      try {
        // Simulate progress (in a real app, you'd track actual upload progress)
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            const current = prev[fileId] || 0
            if (current >= 90) {
              clearInterval(progressInterval)
              return prev
            }
            return { ...prev, [fileId]: current + 10 }
          })
        }, 200)

        await uploadMutation.mutateAsync(file)
        
        clearInterval(progressInterval)
        setUploadProgress(prev => ({ ...prev, [fileId]: 100 }))
        toast.success(`${file.name} uploaded successfully!`)
        
        // Remove from progress after a delay
        setTimeout(() => {
          setUploadProgress(prev => {
            const newProgress = { ...prev }
            delete newProgress[fileId]
            return newProgress
          })
        }, 2000)
      } catch (error: any) {
        toast.error(`Failed to upload ${file.name}: ${error?.message || 'Unknown error'}`)
        setUploadProgress(prev => {
          const newProgress = { ...prev }
          delete newProgress[fileId]
          return newProgress
        })
      }
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/html': ['.html', '.htm'],
    },
    maxSize: 200 * 1024 * 1024, // 200MB
    multiple: true,
  })

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

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-96 mb-6" />
          <Skeleton className="h-48 w-full" />
        </div>
        <div>
          <Skeleton className="h-6 w-48 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold mb-2">Upload Documents</h2>
        <p className="text-gray-600 mb-6">
          Upload PDF, DOCX, TXT, or HTML files to train your bot (max 200MB per file)
        </p>

        {/* Drag & Drop Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-lg font-medium text-blue-600">Drop files here...</p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drag & drop files here, or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, DOCX, TXT, HTML • Max 200MB per file
              </p>
            </>
          )}
        </div>

        {/* Upload Progress */}
        {Object.keys(uploadProgress).length > 0 && (
          <div className="mt-4 space-y-2">
            {Object.entries(uploadProgress).map(([fileId, progress]) => {
              const fileName = fileId.split('-').slice(0, -1).join('-')
              return (
                <div key={fileId} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">{fileName}</span>
                    <span className="text-sm text-blue-700">{progress}%</span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Your Documents</h3>

        {documents.length === 0 ? (
          <div className="text-center py-16 border-2 border-dashed rounded-lg">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-600 mb-4 text-lg">No documents uploaded yet</p>
            <p className="text-gray-500 text-sm mb-6">
              Upload your first document to start training your bot
            </p>
            <Button onClick={() => (document.querySelector('input[type="file"]') as HTMLInputElement)?.click()}>
              <Upload className="w-4 h-4 mr-2" />
              Upload Document
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc: DocumentType) => (
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
                    {doc.status === 'processing' && (
                      <p className="mt-2 text-sm text-blue-600 flex items-center gap-1">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing document... This may take a few minutes.
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

