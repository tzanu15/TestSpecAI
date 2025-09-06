import { InfoCircleOutlined, ReloadOutlined, SaveOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { Button, Card, Col, Input, message, Row, Select, Space, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { parametersService } from '../../services/parameters'
import { Parameter } from '../../types/parameters'

const { TextArea } = Input
const { Option } = Select
const { Text, Title } = Typography

interface TestDataGeneratorProps {
  testDataDescription: Record<string, any>
  onTestDataChange: (testData: Record<string, any>) => void
  disabled?: boolean
}

interface TestDataEntry {
  parameterName: string
  value: string
  manufacturer?: string
  description?: string
}

export const TestDataGenerator: React.FC<TestDataGeneratorProps> = ({
  testDataDescription,
  onTestDataChange,
  disabled = false,
}) => {
  const [parameters, setParameters] = useState<Parameter[]>([])
  const [loading, setLoading] = useState(false)
  const [testDataEntries, setTestDataEntries] = useState<TestDataEntry[]>([])
  const [selectedManufacturer, setSelectedManufacturer] = useState<string>('BMW')

  useEffect(() => {
    loadParameters()
  }, [])

  useEffect(() => {
    // Initialize test data entries from existing testDataDescription
    const entries: TestDataEntry[] = []
    Object.entries(testDataDescription).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        entries.push({
          parameterName: key,
          value: value.value || '',
          manufacturer: value.manufacturer || '',
          description: value.description || '',
        })
      } else {
        entries.push({
          parameterName: key,
          value: String(value),
        })
      }
    })
    setTestDataEntries(entries)
  }, [testDataDescription])

  const loadParameters = async () => {
    try {
      setLoading(true)
      const parametersData = await parametersService.getParameters()
      setParameters(parametersData)
    } catch (error) {
      message.error('Failed to load parameters')
      console.error('Error loading parameters:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateTestData = () => {
    const newEntries: TestDataEntry[] = []

    // Generate test data for parameters with variants
    parameters.forEach(parameter => {
      if (parameter.has_variants && parameter.variants.length > 0) {
        // Find variant for selected manufacturer
        const variant = parameter.variants.find(v => v.manufacturer === selectedManufacturer)
        if (variant) {
          newEntries.push({
            parameterName: parameter.name,
            value: variant.value,
            manufacturer: variant.manufacturer,
            description: variant.description,
          })
        } else {
          // Use first available variant if manufacturer not found
          newEntries.push({
            parameterName: parameter.name,
            value: parameter.variants[0].value,
            manufacturer: parameter.variants[0].manufacturer,
            description: parameter.variants[0].description,
          })
        }
      } else if (parameter.default_value) {
        // Use default value for parameters without variants
        newEntries.push({
          parameterName: parameter.name,
          value: parameter.default_value,
        })
      }
    })

    setTestDataEntries(newEntries)
    message.success('Test data generated successfully')
  }

  const handleEntryChange = (index: number, field: keyof TestDataEntry, value: string) => {
    const newEntries = [...testDataEntries]
    newEntries[index] = { ...newEntries[index], [field]: value }
    setTestDataEntries(newEntries)
  }

  const handleAddEntry = () => {
    setTestDataEntries([...testDataEntries, {
      parameterName: '',
      value: '',
    }])
  }

  const handleRemoveEntry = (index: number) => {
    const newEntries = testDataEntries.filter((_, i) => i !== index)
    setTestDataEntries(newEntries)
  }

  const saveTestData = () => {
    const testData: Record<string, any> = {}

    testDataEntries.forEach(entry => {
      if (entry.parameterName && entry.value) {
        if (entry.manufacturer) {
          testData[entry.parameterName] = {
            value: entry.value,
            manufacturer: entry.manufacturer,
            description: entry.description || '',
          }
        } else {
          testData[entry.parameterName] = entry.value
        }
      }
    })

    onTestDataChange(testData)
    message.success('Test data saved successfully')
  }

  const getAvailableManufacturers = () => {
    const manufacturers = new Set<string>()
    parameters.forEach(parameter => {
      if (parameter.has_variants) {
        parameter.variants.forEach(variant => {
          manufacturers.add(variant.manufacturer)
        })
      }
    })
    return Array.from(manufacturers)
  }

  return (
    <Card
      title="Test Data Generation"
      size="small"
      extra={
        <Space>
          <Select
            placeholder="Select manufacturer"
            value={selectedManufacturer}
            onChange={setSelectedManufacturer}
            style={{ width: 150 }}
            disabled={disabled}
          >
            {getAvailableManufacturers().map(manufacturer => (
              <Option key={manufacturer} value={manufacturer}>
                {manufacturer}
              </Option>
            ))}
          </Select>
          <Button
            type="primary"
            icon={<ThunderboltOutlined />}
            onClick={generateTestData}
            loading={loading}
            disabled={disabled}
          >
            Generate
          </Button>
        </Space>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Generation Controls */}
        <Card size="small" style={{ backgroundColor: '#f0f9ff', border: '1px solid #bae6fd' }}>
          <Space>
            <InfoCircleOutlined style={{ color: '#0ea5e9' }} />
            <Text type="secondary">
              Generate test data based on parameter variants for {selectedManufacturer} or add custom entries
            </Text>
          </Space>
        </Card>

        {/* Test Data Entries */}
        <Space direction="vertical" style={{ width: '100%' }}>
          {testDataEntries.map((entry, index) => (
            <Card key={index} size="small" style={{ backgroundColor: '#f9f9f9' }}>
              <Row gutter={16} align="middle">
                <Col span={6}>
                  <Input
                    placeholder="Parameter name"
                    value={entry.parameterName}
                    onChange={(e) => handleEntryChange(index, 'parameterName', e.target.value)}
                    disabled={disabled}
                  />
                </Col>
                <Col span={6}>
                  <Input
                    placeholder="Value"
                    value={entry.value}
                    onChange={(e) => handleEntryChange(index, 'value', e.target.value)}
                    disabled={disabled}
                  />
                </Col>
                <Col span={4}>
                  <Input
                    placeholder="Manufacturer"
                    value={entry.manufacturer || ''}
                    onChange={(e) => handleEntryChange(index, 'manufacturer', e.target.value)}
                    disabled={disabled}
                  />
                </Col>
                <Col span={6}>
                  <Input
                    placeholder="Description (optional)"
                    value={entry.description || ''}
                    onChange={(e) => handleEntryChange(index, 'description', e.target.value)}
                    disabled={disabled}
                  />
                </Col>
                <Col span={2}>
                  <Button
                    type="text"
                    danger
                    onClick={() => handleRemoveEntry(index)}
                    disabled={disabled}
                  >
                    Remove
                  </Button>
                </Col>
              </Row>
            </Card>
          ))}
        </Space>

        {/* Add Entry Button */}
        <Button
          type="dashed"
          onClick={handleAddEntry}
          disabled={disabled}
          style={{ width: '100%' }}
        >
          Add Custom Entry
        </Button>

        {/* Actions */}
        <Space>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={saveTestData}
            disabled={disabled}
          >
            Save Test Data
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={generateTestData}
            loading={loading}
            disabled={disabled}
          >
            Regenerate
          </Button>
        </Space>

        {/* Summary */}
        <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
          <Space>
            <InfoCircleOutlined style={{ color: '#52c41a' }} />
            <Text type="secondary">
              {testDataEntries.length} test data entries configured
            </Text>
          </Space>
        </Card>
      </Space>
    </Card>
  )
}
