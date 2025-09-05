import { Button, Result } from 'antd'
import React from 'react'
import { useNavigate } from 'react-router-dom'

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/')
  }

  return (
    <Result
      status="404"
      title="404"
      subTitle="Sorry, the page you visited does not exist."
      extra={
        <Button type="primary" onClick={handleGoHome}>
          Back Home
        </Button>
      }
    />
  )
}
