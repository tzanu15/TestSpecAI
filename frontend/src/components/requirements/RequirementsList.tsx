import { DeleteOutlined, EditOutlined, EyeOutlined, SearchOutlined } from '@ant-design/icons'
import { Button, Input, Popconfirm, Space, Table, Tag, Tooltip } from 'antd'
import React, { useMemo, useState } from 'react'
import { Requirement, RequirementCategory } from '../../types/requirements'

interface RequirementsListProps {
  requirements: Requirement[]
  categories: RequirementCategory[]
  loading: boolean
  onEdit: (_id: string, _data: any) => Promise<any>
  onDelete: (_id: string) => Promise<void>
  onView?: (requirement: Requirement) => void
  onSearch?: (searchTerm: string) => void
  onFilter?: (filters: { category_id?: string; source?: string }) => void
  selectedRowKeys?: string[]
  onSelectionChange?: (selectedRowKeys: string[]) => void
}

export const RequirementsList: React.FC<RequirementsListProps> = ({
  requirements,
  categories,
  loading,
  onEdit,
  onDelete,
  onView,
  onSearch,
  onFilter,
  selectedRowKeys = [],
  onSelectionChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter] = useState<string | undefined>()
  const [sourceFilter] = useState<string | undefined>()

  // Debounced search effect
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (onSearch && searchTerm) {
        onSearch(searchTerm)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [searchTerm]) // Remove onSearch from dependencies

  // Filter effect
  React.useEffect(() => {
    if (onFilter && (categoryFilter || sourceFilter)) {
      onFilter({
        category_id: categoryFilter,
        source: sourceFilter,
      })
    }
  }, [categoryFilter, sourceFilter]) // Remove onFilter from dependencies

  const categoryOptions = useMemo(() => {
    return categories.map(category => ({
      label: category.name,
      value: category.id,
    }))
  }, [categories])

  const sourceOptions = [
    { label: 'Manual', value: 'manual' },
    { label: 'Document', value: 'document' },
    { label: 'Import', value: 'import' },
  ]

  const columns = useMemo(() => [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      sorter: (a: Requirement, b: Requirement) =>
        a.title.localeCompare(b.title),
      filterDropdown: () => (
        <div style={{ padding: 8 }}>
          <Input
            placeholder="Search title"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            onPressEnter={() => onSearch?.(searchTerm)}
            style={{ width: 188, marginBottom: 8, display: 'block' }}
            prefix={<SearchOutlined />}
          />
        </div>
      ),
      filterIcon: (filtered: boolean) => (
        <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text} placement="topLeft">
          {text}
        </Tooltip>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category_id',
      key: 'category_id',
      render: (categoryId: string) => {
        const category = categories.find(cat => cat.id === categoryId)
        return <Tag color="blue">{category?.name || categoryId}</Tag>
      },
      filters: categoryOptions.map(option => ({
        text: option.label,
        value: option.value,
      })),
      onFilter: (value: any, record: Requirement) =>
        record.category_id === value,
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source: string) => (
        <Tag color={source === 'manual' ? 'green' : 'orange'}>{source}</Tag>
      ),
      filters: sourceOptions.map(option => ({
        text: option.label,
        value: option.value,
      })),
      onFilter: (value: any, record: Requirement) => record.source === value,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a: Requirement, b: Requirement) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Requirement) => (
        <Space>
          {onView && (
            <Tooltip title="View requirement details">
              <Button
                type="link"
                icon={<EyeOutlined />}
                onClick={() => onView(record)}
              >
                View
              </Button>
            </Tooltip>
          )}
          <Tooltip title="Edit requirement">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => onEdit(record.id, record)}
            >
              Edit
            </Button>
          </Tooltip>
          <Popconfirm
            title="Are you sure you want to delete this requirement?"
            description="This action cannot be undone."
            onConfirm={() => onDelete(record.id)}
            okText="Yes"
            cancelText="No"
            okType="danger"
          >
            <Tooltip title="Delete requirement">
              <Button type="link" danger icon={<DeleteOutlined />}>
                Delete
              </Button>
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ], [categories, categoryOptions, searchTerm]) // Remove function dependencies

  const rowSelection = useMemo(() => onSelectionChange
    ? {
        selectedRowKeys,
        onChange: (selectedRowKeys: React.Key[], _selectedRows: Requirement[]) => {
          onSelectionChange(selectedRowKeys as string[])
        },
        selections: [
          Table.SELECTION_ALL,
          Table.SELECTION_INVERT,
          Table.SELECTION_NONE,
        ],
      }
    : undefined, [selectedRowKeys]) // Remove onSelectionChange dependency

  return (
    <Table
      columns={columns}
      dataSource={requirements}
      loading={loading}
      rowKey="id"
      rowSelection={rowSelection}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) =>
          `${range[0]}-${range[1]} of ${total} items`,
        pageSizeOptions: ['10', '20', '50', '100'],
        showLessItems: true,
      }}
      scroll={{ x: 800 }}
      size="middle"
    />
  )
}
