import { Breadcrumb } from 'antd'
import React from 'react'
import { Link, useLocation } from 'react-router-dom'

interface BreadcrumbItem {
  title: string
  path?: string
}

export const Breadcrumbs: React.FC = () => {
  const location = useLocation()

  const getBreadcrumbItems = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean)
    const items: BreadcrumbItem[] = [
      { title: 'Home', path: '/' }
    ]

    let currentPath = ''

    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`

      // Convert segment to readable title
      const title = segment
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')

      // Don't add link to current page
      const isLast = index === pathSegments.length - 1

      items.push({
        title,
        path: isLast ? undefined : currentPath
      })
    })

    return items
  }

  const breadcrumbItems = getBreadcrumbItems()

  return (
    <Breadcrumb
      items={breadcrumbItems.map((item) => ({
        title: item.path ? (
          <Link to={item.path}>{item.title}</Link>
        ) : (
          item.title
        )
      }))}
    />
  )
}
