import { SaveOutlined } from '@ant-design/icons'
import { Button, Form, Input, Select, Space, Typography } from 'antd'
import React, { useEffect } from 'react'
import { Requirement, RequirementCategory, RequirementCreate, RequirementUpdate } from '../../types/requirements'

const { Title } = Typography
const { TextArea } = Input

interface RequirementFormProps {
  requirement?: Requirement
  categories: RequirementCategory[]
  loading?: boolean
  onSubmit: (data: RequirementCreate | RequirementUpdate) => Promise<void>
  onCancel?: () => void
  mode: 'create' | 'edit'
}

export const RequirementForm: React.FC<RequirementFormProps> = ({
  requirement,
  categories,
  loading = false,
  onSubmit,
  onCancel,
  mode,
}) => {
  const [form] = Form.useForm()

  useEffect(() => {
    if (requirement && mode === 'edit') {
      form.setFieldsValue({
        title: requirement.title,
        description: requirement.description,
        category_id: requirement.category_id,
        source: requirement.source,
      })
    } else {
      form.resetFields()
    }
  }, [requirement, mode, form])

  const handleSubmit = async (values: any) => {
    try {
      await onSubmit(values)
      form.resetFields()
    } catch (error) {
      // Error handling is done in the parent component
      console.error('Form submission error:', error)
    }
  }

  const categoryOptions = categories.map(category => ({
    label: category.name,
    value: category.id,
  }))

  const sourceOptions = [
    { label: 'Manual', value: 'manual' },
    { label: 'Document', value: 'document' },
    { label: 'Import', value: 'import' },
  ]

  return (
    <div>
      <Title level={3}>
        {mode === 'create' ? 'Create New Requirement' : 'Edit Requirement'}
      </Title>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          source: 'manual',
        }}
        requiredMark={false}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[
            { required: true, message: 'Please enter a title' },
            { min: 3, message: 'Title must be at least 3 characters' },
            { max: 255, message: 'Title must not exceed 255 characters' },
          ]}
        >
          <Input placeholder="Enter requirement title" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[
            { required: true, message: 'Please enter a description' },
            { min: 10, message: 'Description must be at least 10 characters' },
          ]}
        >
          <TextArea
            rows={4}
            placeholder="Enter detailed requirement description"
            showCount
            maxLength={2000}
          />
        </Form.Item>

        <Form.Item
          name="category_id"
          label="Category"
          rules={[{ required: true, message: 'Please select a category' }]}
        >
          <Select
            placeholder="Select a category"
            options={categoryOptions}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </Form.Item>

        <Form.Item
          name="source"
          label="Source"
          rules={[{ required: true, message: 'Please select a source' }]}
        >
          <Select
            placeholder="Select source"
            options={sourceOptions}
            disabled={mode === 'edit'}
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={loading}
            >
              {mode === 'create' ? 'Create Requirement' : 'Update Requirement'}
            </Button>
            {onCancel && (
              <Button onClick={onCancel}>
                Cancel
              </Button>
            )}
          </Space>
        </Form.Item>
      </Form>
    </div>
  )
}
