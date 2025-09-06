import { DeleteOutlined, EditOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { Button, Card, Input, Popconfirm, Select, Space, Table, Tag } from 'antd'
import React from 'react'
import { TestSpecification } from '../../types/testSpecs'

const { Search } = Input
const { Option } = Select

interface TestSpecListProps {
  testSpecifications: TestSpecification[]
  loading: boolean
  onEdit: (id: string, data: TestSpecification) => Promise<void>
  onDelete: (id: string) => Promise<void>
  onCreate: () => void
  onDuplicate: (id: string) => Promise<void>
  onSearch?: (search: string) => void
  onFilterChange?: (filters: { functional_area?: string }) => void
}

export const TestSpecList: React.FC<TestSpecListProps> = ({
  testSpecifications,
  loading,
  onEdit,
  onDelete,
  onCreate,
  onDuplicate,
  onSearch,
  onFilterChange,
}) => {
  const functionalAreas = [
    { value: 'UDS', label: 'UDS', color: 'blue' },
    { value: 'Communication', label: 'Communication', color: 'green' },
    { value: 'ErrorHandler', label: 'Error Handler', color: 'orange' },
    { value: 'CyberSecurity', label: 'Cyber Security', color: 'red' },
  ]

  const getFunctionalAreaTag = (area: string) => {
    const functionalArea = functionalAreas.find(fa => fa.value === area)
    return functionalArea ? (
      <Tag color={functionalArea.color}>{functionalArea.label}</Tag>
    ) : (
      <Tag>{area}</Tag>
    )
  }

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: TestSpecification, b: TestSpecification) => a.name.localeCompare(b.name),
      ellipsis: true,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (description: string) => (
        <span title={description}>{description}</span>
      ),
    },
    {
      title: 'Functional Area',
      dataIndex: 'functional_area',
      key: 'functional_area',
      render: (area: string) => getFunctionalAreaTag(area),
      filters: functionalAreas.map(fa => ({
        text: fa.label,
        value: fa.value,
      })),
      onFilter: (value: string, record: TestSpecification) => record.functional_area === value,
    },
    {
      title: 'Test Steps',
      key: 'test_steps_count',
      render: (_: any, record: TestSpecification) => (
        <Tag color="geekblue">{record.test_steps?.length || 0} steps</Tag>
      ),
      sorter: (a: TestSpecification, b: TestSpecification) =>
        (a.test_steps?.length || 0) - (b.test_steps?.length || 0),
    },
    {
      title: 'Requirements',
      key: 'requirements_count',
      render: (_: any, record: TestSpecification) => (
        <Tag color="purple">{record.requirement_ids?.length || 0} linked</Tag>
      ),
      sorter: (a: TestSpecification, b: TestSpecification) =>
        (a.requirement_ids?.length || 0) - (b.requirement_ids?.length || 0),
    },
    {
      title: 'Status',
      key: 'status',
      render: (_: any, record: TestSpecification) => (
        <Tag color={record.is_active ? 'green' : 'red'}>
          {record.is_active ? 'Active' : 'Inactive'}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value: boolean, record: TestSpecification) => record.is_active === value,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a: TestSpecification, b: TestSpecification) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: TestSpecification) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onEdit(record.id, record)}
            size="small"
          >
            Edit
          </Button>
          <Button
            type="link"
            icon={<PlusOutlined />}
            onClick={() => onDuplicate(record.id)}
            size="small"
          >
            Duplicate
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this test specification?"
            description="This action cannot be undone."
            onConfirm={() => onDelete(record.id)}
            okText="Yes"
            cancelText="No"
            okType="danger"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const handleSearch = (value: string) => {
    onSearch?.(value)
  }

  const handleFilterChange = (value: string) => {
    onFilterChange?.({ functional_area: value || undefined })
  }

  return (
    <Card>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <Search
          placeholder="Search test specifications..."
          allowClear
          onSearch={handleSearch}
          style={{ width: 300 }}
          prefix={<SearchOutlined />}
        />
        <Select
          placeholder="Filter by functional area"
          allowClear
          style={{ width: 200 }}
          onChange={handleFilterChange}
        >
          {functionalAreas.map(area => (
            <Option key={area.value} value={area.value}>
              {area.label}
            </Option>
          ))}
        </Select>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onCreate}
        >
          Create Test Specification
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={testSpecifications}
        loading={loading}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `${range[0]}-${range[1]} of ${total} test specifications`,
          pageSizeOptions: ['10', '20', '50', '100'],
        }}
        scroll={{ x: 1200 }}
        size="middle"
      />
    </Card>
  )
}
