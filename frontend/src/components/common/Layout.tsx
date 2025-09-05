import { Layout as AntLayout } from 'antd'
import React, { useState, useEffect } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

const { Header: AntHeader, Sider, Content } = AntLayout

interface LayoutProps {
  children: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    const checkIsMobile = () => {
      // Auto-collapse sidebar on mobile
      if (window.innerWidth <= 768) {
        setCollapsed(true)
      }
    }

    checkIsMobile()
    window.addEventListener('resize', checkIsMobile)
    
    return () => window.removeEventListener('resize', checkIsMobile)
  }, [])

  const handleToggleCollapse = () => {
    setCollapsed(!collapsed)
  }

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} theme="dark">
        <Sidebar collapsed={collapsed} />
      </Sider>
      <AntLayout>
        <AntHeader>
          <Header collapsed={collapsed} onToggleCollapse={handleToggleCollapse} />
        </AntHeader>
        <Content
          style={{ margin: '24px 16px', padding: 24, background: '#fff' }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
