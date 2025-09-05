import { Card, Typography } from 'antd'
import React from 'react'

const { Title, Paragraph } = Typography

export const ParametersPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Parameters</Title>
        <Paragraph>Manage your test parameters and variants here.</Paragraph>
      </div>

      <Card>
        <Paragraph>Parameters management will be implemented here.</Paragraph>
      </Card>
    </div>
  )
}
