import { InfoCircleOutlined, SearchOutlined } from '@ant-design/icons'
import { Card, Input, message, Radio, Select, Space, Tag, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { parametersService } from '../../services/parameters'
import { Parameter, ParameterCategory } from '../../types/parameters'

const { Option } = Select
const { Text } = Typography

interface ParameterSelectorProps {
  parameterIds: string[]
  onParametersChange: (parameters: Record<string, string>) => void
  disabled?: boolean
}

export const ParameterSelector: React.FC<ParameterSelectorProps> = ({
  parameterIds,
  onParametersChange,
  disabled = false,
}) => {
  const [parameters, setParameters] = useState<Parameter[]>([])
  const [categories, setCategories] = useState<ParameterCategory[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()
  const [parameterValues, setParameterValues] = useState<Record<string, string>>({})

  useEffect(() => {
    loadParameters()
    loadCategories()
  }, [])

  useEffect(() => {
    // Initialize parameter values when parameterIds change
    const initialValues: Record<string, string> = {}
    parameterIds.forEach(paramId => {
      const param = parameters.find(p => p.id === paramId)
      if (param && !parameterValues[paramId]) {
        if (param.has_variants && param.variants.length > 0) {
          initialValues[paramId] = param.variants[0].value
        } else if (param.default_value) {
          initialValues[paramId] = param.default_value
        }
      }
    })
    if (Object.keys(initialValues).length > 0) {
      setParameterValues(prev => ({ ...prev, ...initialValues }))
      onParametersChange({ ...parameterValues, ...initialValues })
    }
  }, [parameterIds, parameters])

  const loadParameters = async () => {
    try {
      setLoading(true)
      const [parametersData, categoriesData] = await Promise.all([
        parametersService.getParameters(),
        parametersService.getCategories()
      ])
      setParameters(parametersData)
      setCategories(categoriesData)
    } catch (error) {
      message.error('Failed to load parameters')
      console.error('Error loading parameters:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredParameters = parameters.filter(parameter => {
    const matchesSearch = !searchTerm ||
      parameter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      parameter.description.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = !selectedCategory || parameter.category_id === selectedCategory

    return matchesSearch && matchesCategory
  })

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId)
    return category?.name || 'Unknown Category'
  }

  const handleParameterValueChange = (parameterId: string, value: string) => {
    const newValues = { ...parameterValues, [parameterId]: value }
    setParameterValues(newValues)
    onParametersChange(newValues)
  }

  const getParameterDisplayName = (parameterId: string) => {
    const parameter = parameters.find(p => p.id === parameterId)
    return parameter?.name || 'Unknown Parameter'
  }

  const getParameterDescription = (parameterId: string) => {
    const parameter = parameters.find(p => p.id === parameterId)
    return parameter?.description || ''
  }

  const getParameterVariants = (parameterId: string) => {
    const parameter = parameters.find(p => p.id === parameterId)
    return parameter?.variants || []
  }

  const getParameterDefaultValue = (parameterId: string) => {
    const parameter = parameters.find(p => p.id === parameterId)
    return parameter?.default_value || ''
  }

  const hasVariants = (parameterId: string) => {
    const parameter = parameters.find(p => p.id === parameterId)
    return parameter?.has_variants || false
  }

  if (parameterIds.length === 0) {
    return (
      <Card size="small" style={{ textAlign: 'center', backgroundColor: '#fafafa' }}>
        <Text type="secondary">No parameters required for the selected command</Text>
      </Card>
    )
  }

  return (
    <Card
      title="Parameter Configuration"
      size="small"
      extra={
        <Space>
          <Input
            placeholder="Search parameters..."
            prefix={<SearchOutlined />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: 200 }}
            disabled={disabled}
          />
          <Select
            placeholder="Filter by category"
            value={selectedCategory}
            onChange={setSelectedCategory}
            allowClear
            style={{ width: 150 }}
            disabled={disabled}
          >
            {categories.map(category => (
              <Option key={category.id} value={category.id}>
                {category.name}
              </Option>
            ))}
          </Select>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {parameterIds.map(parameterId => {
          const parameter = parameters.find(p => p.id === parameterId)
          if (!parameter) return null

          return (
            <Card key={parameterId} size="small" style={{ backgroundColor: '#f9f9f9' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space>
                  <Text strong>{parameter.name}</Text>
                  <Tag color="blue" size="small">
                    {getCategoryName(parameter.category_id)}
                  </Tag>
                  {parameter.has_variants && (
                    <Tag color="green" size="small">
                      Has Variants
                    </Tag>
                  )}
                </Space>

                {parameter.description && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {parameter.description}
                  </Text>
                )}

                {hasVariants(parameterId) ? (
                  <Radio.Group
                    value={parameterValues[parameterId]}
                    onChange={(e) => handleParameterValueChange(parameterId, e.target.value)}
                    disabled={disabled}
                  >
                    <Space direction="vertical">
                      {getParameterVariants(parameterId).map(variant => (
                        <Radio key={variant.id} value={variant.value}>
                          <Space>
                            <Text>{variant.value}</Text>
                            <Tag color="orange" size="small">{variant.manufacturer}</Tag>
                            {variant.description && (
                              <Text type="secondary" style={{ fontSize: '11px' }}>
                                {variant.description}
                              </Text>
                            )}
                          </Space>
                        </Radio>
                      ))}
                    </Space>
                  </Radio.Group>
                ) : (
                  <Input
                    placeholder={`Enter value for ${parameter.name}`}
                    value={parameterValues[parameterId] || getParameterDefaultValue(parameterId)}
                    onChange={(e) => handleParameterValueChange(parameterId, e.target.value)}
                    disabled={disabled}
                  />
                )}
              </Space>
            </Card>
          )
        })}

        {parameterIds.length > 0 && (
          <Card size="small" style={{ backgroundColor: '#e6f7ff', border: '1px solid #91d5ff' }}>
            <Space>
              <InfoCircleOutlined style={{ color: '#1890ff' }} />
              <Text type="secondary">
                Configure {parameterIds.length} required parameter{parameterIds.length > 1 ? 's' : ''}
              </Text>
            </Space>
          </Card>
        )}
      </Space>
    </Card>
  )
}
