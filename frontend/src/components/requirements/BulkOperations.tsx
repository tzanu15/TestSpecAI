import {
    CheckCircleOutlined,
    CopyOutlined,
    DeleteOutlined,
    EditOutlined,
    ExclamationCircleOutlined,
    ExportOutlined,
    TagOutlined
} from '@ant-design/icons'
import {
    Button,
    Card,
    Col,
    Divider,
    Form,
    Input,
    message,
    Modal,
    Popconfirm,
    Row,
    Select,
    Space,
    Statistic,
    Tag,
    Tooltip
} from 'antd'
import React, { useState } from 'react'
import { Requirement, RequirementCategory } from '../../types/requirements'

const { Option } = Select
const { TextArea } = Input

interface BulkOperationsProps {
  selectedRequirements: Requirement[]
  categories: RequirementCategory[]
  onBulkDelete: (ids: string[]) => Promise<void>
  onBulkUpdateStatus: (ids: string[], status: string) => Promise<void>
  onBulkUpdateCategory: (ids: string[], categoryId: string) => Promise<void>
  onBulkExport: (requirements: Requirement[]) => void
  onBulkDuplicate: (requirements: Requirement[]) => Promise<void>
  loading?: boolean
}

export const BulkOperations: React.FC<BulkOperationsProps> = ({
  selectedRequirements,
  categories,
  onBulkDelete,
  onBulkUpdateStatus,
  onBulkUpdateCategory,
  onBulkExport,
  onBulkDuplicate,
  loading = false
}) => {
  const [isStatusModalVisible, setIsStatusModalVisible] = useState(false)
  const [isCategoryModalVisible, setIsCategoryModalVisible] = useState(false)
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false)
  const [isDuplicateModalVisible, setIsDuplicateModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [duplicateForm] = Form.useForm()

  const selectedCount = selectedRequirements.length

  if (selectedCount === 0) {
    return null
  }

  const handleBulkDelete = async () => {
    try {
      const ids = selectedRequirements.map(req => req.id)
      await onBulkDelete(ids)
      setIsDeleteModalVisible(false)
      message.success(`Successfully deleted ${selectedCount} requirements`)
    } catch (error) {
      message.error('Failed to delete requirements')
    }
  }

  const handleBulkStatusUpdate = async (values: { status: string }) => {
    try {
      const ids = selectedRequirements.map(req => req.id)
      await onBulkUpdateStatus(ids, values.status)
      setIsStatusModalVisible(false)
      form.resetFields()
      message.success(`Successfully updated status for ${selectedCount} requirements`)
    } catch (error) {
      message.error('Failed to update status')
    }
  }

  const handleBulkCategoryUpdate = async (values: { category_id: string }) => {
    try {
      const ids = selectedRequirements.map(req => req.id)
      await onBulkUpdateCategory(ids, values.category_id)
      setIsCategoryModalVisible(false)
      form.resetFields()
      message.success(`Successfully updated category for ${selectedCount} requirements`)
    } catch (error) {
      message.error('Failed to update category')
    }
  }

  const handleBulkDuplicate = async (values: { suffix: string }) => {
    try {
      await onBulkDuplicate(selectedRequirements)
      setIsDuplicateModalVisible(false)
      duplicateForm.resetFields()
      message.success(`Successfully duplicated ${selectedCount} requirements`)
    } catch (error) {
      message.error('Failed to duplicate requirements')
    }
  }

  const handleBulkExport = () => {
    onBulkExport(selectedRequirements)
    message.success(`Exported ${selectedCount} requirements`)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green'
      case 'inactive':
        return 'red'
      case 'draft':
        return 'orange'
      case 'review':
        return 'blue'
      default:
        return 'default'
    }
  }

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'manual':
        return 'green'
      case 'document':
        return 'blue'
      case 'import':
        return 'purple'
      default:
        return 'default'
    }
  }

  // Calculate statistics
  const statusCounts = selectedRequirements.reduce((acc, req) => {
    const status = req.is_active ? 'active' : 'inactive'
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const sourceCounts = selectedRequirements.reduce((acc, req) => {
    acc[req.source] = (acc[req.source] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const categoryCounts = selectedRequirements.reduce((acc, req) => {
    const category = categories.find(cat => cat.id === req.category_id)
    const categoryName = category ? category.name : 'Uncategorized'
    acc[categoryName] = (acc[categoryName] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <Card
      title={
        <Space>
          <EditOutlined />
          Bulk Operations
          <Tag color="blue">{selectedCount} selected</Tag>
        </Space>
      }
      style={{ marginBottom: '16px' }}
    >
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Statistic
            title="Selected Requirements"
            value={selectedCount}
            prefix={<CheckCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Active"
            value={statusCounts.active || 0}
            valueStyle={{ color: '#3f8600' }}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Inactive"
            value={statusCounts.inactive || 0}
            valueStyle={{ color: '#cf1322' }}
          />
        </Col>
      </Row>

      <Divider />

      <Space wrap>
        <Tooltip title="Update status for selected requirements">
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => setIsStatusModalVisible(true)}
            loading={loading}
          >
            Update Status
          </Button>
        </Tooltip>

        <Tooltip title="Update category for selected requirements">
          <Button
            icon={<TagOutlined />}
            onClick={() => setIsCategoryModalVisible(true)}
            loading={loading}
          >
            Update Category
          </Button>
        </Tooltip>

        <Tooltip title="Duplicate selected requirements">
          <Button
            icon={<CopyOutlined />}
            onClick={() => setIsDuplicateModalVisible(true)}
            loading={loading}
          >
            Duplicate
          </Button>
        </Tooltip>

        <Tooltip title="Export selected requirements">
          <Button
            icon={<ExportOutlined />}
            onClick={handleBulkExport}
          >
            Export
          </Button>
        </Tooltip>

        <Popconfirm
          title={`Delete ${selectedCount} requirements?`}
          description="This action cannot be undone. Are you sure you want to delete all selected requirements?"
          onConfirm={() => setIsDeleteModalVisible(true)}
          okText="Yes, Delete"
          cancelText="Cancel"
          okType="danger"
        >
          <Tooltip title="Delete selected requirements">
            <Button
              danger
              icon={<DeleteOutlined />}
              loading={loading}
            >
              Delete
            </Button>
          </Tooltip>
        </Popconfirm>
      </Space>

      <Divider />

      <div>
        <h4>Selection Summary</h4>
        <Row gutter={[16, 8]}>
          <Col span={8}>
            <div>
              <strong>Status Distribution:</strong>
              <div style={{ marginTop: '4px' }}>
                {Object.entries(statusCounts).map(([status, count]) => (
                  <Tag key={status} color={getStatusColor(status)} style={{ marginBottom: '4px' }}>
                    {status}: {count}
                  </Tag>
                ))}
              </div>
            </div>
          </Col>
          <Col span={8}>
            <div>
              <strong>Source Distribution:</strong>
              <div style={{ marginTop: '4px' }}>
                {Object.entries(sourceCounts).map(([source, count]) => (
                  <Tag key={source} color={getSourceColor(source)} style={{ marginBottom: '4px' }}>
                    {source}: {count}
                  </Tag>
                ))}
              </div>
            </div>
          </Col>
          <Col span={8}>
            <div>
              <strong>Category Distribution:</strong>
              <div style={{ marginTop: '4px' }}>
                {Object.entries(categoryCounts).map(([category, count]) => (
                  <Tag key={category} color="blue" style={{ marginBottom: '4px' }}>
                    {category}: {count}
                  </Tag>
                ))}
              </div>
            </div>
          </Col>
        </Row>
      </div>

      {/* Status Update Modal */}
      <Modal
        title="Update Status"
        open={isStatusModalVisible}
        onCancel={() => setIsStatusModalVisible(false)}
        footer={null}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleBulkStatusUpdate}
        >
          <Form.Item
            name="status"
            label="New Status"
            rules={[{ required: true, message: 'Please select a status' }]}
          >
            <Select placeholder="Select status">
              <Option value="active">Active</Option>
              <Option value="inactive">Inactive</Option>
              <Option value="draft">Draft</Option>
              <Option value="review">Under Review</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                Update Status
              </Button>
              <Button onClick={() => setIsStatusModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Category Update Modal */}
      <Modal
        title="Update Category"
        open={isCategoryModalVisible}
        onCancel={() => setIsCategoryModalVisible(false)}
        footer={null}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleBulkCategoryUpdate}
        >
          <Form.Item
            name="category_id"
            label="New Category"
            rules={[{ required: true, message: 'Please select a category' }]}
          >
            <Select placeholder="Select category">
              {categories.map(category => (
                <Option key={category.id} value={category.id}>
                  {category.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                Update Category
              </Button>
              <Button onClick={() => setIsCategoryModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Duplicate Modal */}
      <Modal
        title="Duplicate Requirements"
        open={isDuplicateModalVisible}
        onCancel={() => setIsDuplicateModalVisible(false)}
        footer={null}
        destroyOnHidden
      >
        <Form
          form={duplicateForm}
          layout="vertical"
          onFinish={handleBulkDuplicate}
        >
          <Form.Item
            name="suffix"
            label="Suffix for duplicated requirements"
            rules={[{ required: true, message: 'Please enter a suffix' }]}
            initialValue=" (Copy)"
          >
            <Input placeholder="e.g., (Copy), (Duplicate)" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                Duplicate
              </Button>
              <Button onClick={() => setIsDuplicateModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        title="Confirm Deletion"
        open={isDeleteModalVisible}
        onCancel={() => setIsDeleteModalVisible(false)}
        footer={null}
        destroyOnHidden
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <ExclamationCircleOutlined style={{ fontSize: '48px', color: '#ff4d4f', marginBottom: '16px' }} />
          <h3>Are you sure you want to delete {selectedCount} requirements?</h3>
          <p style={{ color: '#666' }}>
            This action cannot be undone. All selected requirements will be permanently deleted.
          </p>
          <Space style={{ marginTop: '24px' }}>
            <Button
              danger
              onClick={handleBulkDelete}
              loading={loading}
            >
              Yes, Delete All
            </Button>
            <Button onClick={() => setIsDeleteModalVisible(false)}>
              Cancel
            </Button>
          </Space>
        </div>
      </Modal>
    </Card>
  )
}
