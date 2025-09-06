import {
    ClearOutlined,
    FilterOutlined,
    SaveOutlined,
    SearchOutlined
} from '@ant-design/icons'
import {
    Button,
    Card,
    Col,
    Collapse,
    DatePicker,
    Divider,
    Form,
    Input,
    Row,
    Select,
    Space,
    Tag,
    Tooltip
} from 'antd'
import dayjs from 'dayjs'
import React, { useEffect, useState } from 'react'
import { RequirementCategory } from '../../types/requirements'

const { Option } = Select
const { RangePicker } = DatePicker
// Panel no longer needed with items prop

interface AdvancedSearchProps {
  categories: RequirementCategory[]
  onSearch: (filters: SearchFilters) => void
  onClear: () => void
  onSaveSearch?: (name: string, filters: SearchFilters) => void
  loading?: boolean
}

export interface SearchFilters {
  text?: string
  category_id?: string
  source?: string
  status?: string
  created_by?: string
  date_range?: [string, string]
  priority?: string
}

interface SavedSearch {
  id: string
  name: string
  filters: SearchFilters
  created_at: string
}

export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  categories,
  onSearch,
  onClear,
  onSaveSearch,
  loading = false
}) => {
  const [form] = Form.useForm()
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Mock saved searches - in real app, this would come from API
  useEffect(() => {
    const mockSavedSearches: SavedSearch[] = [
      {
        id: '1',
        name: 'Active UDS Requirements',
        filters: {
          category_id: 'uds-category-id',
          status: 'active'
        },
        created_at: '2023-12-01T10:00:00Z'
      },
      {
        id: '2',
        name: 'Recent Manual Entries',
        filters: {
          source: 'manual',
          date_range: ['2023-12-01', '2023-12-31']
        },
        created_at: '2023-12-02T14:30:00Z'
      }
    ]
    setSavedSearches(mockSavedSearches)
  }, [])

  const handleSearch = (values: any) => {
    const filters: SearchFilters = {
      text: values.text,
      category_id: values.category_id,
      source: values.source,
      status: values.status,
      created_by: values.created_by,
      priority: values.priority
    }

    if (values.date_range && values.date_range.length === 2) {
      filters.date_range = [
        values.date_range[0].format('YYYY-MM-DD'),
        values.date_range[1].format('YYYY-MM-DD')
      ]
    }

    onSearch(filters)
  }

  const handleClear = () => {
    form.resetFields()
    onClear()
  }

  const handleSaveSearch = () => {
    const values = form.getFieldsValue()
    const searchName = prompt('Enter a name for this search:')

    if (searchName && onSaveSearch) {
      const filters: SearchFilters = {
        text: values.text,
        category_id: values.category_id,
        source: values.source,
        status: values.status,
        created_by: values.created_by,
        priority: values.priority
      }

      if (values.date_range && values.date_range.length === 2) {
        filters.date_range = [
          values.date_range[0].format('YYYY-MM-DD'),
          values.date_range[1].format('YYYY-MM-DD')
        ]
      }

      onSaveSearch(searchName, filters)
    }
  }

  const handleLoadSavedSearch = (savedSearch: SavedSearch) => {
    const formValues: any = {
      text: savedSearch.filters.text,
      category_id: savedSearch.filters.category_id,
      source: savedSearch.filters.source,
      status: savedSearch.filters.status,
      created_by: savedSearch.filters.created_by,
      priority: savedSearch.filters.priority
    }

    if (savedSearch.filters.date_range) {
      formValues.date_range = [
        dayjs(savedSearch.filters.date_range[0]),
        dayjs(savedSearch.filters.date_range[1])
      ]
    }

    form.setFieldsValue(formValues)
    onSearch(savedSearch.filters)
  }

  const handleDeleteSavedSearch = (searchId: string) => {
    setSavedSearches(prev => prev.filter(search => search.id !== searchId))
  }

  const getActiveFiltersCount = () => {
    try {
      const values = form.getFieldsValue()
      let count = 0

      if (values.text) count++
      if (values.category_id) count++
      if (values.source) count++
      if (values.status) count++
      if (values.created_by) count++
      if (values.priority) count++
      if (values.date_range && values.date_range.length === 2) count++

      return count
    } catch (error) {
      // Form not yet initialized
      return 0
    }
  }

  const activeFiltersCount = getActiveFiltersCount()

  return (
    <Card
      title={
        <Space>
          <FilterOutlined />
          Advanced Search
          {activeFiltersCount > 0 && (
            <Tag color="blue">{activeFiltersCount} filters active</Tag>
          )}
        </Space>
      }
      extra={
        <Space>
          <Button
            type="link"
            onClick={() => setShowAdvanced(!showAdvanced)}
            icon={<FilterOutlined />}
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced
          </Button>
          {onSaveSearch && (
            <Tooltip title="Save current search">
              <Button
                type="link"
                icon={<SaveOutlined />}
                onClick={handleSaveSearch}
                disabled={activeFiltersCount === 0}
              >
                Save Search
              </Button>
            </Tooltip>
          )}
        </Space>
      }
      style={{ marginBottom: '16px' }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSearch}
        initialValues={{
          status: 'all',
          source: 'all'
        }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              name="text"
              label="Search Text"
            >
              <Input
                placeholder="Search in title and description..."
                prefix={<SearchOutlined />}
                allowClear
              />
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} md={8}>
            <Form.Item
              name="category_id"
              label="Category"
            >
              <Select
                placeholder="Select category"
                allowClear
                showSearch
                optionFilterProp="children"
              >
                {categories.map(category => (
                  <Option key={category.id} value={category.id}>
                    {category.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={12} md={8}>
            <Form.Item
              name="source"
              label="Source"
            >
              <Select placeholder="Select source" allowClear>
                <Option value="all">All Sources</Option>
                <Option value="manual">Manual Entry</Option>
                <Option value="document">Document Import</Option>
                <Option value="import">System Import</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Collapse
          activeKey={showAdvanced ? ['advanced'] : []}
          onChange={(keys) => setShowAdvanced(keys.includes('advanced'))}
          ghost
          items={[
            {
              key: 'advanced',
              label: 'Advanced Filters',
              children: (
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={8}>
                <Form.Item
                  name="status"
                  label="Status"
                >
                  <Select placeholder="Select status" allowClear>
                    <Option value="all">All Statuses</Option>
                    <Option value="active">Active</Option>
                    <Option value="inactive">Inactive</Option>
                    <Option value="draft">Draft</Option>
                    <Option value="review">Under Review</Option>
                  </Select>
                </Form.Item>
              </Col>

              <Col xs={24} sm={12} md={8}>
                <Form.Item
                  name="created_by"
                  label="Created By"
                >
                  <Input
                    placeholder="Enter creator name"
                    allowClear
                  />
                </Form.Item>
              </Col>

              <Col xs={24} sm={12} md={8}>
                <Form.Item
                  name="priority"
                  label="Priority"
                >
                  <Select placeholder="Select priority" allowClear>
                    <Option value="high">High</Option>
                    <Option value="medium">Medium</Option>
                    <Option value="low">Low</Option>
                  </Select>
                </Form.Item>
              </Col>

              <Col xs={24} sm={12} md={8}>
                <Form.Item
                  name="date_range"
                  label="Date Range"
                >
                  <RangePicker
                    style={{ width: '100%' }}
                    placeholder={['Start Date', 'End Date']}
                  />
                </Form.Item>
              </Col>
            </Row>
              )
            }
          ]}
        />

        <Divider />

        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SearchOutlined />}
                loading={loading}
              >
                Search
              </Button>
              <Button
                onClick={handleClear}
                icon={<ClearOutlined />}
              >
                Clear
              </Button>
            </Space>
          </Col>
        </Row>
      </Form>

      {savedSearches.length > 0 && (
        <>
          <Divider />
          <div>
            <h4>Saved Searches</h4>
            <Space wrap>
              {savedSearches.map(search => (
                <Tag
                  key={search.id}
                  closable
                  onClose={() => handleDeleteSavedSearch(search.id)}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleLoadSavedSearch(search)}
                >
                  {search.name}
                </Tag>
              ))}
            </Space>
          </div>
        </>
      )}
    </Card>
  )
}
