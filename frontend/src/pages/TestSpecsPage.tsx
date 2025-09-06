import { Typography, message } from 'antd'
import React, { useState } from 'react'
import { TestSpecEditor, TestSpecList } from '../components/testSpecs'
import { useTestSpecs } from '../hooks/useTestSpecs'
import { TestSpecification, TestSpecificationCreate, TestSpecificationUpdate } from '../types/testSpecs'

const { Title, Paragraph } = Typography

export const TestSpecsPage: React.FC = () => {
  const {
    testSpecifications,
    loading,
    error,
    loadTestSpecifications,
    createTestSpecification,
    updateTestSpecification,
    deleteTestSpecification,
    duplicateTestSpecification,
    searchTestSpecifications,
    filterTestSpecifications,
  } = useTestSpecs()

  const [isCreating] = useState(false)
  const [editorVisible, setEditorVisible] = useState(false)
  const [editingTestSpec, setEditingTestSpec] = useState<TestSpecification | null>(null)

  const handleCreate = () => {
    setEditingTestSpec(null)
    setEditorVisible(true)
  }

  const handleEdit = async (_id: string, data: TestSpecification) => {
    setEditingTestSpec(data)
    setEditorVisible(true)
  }

  const handleSave = async (data: TestSpecificationCreate | TestSpecificationUpdate) => {
    try {
      if (editingTestSpec) {
        await updateTestSpecification(editingTestSpec.id, data as TestSpecificationUpdate)
      } else {
        await createTestSpecification(data as TestSpecificationCreate)
      }
      setEditorVisible(false)
      setEditingTestSpec(null)
    } catch (error) {
      throw error // Let the editor handle the error display
    }
  }

  const handleCloseEditor = () => {
    setEditorVisible(false)
    setEditingTestSpec(null)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteTestSpecification(id)
      message.success('Test specification deleted successfully')
    } catch (error) {
      message.error('Failed to delete test specification')
    }
  }

  const handleDuplicate = async (id: string) => {
    try {
      await duplicateTestSpecification(id)
      message.success('Test specification duplicated successfully')
    } catch (error) {
      message.error('Failed to duplicate test specification')
    }
  }

  const handleSearch = (search: string) => {
    if (search.trim()) {
      searchTestSpecifications(search)
    } else {
      loadTestSpecifications()
    }
  }

  const handleFilterChange = (filters: { functional_area?: string }) => {
    filterTestSpecifications(filters)
  }

  if (error) {
    return (
      <div>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>Test Specifications</Title>
          <Paragraph>Manage your automotive test specifications here.</Paragraph>
        </div>
        <div style={{ textAlign: 'center', padding: 24 }}>
          <Typography.Text type="danger">{error}</Typography.Text>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Test Specifications</Title>
        <Paragraph>Manage your automotive test specifications here.</Paragraph>
      </div>

      <TestSpecList
        testSpecifications={testSpecifications}
        loading={loading || isCreating}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onCreate={handleCreate}
        onDuplicate={handleDuplicate}
        onSearch={handleSearch}
        onFilterChange={handleFilterChange}
      />

      <TestSpecEditor
        visible={editorVisible}
        onClose={handleCloseEditor}
        onSave={handleSave}
        testSpec={editingTestSpec}
        loading={loading}
      />
    </div>
  )
}
