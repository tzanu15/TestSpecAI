import { Button, Card, Form, Input, Typography } from 'antd'
import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

const { Title, Text } = Typography

interface LoginFormData {
  username: string
  password: string
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as any)?.from?.pathname || '/'

  const handleLogin = (values: LoginFormData) => {
    // For now, authentication is out of scope
    // This would normally authenticate the user and redirect
    console.log('Login attempt:', values)

    // Simulate successful login
    navigate(from, { replace: true })
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, padding: '24px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Title level={2}>TestSpecAI</Title>
          <Text type="secondary">Automotive Test Specification Platform</Text>
        </div>

        <Form
          name="login"
          onFinish={handleLogin}
          layout="vertical"
          size="large"
        >
          <Form.Item
            label="Username"
            name="username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input placeholder="Enter your username" />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password placeholder="Enter your password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Sign In
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Note: Authentication is currently disabled for development
          </Text>
        </div>
      </Card>
    </div>
  )
}
