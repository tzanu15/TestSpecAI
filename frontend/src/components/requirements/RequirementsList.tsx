import { DeleteOutlined, EditOutlined } from '@ant-design/icons'
import { Button, Popconfirm, Space, Table, Tag } from 'antd'
import React from 'react'
import { Requirement } from '../../types/requirements'

interface RequirementsListProps {
  requirements: Requirement[]
  loading: boolean
  onEdit: (_id: string, _data: any) => Promise<any>
  onDelete: (_id: string) => Promise<void>
}

export const RequirementsList: React.FC<RequirementsListProps> = ({
  requirements,
  loading,
  onEdit,
  onDelete,
}) => {
  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      sorter: (a: Requirement, b: Requirement) =>
        a.title.localeCompare(b.title),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Category',
      dataIndex: 'category_id',
      key: 'category_id',
      render: (categoryId: string) => <Tag color="blue">{categoryId}</Tag>,
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source: string) => (
        <Tag color={source === 'manual' ? 'green' : 'orange'}>{source}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Requirement) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => onEdit(record.id, record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this requirement?"
            onConfirm={() => onDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Table
      columns={columns}
      dataSource={requirements}
      loading={loading}
      rowKey="id"
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) =>
          `${range[0]}-${range[1]} of ${total} items`,
      }}
    />
  )
}
