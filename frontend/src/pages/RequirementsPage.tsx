import { PlusOutlined, UploadOutlined } from '@ant-design/icons'
import { Button, Card, Drawer, Modal, Space, Typography } from 'antd'
import React, { useCallback, useEffect, useState } from 'react'
import { AdvancedSearch, BulkOperations, DocumentUpload, RequirementDetail, RequirementForm, RequirementsList, SearchFilters } from '../components/requirements'
import { useRequirements } from '../hooks/useRequirements'
import { Requirement, RequirementCreate, RequirementUpdate } from '../types/requirements'

const { Title } = Typography

export const RequirementsPage: React.FC = () => {
  const {
    requirements,
    categories,
    loading,
    error,
    loadRequirements,
    createRequirement,
    updateRequirement,
    deleteRequirement,
    setFilters,
  } = useRequirements()

  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [isUploadModalVisible, setIsUploadModalVisible] = useState(false)
  const [isDetailDrawerVisible, setIsDetailDrawerVisible] = useState(false)
  const [editingRequirement, setEditingRequirement] = useState<Requirement | null>(null)
  const [viewingRequirement, setViewingRequirement] = useState<Requirement | null>(null)
  const [formLoading, setFormLoading] = useState(false)
  const [, setAdvancedFilters] = useState<SearchFilters>({})

  useEffect(() => {
    loadRequirements()
  }, [loadRequirements])

  const handleSearch = useCallback((searchTerm: string) => {
    setFilters({ search: searchTerm })
  }, [setFilters])

  const handleFilter = useCallback((filters: { category_id?: string; source?: string }) => {
    setFilters(filters)
  }, [setFilters])

  const handleSelectionChange = useCallback((selectedRowKeys: string[]) => {
    setSelectedRowKeys(selectedRowKeys)
  }, [])

  const handleCreateClick = () => {
    setEditingRequirement(null)
    setIsModalVisible(true)
  }

  const handleUploadClick = () => {
    setIsUploadModalVisible(true)
  }

  const handleEditClick = async (_id: string, requirement: Requirement) => {
    setEditingRequirement(requirement)
    setIsModalVisible(true)
  }

  const handleViewClick = (requirement: Requirement) => {
    setViewingRequirement(requirement)
    setIsDetailDrawerVisible(true)
  }

  const handleDetailDrawerClose = () => {
    setIsDetailDrawerVisible(false)
    setViewingRequirement(null)
  }

  const handleModalCancel = () => {
    setIsModalVisible(false)
    setEditingRequirement(null)
  }

  const handleUploadModalCancel = () => {
    setIsUploadModalVisible(false)
  }

  const handleFormSubmit = async (data: RequirementCreate | RequirementUpdate) => {
    setFormLoading(true)
    try {
      if (editingRequirement) {
        await updateRequirement(editingRequirement.id, data as RequirementUpdate)
      } else {
        await createRequirement(data as RequirementCreate)
      }
      setIsModalVisible(false)
      setEditingRequirement(null)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setFormLoading(false)
    }
  }

  const handleUploadComplete = (_requirementsCount: number) => {
    setIsUploadModalVisible(false)
    loadRequirements() // Refresh the list
  }

  const handleAdvancedSearch = (filters: SearchFilters) => {
    setAdvancedFilters(filters)
    setFilters(filters)
  }

  const handleClearAdvancedSearch = () => {
    setAdvancedFilters({})
    setFilters({})
  }

  const handleSaveSearch = (name: string, filters: SearchFilters) => {
    // In a real app, this would save to the backend
    console.log('Saving search:', name, filters)
  }

  const handleBulkDelete = async (ids: string[]) => {
    try {
      for (const id of ids) {
        await deleteRequirement(id)
      }
      setSelectedRowKeys([])
    } catch (error) {
      console.error('Bulk delete error:', error)
    }
  }

  const handleBulkUpdateStatus = async (ids: string[], status: string) => {
    try {
      for (const id of ids) {
        await updateRequirement(id, { is_active: status === 'active' })
      }
      setSelectedRowKeys([])
    } catch (error) {
      console.error('Bulk status update error:', error)
    }
  }

  const handleBulkUpdateCategory = async (ids: string[], categoryId: string) => {
    try {
      for (const id of ids) {
        await updateRequirement(id, { category_id: categoryId })
      }
      setSelectedRowKeys([])
    } catch (error) {
      console.error('Bulk category update error:', error)
    }
  }

  const handleBulkExport = (requirements: Requirement[]) => {
    // In a real app, this would generate and download a file
    console.log('Exporting requirements:', requirements)
  }

  const handleBulkDuplicate = async (requirements: Requirement[]) => {
    try {
      for (const requirement of requirements) {
        const duplicateData: RequirementCreate = {
          title: `${requirement.title} (Copy)`,
          description: requirement.description,
          category_id: requirement.category_id,
          source: 'manual',
          metadata: requirement.metadata
        }
        await createRequirement(duplicateData)
      }
      setSelectedRowKeys([])
    } catch (error) {
      console.error('Bulk duplicate error:', error)
    }
  }

  if (error) {
    return (
      <Card>
        <Typography.Text type="danger">{error}</Typography.Text>
      </Card>
    )
  }

  const selectedRequirements = requirements.filter(req => selectedRowKeys.includes(req.id))

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Requirements Management</Title>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateClick}>
            Add Requirement
          </Button>
          <Button icon={<UploadOutlined />} onClick={handleUploadClick}>
            Import from Document
          </Button>
        </Space>
      </div>

      <AdvancedSearch
        categories={categories}
        onSearch={handleAdvancedSearch}
        onClear={handleClearAdvancedSearch}
        onSaveSearch={handleSaveSearch}
        loading={loading}
      />

      {selectedRowKeys.length > 0 && (
        <BulkOperations
          selectedRequirements={selectedRequirements}
          categories={categories}
          onBulkDelete={handleBulkDelete}
          onBulkUpdateStatus={handleBulkUpdateStatus}
          onBulkUpdateCategory={handleBulkUpdateCategory}
          onBulkExport={handleBulkExport}
          onBulkDuplicate={handleBulkDuplicate}
          loading={loading}
        />
      )}

      <RequirementsList
        requirements={requirements}
        categories={categories}
        loading={loading}
        onEdit={handleEditClick}
        onDelete={deleteRequirement}
        onView={handleViewClick}
        onSearch={handleSearch}
        onFilter={handleFilter}
        selectedRowKeys={selectedRowKeys}
        onSelectionChange={handleSelectionChange}
      />

      <Modal
        title={editingRequirement ? 'Edit Requirement' : 'Create New Requirement'}
        open={isModalVisible}
        onCancel={handleModalCancel}
        footer={null}
        width={600}
        destroyOnHidden
      >
        <RequirementForm
          requirement={editingRequirement || undefined}
          categories={categories}
          loading={formLoading}
          onSubmit={handleFormSubmit}
          onCancel={handleModalCancel}
          mode={editingRequirement ? 'edit' : 'create'}
        />
      </Modal>

      <Modal
        title="Import Requirements from Document"
        open={isUploadModalVisible}
        onCancel={handleUploadModalCancel}
        footer={null}
        width={800}
        destroyOnHidden
      >
        <DocumentUpload
          onUploadSuccess={() => {}}
          onUploadError={(error) => console.error('Upload error:', error)}
          onProcessingComplete={handleUploadComplete}
          categoryId={categories[0]?.id} // Use first category as default
        />
      </Modal>

      <Drawer
        title="Requirement Details"
        placement="right"
        size="large"
        open={isDetailDrawerVisible}
        onClose={handleDetailDrawerClose}
        destroyOnHidden
      >
        {viewingRequirement && (
          <RequirementDetail
            requirement={viewingRequirement}
            category={categories.find(cat => cat.id === viewingRequirement.category_id)}
            onEdit={(requirement) => {
              handleDetailDrawerClose()
              handleEditClick(requirement.id, requirement)
            }}
            onDelete={(id) => {
              handleDetailDrawerClose()
              deleteRequirement(id)
            }}
            loading={loading}
          />
        )}
      </Drawer>
    </div>
  )
}
