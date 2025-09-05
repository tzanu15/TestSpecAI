import {
    ApiOutlined,
    DashboardOutlined,
    FileTextOutlined,
    SettingOutlined,
} from '@ant-design/icons'
import { Card, Col, Row, Statistic, Typography } from 'antd'
import React from 'react'

const { Title, Paragraph } = Typography

export const DashboardPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <DashboardOutlined style={{ marginRight: 8 }} />
          Dashboard
        </Title>
        <Paragraph>
          Welcome to TestSpecAI - Your automotive test specification management
          platform.
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Requirements"
              value={0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Test Specifications"
              value={0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Parameters"
              value={0}
              prefix={<SettingOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Commands"
              value={0}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Recent Activity" size="small">
            <Paragraph>No recent activity to display.</Paragraph>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Quick Actions" size="small">
            <Paragraph>Quick actions will be available here.</Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
