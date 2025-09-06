import { InfoCircleOutlined, SearchOutlined } from '@ant-design/icons'
import { Card, Input, message, Select, Space, Tag, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { commandsService } from '../../services/commands'
import { CommandCategory, GenericCommand } from '../../types/commands'

const { Option } = Select
const { Text } = Typography

interface CommandSelectorProps {
  onCommandSelect: (command: GenericCommand) => void
  selectedCommandId?: string
  disabled?: boolean
  placeholder?: string
}

export const CommandSelector: React.FC<CommandSelectorProps> = ({
  onCommandSelect,
  selectedCommandId,
  disabled = false,
  placeholder = "Select a command...",
}) => {
  const [commands, setCommands] = useState<GenericCommand[]>([])
  const [categories, setCategories] = useState<CommandCategory[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()

  useEffect(() => {
    loadCommands()
    loadCategories()
  }, [])

  const loadCommands = async () => {
    try {
      setLoading(true)
      const [commandsData, categoriesData] = await Promise.all([
        commandsService.getCommands(),
        commandsService.getCategories()
      ])
      setCommands(commandsData)
      setCategories(categoriesData)
    } catch (error) {
      message.error('Failed to load commands')
      console.error('Error loading commands:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredCommands = commands.filter(command => {
    const matchesSearch = !searchTerm ||
      command.template.toLowerCase().includes(searchTerm.toLowerCase()) ||
      command.description.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = !selectedCategory || command.category_id === selectedCategory

    return matchesSearch && matchesCategory
  })

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(cat => cat.id === categoryId)
    return category?.name || 'Unknown Category'
  }

  const handleCommandChange = (commandId: string) => {
    const command = commands.find(cmd => cmd.id === commandId)
    if (command) {
      onCommandSelect(command)
    }
  }

  return (
    <Card
      title="Command Selection"
      size="small"
      extra={
        <Space>
          <Input
            placeholder="Search commands..."
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
        <Select
          placeholder={placeholder}
          value={selectedCommandId}
          onChange={handleCommandChange}
          loading={loading}
          disabled={disabled}
          style={{ width: '100%' }}
          showSearch
          filterOption={false}
          notFoundContent={loading ? 'Loading...' : 'No commands found'}
        >
          {filteredCommands.map(command => (
            <Option key={command.id} value={command.id}>
              <Space direction="vertical" size={0}>
                <Text strong>{command.template}</Text>
                <Space size={4}>
                  <Tag color="blue" size="small">
                    {getCategoryName(command.category_id)}
                  </Tag>
                  {command.required_parameters.length > 0 && (
                    <Tag color="orange" size="small">
                      {command.required_parameters.length} params
                    </Tag>
                  )}
                </Space>
                {command.description && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {command.description}
                  </Text>
                )}
              </Space>
            </Option>
          ))}
        </Select>

        {selectedCommandId && (
          <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
            <Space>
              <InfoCircleOutlined style={{ color: '#52c41a' }} />
              <Text type="secondary">
                Selected command requires {commands.find(cmd => cmd.id === selectedCommandId)?.required_parameters.length || 0} parameters
              </Text>
            </Space>
          </Card>
        )}
      </Space>
    </Card>
  )
}
