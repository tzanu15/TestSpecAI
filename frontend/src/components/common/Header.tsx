import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons'
import { Button, Space, Typography } from 'antd'
import React from 'react'
import { Breadcrumbs } from './Breadcrumbs'

const { Title } = Typography

interface HeaderProps {
  collapsed: boolean
  onToggleCollapse: () => void
}

export const Header: React.FC<HeaderProps> = ({ collapsed, onToggleCollapse }) => {
  return (
    <div
      style={{
        padding: 0,
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingRight: 24,
      }}
    >
      <Button
        type="text"
        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        onClick={onToggleCollapse}
        style={{
          fontSize: '16px',
          width: 64,
          height: 64,
        }}
      />
      <div style={{ flex: 1, marginLeft: 16 }}>
        <Space direction="vertical" size={0}>
          <Title
            level={4}
            style={{
              margin: 0,
              display: window.innerWidth <= 576 ? 'none' : 'block'
            }}
          >
            TestSpecAI - Automotive Test Specification Platform
          </Title>
          <Title
            level={5}
            style={{
              margin: 0,
              display: window.innerWidth <= 576 ? 'block' : 'none'
            }}
          >
            TestSpecAI
          </Title>
          <Breadcrumbs />
        </Space>
      </div>
    </div>
  )
}
