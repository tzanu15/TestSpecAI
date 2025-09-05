import { Card, Typography } from 'antd'
import React from 'react'

const { Title, Paragraph } = Typography

export const TestSpecsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Test Specifications</Title>
        <Paragraph>Manage your automotive test specifications here.</Paragraph>
      </div>

      <Card>
        <Paragraph>
          Test specifications management will be implemented here.
        </Paragraph>
      </Card>
    </div>
  )
}
