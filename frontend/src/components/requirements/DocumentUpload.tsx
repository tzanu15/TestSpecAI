import { FileExcelOutlined, FilePdfOutlined, FileTextOutlined, InboxOutlined } from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { Card, Progress, Space, Typography, Upload, message } from 'antd'
import React, { useState } from 'react'
import { documentsService } from '../../services/documents'

const { Title, Text } = Typography
const { Dragger } = Upload

interface DocumentUploadProps {
  onUploadSuccess?: (file: UploadFile, jobId: string) => void
  onUploadError?: (error: string) => void
  onProcessingComplete?: (requirementsCount: number) => void
  maxFileSize?: number // in MB
  acceptedTypes?: string[]
  categoryId?: string
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  onProcessingComplete,
  maxFileSize = 10, // 10MB default
  acceptedTypes = [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
    'application/pdf', // .pdf
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
    'application/vnd.ms-excel', // .xls
  ],
  categoryId,
}) => {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<UploadFile[]>([])

  const getFileIcon = (fileType: string) => {
    if (fileType.includes('word')) return <FileTextOutlined style={{ fontSize: 24, color: '#1890ff' }} />
    if (fileType.includes('pdf')) return <FilePdfOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />
    if (fileType.includes('excel') || fileType.includes('sheet')) return <FileExcelOutlined style={{ fontSize: 24, color: '#52c41a' }} />
    return <FileTextOutlined style={{ fontSize: 24, color: '#8c8c8c' }} />
  }

  const beforeUpload = (file: File) => {
    const isValidType = acceptedTypes.includes(file.type)
    if (!isValidType) {
      const errorMsg = `File type not supported. Please upload Word (.docx), PDF (.pdf), or Excel (.xlsx, .xls) files.`
      message.error(errorMsg)
      onUploadError?.(errorMsg)
      return false
    }

    const isValidSize = file.size / 1024 / 1024 < maxFileSize
    if (!isValidSize) {
      const errorMsg = `File size must be smaller than ${maxFileSize}MB!`
      message.error(errorMsg)
      onUploadError?.(errorMsg)
      return false
    }

    return true
  }

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options

    setUploading(true)
    setUploadProgress(0)

    try {
      // Upload file to backend
      const response = await documentsService.uploadDocument(file as File, categoryId)

      setUploadProgress(50)

      const uploadedFile: UploadFile = {
        uid: Date.now().toString(),
        name: (file as File).name,
        status: 'uploading',
        type: (file as File).type,
        size: (file as File).size,
      }

      setUploadedFiles(prev => [...prev, uploadedFile])
      onSuccess?.(uploadedFile)
      onUploadSuccess?.(uploadedFile, response.job_id)

      message.success(`${(file as File).name} uploaded successfully! Processing...`)

      // Start polling for processing status
      documentsService.pollProcessingStatus(
        response.job_id,
        (status) => {
          setUploadProgress(75)
          if (status.requirements_extracted) {
            message.info(`Extracted ${status.requirements_extracted} requirements`)
          }
        },
        (status) => {
          setUploadProgress(100)
          uploadedFile.status = 'done'
          setUploadedFiles(prev =>
            prev.map(f => f.uid === uploadedFile.uid ? uploadedFile : f)
          )

          const requirementsCount = status.requirements_saved || 0
          message.success(`Processing completed! ${requirementsCount} requirements imported.`)
          onProcessingComplete?.(requirementsCount)
        },
        (error) => {
          uploadedFile.status = 'error'
          setUploadedFiles(prev =>
            prev.map(f => f.uid === uploadedFile.uid ? uploadedFile : f)
          )
          message.error(`Processing failed: ${error}`)
          onUploadError?.(error)
        }
      )

    } catch (error) {
      const errorMsg = `Failed to upload ${(file as File).name}`
      message.error(errorMsg)
      onError?.(error as Error)
      onUploadError?.(errorMsg)
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  const handleRemove = (file: UploadFile) => {
    setUploadedFiles(prev => prev.filter(f => f.uid !== file.uid))
    message.info(`${file.name} removed`)
  }

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: '.docx,.pdf,.xlsx,.xls',
    beforeUpload,
    customRequest: handleUpload,
    onRemove: handleRemove,
    fileList: uploadedFiles,
    showUploadList: {
      showPreviewIcon: true,
      showRemoveIcon: true,
      showDownloadIcon: false,
    },
  }

  return (
    <div>
      <Title level={4}>Import Requirements from Documents</Title>
      <Text type="secondary">
        Upload Word, PDF, or Excel documents to automatically extract requirements.
      </Text>

      <Card style={{ marginTop: 16 }}>
        <Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">
            Click or drag files to this area to upload
          </p>
          <p className="ant-upload-hint">
            Support for Word (.docx), PDF (.pdf), and Excel (.xlsx, .xls) files.
            Maximum file size: {maxFileSize}MB
          </p>
        </Dragger>

        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Text>Uploading...</Text>
            <Progress percent={uploadProgress} status="active" />
          </div>
        )}

        {uploadedFiles.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Title level={5}>Uploaded Files</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              {uploadedFiles.map(file => (
                <Card key={file.uid} size="small">
                  <Space>
                    {getFileIcon(file.type || '')}
                    <div>
                      <Text strong>{file.name}</Text>
                      <br />
                      <Text type="secondary">
                        {(file.size! / 1024 / 1024).toFixed(2)} MB
                      </Text>
                    </div>
                  </Space>
                </Card>
              ))}
            </Space>
          </div>
        )}
      </Card>
    </div>
  )
}
