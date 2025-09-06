import {
    CalendarOutlined,
    CheckCircleOutlined,
    ClockCircleOutlined,
    CommentOutlined,
    DeleteOutlined,
    EditOutlined,
    ExclamationCircleOutlined,
    FileTextOutlined,
    HistoryOutlined,
    LinkOutlined,
    UserOutlined
} from '@ant-design/icons'
import {
    Badge,
    Button,
    Card,
    Col,
    Descriptions,
    Divider,
    Empty,
    Progress,
    Row,
    Space,
    Statistic,
    Tag,
    Timeline,
    Tooltip,
    Typography
} from 'antd'
import React from 'react'
import { Requirement, RequirementCategory } from '../../types/requirements'

const { Title, Text, Paragraph } = Typography

interface RequirementDetailProps {
  requirement: Requirement
  category?: RequirementCategory
  onEdit: (requirement: Requirement) => void
  onDelete: (id: string) => void
  onStatusChange?: (id: string, status: string) => void
  loading?: boolean
}

export const RequirementDetail: React.FC<RequirementDetailProps> = ({
  requirement,
  category,
  onEdit,
  onDelete,
  onStatusChange,
  loading = false
}) => {
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

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'manual':
        return <UserOutlined />
      case 'document':
        return <FileTextOutlined />
      case 'import':
        return <LinkOutlined />
      default:
        return <FileTextOutlined />
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

  // Mock data for demonstration - in real app, this would come from API
  const mockHistory = [
    {
      id: '1',
      action: 'Created',
      user: 'John Doe',
      timestamp: '2023-12-01T10:00:00Z',
      description: 'Requirement created'
    },
    {
      id: '2',
      action: 'Updated',
      user: 'Jane Smith',
      timestamp: '2023-12-02T14:30:00Z',
      description: 'Updated description and category'
    },
    {
      id: '3',
      action: 'Status Changed',
      user: 'Mike Johnson',
      timestamp: '2023-12-03T09:15:00Z',
      description: 'Status changed to Active'
    }
  ]

  const mockRelatedItems = [
    {
      id: '1',
      type: 'Test Specification',
      name: 'UDS Diagnostic Test Suite',
      status: 'completed',
      link: '/test-specs/1'
    },
    {
      id: '2',
      type: 'Parameter',
      name: 'Authentication Level',
      status: 'active',
      link: '/parameters/1'
    }
  ]

  const mockComments = [
    {
      id: '1',
      user: 'John Doe',
      timestamp: '2023-12-01T10:30:00Z',
      content: 'This requirement needs clarification on the authentication mechanism.'
    },
    {
      id: '2',
      user: 'Jane Smith',
      timestamp: '2023-12-02T15:00:00Z',
      content: 'Updated based on stakeholder feedback. Please review.'
    }
  ]

  const coveragePercentage = 75 // Mock data
  const testSpecCount = 2 // Mock data
  const parameterCount = 1 // Mock data

  return (
    <div style={{ padding: '24px' }}>
      {/* Header Section */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="top">
          <Col flex="auto">
            <Title level={2} style={{ margin: 0, marginBottom: '8px' }}>
              {requirement.title}
            </Title>
            <Space size="middle" wrap>
              <Tag color={getStatusColor(requirement.is_active ? 'active' : 'inactive')} icon={<CheckCircleOutlined />}>
                {requirement.is_active ? 'Active' : 'Inactive'}
              </Tag>
              <Tag color={getSourceColor(requirement.source)} icon={getSourceIcon(requirement.source)}>
                {requirement.source}
              </Tag>
              {category && (
                <Tag color="blue">
                  {category.name}
                </Tag>
              )}
            </Space>
          </Col>
          <Col>
            <Space>
              <Tooltip title="Edit Requirement">
                <Button
                  type="primary"
                  icon={<EditOutlined />}
                  onClick={() => onEdit(requirement)}
                  loading={loading}
                >
                  Edit
                </Button>
              </Tooltip>
              <Tooltip title="Delete Requirement">
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => onDelete(requirement.id)}
                  loading={loading}
                >
                  Delete
                </Button>
              </Tooltip>
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]}>
        {/* Main Content */}
        <Col xs={24} lg={16}>
          {/* Description */}
          <Card title="Description" style={{ marginBottom: '24px' }}>
            <Paragraph style={{ fontSize: '16px', lineHeight: '1.6' }}>
              {requirement.description}
            </Paragraph>
          </Card>

          {/* Metadata */}
          <Card title="Metadata" style={{ marginBottom: '24px' }}>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="ID" span={1}>
                <Text code>{requirement.id}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="Category" span={1}>
                {category ? category.name : 'Uncategorized'}
              </Descriptions.Item>
              <Descriptions.Item label="Source" span={1}>
                <Tag color={getSourceColor(requirement.source)} icon={getSourceIcon(requirement.source)}>
                  {requirement.source}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Status" span={1}>
                <Tag color={getStatusColor(requirement.is_active ? 'active' : 'inactive')}>
                  {requirement.is_active ? 'Active' : 'Inactive'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Created By" span={1}>
                <Space>
                  <UserOutlined />
                  {requirement.created_by}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Created At" span={1}>
                <Space>
                  <CalendarOutlined />
                  {new Date(requirement.created_at).toLocaleDateString()}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Last Updated" span={2}>
                <Space>
                  <ClockCircleOutlined />
                  {new Date(requirement.updated_at).toLocaleString()}
                </Space>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Related Items */}
          <Card title="Related Items" style={{ marginBottom: '24px' }}>
            {mockRelatedItems.length > 0 ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                {mockRelatedItems.map((item) => (
                  <Card key={item.id} size="small" hoverable>
                    <Row justify="space-between" align="middle">
                      <Col>
                        <Space>
                          <Badge status={item.status === 'completed' ? 'success' : 'processing'} />
                          <Text strong>{item.name}</Text>
                          <Tag>{item.type}</Tag>
                        </Space>
                      </Col>
                      <Col>
                        <Button type="link" size="small">
                          View
                        </Button>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </Space>
            ) : (
              <Empty description="No related items found" />
            )}
          </Card>

          {/* Comments */}
          <Card title="Comments" extra={<Button type="link" icon={<CommentOutlined />}>Add Comment</Button>}>
            {mockComments.length > 0 ? (
              <Timeline>
                {mockComments.map((comment) => (
                  <Timeline.Item
                    key={comment.id}
                    dot={<CommentOutlined style={{ fontSize: '16px' }} />}
                  >
                    <Card size="small">
                      <Row justify="space-between" align="top">
                        <Col>
                          <Text strong>{comment.user}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            {new Date(comment.timestamp).toLocaleString()}
                          </Text>
                        </Col>
                      </Row>
                      <Divider style={{ margin: '8px 0' }} />
                      <Paragraph style={{ margin: 0 }}>
                        {comment.content}
                      </Paragraph>
                    </Card>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <Empty description="No comments yet" />
            )}
          </Card>
        </Col>

        {/* Sidebar */}
        <Col xs={24} lg={8}>
          {/* Coverage Statistics */}
          <Card title="Coverage Statistics" style={{ marginBottom: '24px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Statistic
                title="Test Coverage"
                value={coveragePercentage}
                suffix="%"
                valueStyle={{ color: coveragePercentage > 80 ? '#3f8600' : coveragePercentage > 60 ? '#cf1322' : '#faad14' }}
              />
              <Progress
                percent={coveragePercentage}
                strokeColor={coveragePercentage > 80 ? '#3f8600' : coveragePercentage > 60 ? '#cf1322' : '#faad14'}
                showInfo={false}
              />
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="Test Specs"
                    value={testSpecCount}
                    prefix={<FileTextOutlined />}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Parameters"
                    value={parameterCount}
                    prefix={<LinkOutlined />}
                  />
                </Col>
              </Row>
            </Space>
          </Card>

          {/* History */}
          <Card title="History" extra={<Button type="link" icon={<HistoryOutlined />}>View All</Button>}>
            {mockHistory.length > 0 ? (
              <Timeline size="small">
                {mockHistory.slice(0, 3).map((item) => (
                  <Timeline.Item
                    key={item.id}
                    dot={<ClockCircleOutlined style={{ fontSize: '12px' }} />}
                  >
                    <div>
                      <Text strong style={{ fontSize: '12px' }}>{item.action}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '11px' }}>
                        by {item.user}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '10px' }}>
                        {new Date(item.timestamp).toLocaleString()}
                      </Text>
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <Empty description="No history available" size="small" />
            )}
          </Card>

          {/* Quick Actions */}
          <Card title="Quick Actions">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                block
                icon={<EditOutlined />}
                onClick={() => onEdit(requirement)}
                loading={loading}
              >
                Edit Requirement
              </Button>
              <Button
                block
                icon={<LinkOutlined />}
                onClick={() => console.log('Link to test specs')}
              >
                View Test Specifications
              </Button>
              <Button
                block
                icon={<FileTextOutlined />}
                onClick={() => console.log('Export requirement')}
              >
                Export Requirement
              </Button>
              {onStatusChange && (
                <Button
                  block
                  icon={requirement.is_active ? <ExclamationCircleOutlined /> : <CheckCircleOutlined />}
                  onClick={() => onStatusChange(requirement.id, requirement.is_active ? 'inactive' : 'active')}
                  loading={loading}
                >
                  {requirement.is_active ? 'Deactivate' : 'Activate'}
                </Button>
              )}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
