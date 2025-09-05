import {
  ApiOutlined,
  DashboardOutlined,
  FileTextOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { Menu, Spin } from 'antd'
import React, { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

interface SidebarProps {
  collapsed: boolean
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(false)

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/requirements',
      icon: <FileTextOutlined />,
      label: 'Requirements',
    },
    {
      key: '/test-specs',
      icon: <FileTextOutlined />,
      label: 'Test Specifications',
    },
    {
      key: '/parameters',
      icon: <SettingOutlined />,
      label: 'Parameters',
    },
    {
      key: '/commands',
      icon: <ApiOutlined />,
      label: 'Commands',
    },
  ]

  const handleMenuClick = async ({ key }: { key: string }) => {
    if (key !== location.pathname) {
      setLoading(true)
      // Small delay to show loading state
      setTimeout(() => {
        navigate(key)
        setLoading(false)
      }, 100)
    }
  }

  return (
    <>
      <div
        style={{
          height: 32,
          margin: 16,
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold',
        }}
      >
        {collapsed ? 'TS' : 'TestSpecAI'}
      </div>
              {loading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '200px' 
          }}>
            <Spin size="small" />
          </div>
        ) : (
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
          />
        )}
    </>
  )
}
