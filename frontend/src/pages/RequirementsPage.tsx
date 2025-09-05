import { PlusOutlined } from '@ant-design/icons'
import { Button, Card, Space, Typography } from 'antd'
import React, { useEffect } from 'react'
import { RequirementsList } from '../components/requirements/RequirementsList'
import { useRequirements } from '../hooks/useRequirements'

const { Title } = Typography

export const RequirementsPage: React.FC = () => {
  const {
    requirements,
    loading,
    error,
    loadRequirements,
    updateRequirement,
    deleteRequirement,
  } = useRequirements()

  useEffect(() => {
    loadRequirements()
  }, [loadRequirements])

  if (error) {
    return (
      <Card>
        <Typography.Text type="danger">{error}</Typography.Text>
      </Card>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Requirements Management</Title>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>
            Add Requirement
          </Button>
        </Space>
      </div>

      <RequirementsList
        requirements={requirements}
        loading={loading}
        onEdit={updateRequirement}
        onDelete={deleteRequirement}
      />
    </div>
  )
}
