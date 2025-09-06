import { DisconnectOutlined, InfoCircleOutlined, LinkOutlined, SearchOutlined } from '@ant-design/icons'
import { Avatar, Button, Card, Input, List, message, Select, Space, Tag, Tooltip, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { requirementsService } from '../../services/requirements'
import { Requirement } from '../../types/requirements'

const { Option } = Select
const { Text, Title } = Typography

interface RequirementLinkerProps {
  linkedRequirementIds: string[]
  onRequirementsChange: (requirementIds: string[]) => void
  disabled?: boolean
}

export const RequirementLinker: React.FC<RequirementLinkerProps> = ({
  linkedRequirementIds,
  onRequirementsChange,
  disabled = false,
}) => {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()

  useEffect(() => {
    loadRequirements()
  }, [])

  const loadRequirements = async () => {
    try {
      setLoading(true)
      const requirementsData = await requirementsService.getRequirements()
      setRequirements(requirementsData)
    } catch (error) {
      message.error('Failed to load requirements')
      console.error('Error loading requirements:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredRequirements = requirements.filter(requirement => {
    const matchesSearch = !searchTerm ||
      requirement.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      requirement.description.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = !selectedCategory || requirement.category_id === selectedCategory

    return matchesSearch && matchesCategory
  })

  const linkedRequirements = requirements.filter(req =>
    linkedRequirementIds.includes(req.id)
  )

  const unlinkedRequirements = filteredRequirements.filter(req =>
    !linkedRequirementIds.includes(req.id)
  )

  const handleLinkRequirement = (requirementId: string) => {
    if (!linkedRequirementIds.includes(requirementId)) {
      onRequirementsChange([...linkedRequirementIds, requirementId])
      message.success('Requirement linked successfully')
    }
  }

  const handleUnlinkRequirement = (requirementId: string) => {
    const newLinkedIds = linkedRequirementIds.filter(id => id !== requirementId)
    onRequirementsChange(newLinkedIds)
    message.success('Requirement unlinked successfully')
  }

  const getRequirementSourceColor = (source: string) => {
    switch (source) {
      case 'manual':
        return 'green'
      case 'document':
        return 'blue'
      case 'ai_generated':
        return 'purple'
      default:
        return 'default'
    }
  }

  return (
    <Card
      title="Requirement Linking"
      size="small"
      extra={
        <Space>
          <Input
            placeholder="Search requirements..."
            prefix={<SearchOutlined />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: 200 }}
            disabled={disabled}
          />
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Linked Requirements */}
        {linkedRequirements.length > 0 && (
          <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Title level={5} style={{ margin: 0, color: '#52c41a' }}>
              Linked Requirements ({linkedRequirements.length})
            </Title>
            <List
              size="small"
              dataSource={linkedRequirements}
              renderItem={(requirement) => (
                <List.Item
                  actions={[
                    <Tooltip title="Unlink Requirement">
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DisconnectOutlined />}
                        onClick={() => handleUnlinkRequirement(requirement.id)}
                        disabled={disabled}
                      />
                    </Tooltip>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar size="small" icon={<LinkOutlined />} />}
                    title={
                      <Space>
                        <Text strong>{requirement.title}</Text>
                        <Tag color={getRequirementSourceColor(requirement.source)} size="small">
                          {requirement.source}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Text type="secondary" ellipsis style={{ maxWidth: 400 }}>
                        {requirement.description}
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* Available Requirements */}
        <Card size="small" style={{ backgroundColor: '#fafafa' }}>
          <Title level={5} style={{ margin: 0 }}>
            Available Requirements ({unlinkedRequirements.length})
          </Title>
          {unlinkedRequirements.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 16 }}>
              <Text type="secondary">
                {searchTerm ? 'No requirements match your search' : 'No available requirements to link'}
              </Text>
            </div>
          ) : (
            <List
              size="small"
              dataSource={unlinkedRequirements.slice(0, 10)} // Limit to 10 for performance
              renderItem={(requirement) => (
                <List.Item
                  actions={[
                    <Tooltip title="Link Requirement">
                      <Button
                        type="text"
                        size="small"
                        icon={<LinkOutlined />}
                        onClick={() => handleLinkRequirement(requirement.id)}
                        disabled={disabled}
                      />
                    </Tooltip>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar size="small" icon={<InfoCircleOutlined />} />}
                    title={
                      <Space>
                        <Text>{requirement.title}</Text>
                        <Tag color={getRequirementSourceColor(requirement.source)} size="small">
                          {requirement.source}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Text type="secondary" ellipsis style={{ maxWidth: 400 }}>
                        {requirement.description}
                      </Text>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>

        {/* Summary */}
        <Card size="small" style={{ backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
          <Space>
            <InfoCircleOutlined style={{ color: '#1890ff' }} />
            <Text type="secondary">
              {linkedRequirementIds.length} requirement{linkedRequirementIds.length !== 1 ? 's' : ''} linked to this test specification
            </Text>
          </Space>
        </Card>
      </Space>
    </Card>
  )
}
