import { apiService } from './api'

export interface DocumentUploadResponse {
  job_id: string
  status: 'processing' | 'completed' | 'failed'
  message: string
}

export interface DocumentProcessingStatus {
  job_id: string
  status: 'processing' | 'completed' | 'failed'
  requirements_extracted?: number
  requirements_saved?: number
  errors?: string[]
  processing_time?: number
  confidence_scores?: number[]
}

export class DocumentsService {
  async uploadDocument(
    file: File,
    categoryId?: string
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (categoryId) {
      formData.append('category_id', categoryId)
    }

    return apiService.post<DocumentUploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  async getProcessingStatus(jobId: string): Promise<DocumentProcessingStatus> {
    return apiService.get<DocumentProcessingStatus>(`/documents/process-status/${jobId}`)
  }

  async pollProcessingStatus(
    jobId: string,
    onUpdate: (status: DocumentProcessingStatus) => void,
    onComplete: (status: DocumentProcessingStatus) => void,
    onError: (error: string) => void,
    maxAttempts: number = 30,
    intervalMs: number = 2000
  ): Promise<void> {
    let attempts = 0

    const poll = async () => {
      try {
        attempts++
        const status = await this.getProcessingStatus(jobId)

        onUpdate(status)

        if (status.status === 'completed') {
          onComplete(status)
          return
        }

        if (status.status === 'failed') {
          onError(status.errors?.join(', ') || 'Processing failed')
          return
        }

        if (attempts >= maxAttempts) {
          onError('Processing timeout - maximum attempts reached')
          return
        }

        // Continue polling
        setTimeout(poll, intervalMs)
      } catch (error) {
        onError(error instanceof Error ? error.message : 'Unknown error occurred')
      }
    }

    poll()
  }
}

export const documentsService = new DocumentsService()
