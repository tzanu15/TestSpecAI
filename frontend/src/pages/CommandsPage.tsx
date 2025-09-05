import { Card, Typography } from 'antd'
import React from 'react'

const { Title, Paragraph } = Typography

export const CommandsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Commands</Title>
        <Paragraph>Manage your generic commands here.</Paragraph>
      </div>

      <Card>
        <Paragraph>Commands management will be implemented here.</Paragraph>
      </Card>
    </div>
  )
}
