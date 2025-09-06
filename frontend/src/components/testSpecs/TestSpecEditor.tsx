import { CloseOutlined, SaveOutlined } from '@ant-design/icons'
import {
  Button,
  Col,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Tabs,
  Typography,
  message
} from 'antd'
import React, { useEffect, useState } from 'react'
import { TestSpecification, TestSpecificationCreate, TestSpecificationUpdate, TestStep } from '../../types/testSpecs'
import { RequirementLinker } from './RequirementLinker'
import { TestDataGenerator } from './TestDataGenerator'
import { TestStepBuilder } from './TestStepBuilder'

const { TextArea } = Input
const { Option } = Select
const { Title } = Typography
const { TabPane } = Tabs

interface TestSpecEditorProps {
  visible: boolean
  onClose: () => void
  onSave: (data: TestSpecificationCreate | TestSpecificationUpdate) => Promise<void>
  testSpec?: TestSpecification | null
  loading?: boolean
}

// Form validation rules
const formRules = {
  name: [
    { required: true, message: 'Name is required' },
    { max: 255, message: 'Name must be less than 255 characters' }
  ],
  description: [
    { required: true, message: 'Description is required' }
  ],
  functional_area: [
    { required: true, message: 'Functional area is required' }
  ],
  precondition: [
    { required: true, message: 'Precondition is required' }
  ],
  postcondition: [
    { required: true, message: 'Postcondition is required' }
  ]
}

const functionalAreas = [
  { value: 'UDS', label: 'UDS' },
  { value: 'Communication', label: 'Communication' },
  { value: 'ErrorHandler', label: 'Error Handler' },
  { value: 'CyberSecurity', label: 'Cyber Security' },
]

export const TestSpecEditor: React.FC<TestSpecEditorProps> = ({
  visible,
  onClose,
  onSave,
  testSpec,
  loading = false,
}) => {
  const [form] = Form.useForm()
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [testSteps, setTestSteps] = useState<TestStep[]>(testSpec?.test_steps || [])
  const [linkedRequirementIds, setLinkedRequirementIds] = useState<string[]>(testSpec?.requirement_ids || [])
  const [testDataDescription, setTestDataDescription] = useState<Record<string, any>>(testSpec?.test_data_description || {})

  const isEditing = !!testSpec

  // Auto-save functionality
  useEffect(() => {
    if (!autoSaveEnabled || !visible) return

    const autoSaveInterval = setInterval(() => {
      if (hasChanges()) {
        handleAutoSave()
      }
    }, 30000) // Auto-save every 30 seconds

    return () => clearInterval(autoSaveInterval)
  }, [autoSaveEnabled, visible])

  // Reset form when testSpec changes
  useEffect(() => {
    if (testSpec) {
      setTestSteps(testSpec.test_steps || [])
      setLinkedRequirementIds(testSpec.requirement_ids || [])
      setTestDataDescription(testSpec.test_data_description || {})
      form.setFieldsValue({
        name: testSpec.name,
        description: testSpec.description,
        functional_area: testSpec.functional_area,
        precondition: testSpec.precondition,
        postcondition: testSpec.postcondition,
      })
    } else {
      setTestSteps([])
      setLinkedRequirementIds([])
      setTestDataDescription({})
      form.resetFields()
    }
  }, [testSpec, form])

  const hasChanges = () => {
    if (!testSpec) return true

    const formValues = form.getFieldsValue()
    return (
      formValues.name !== testSpec.name ||
      formValues.description !== testSpec.description ||
      formValues.functional_area !== testSpec.functional_area ||
      formValues.precondition !== testSpec.precondition ||
      formValues.postcondition !== testSpec.postcondition ||
      JSON.stringify(linkedRequirementIds) !== JSON.stringify(testSpec.requirement_ids) ||
      JSON.stringify(testDataDescription) !== JSON.stringify(testSpec.test_data_description) ||
      JSON.stringify(testSteps) !== JSON.stringify(testSpec.test_steps)
    )
  }

  const handleAutoSave = async () => {
    try {
      if (isEditing && testSpec) {
        const formValues = form.getFieldsValue()
        await onSave({
          name: formValues.name,
          description: formValues.description,
          functional_area: formValues.functional_area,
          precondition: formValues.precondition,
          postcondition: formValues.postcondition,
          requirement_ids: linkedRequirementIds,
          test_data_description: testDataDescription,
          test_steps: testSteps,
        })
        setLastSaved(new Date())
        message.success('Auto-saved successfully', 2)
      }
    } catch (error) {
      console.error('Auto-save failed:', error)
    }
  }

  const handleSave = async () => {
    try {
      const formValues = await form.validateFields()
      await onSave({
        name: formValues.name,
        description: formValues.description,
        functional_area: formValues.functional_area,
        precondition: formValues.precondition,
        postcondition: formValues.postcondition,
        requirement_ids: linkedRequirementIds,
        test_data_description: testDataDescription,
        test_steps: testSteps,
      })

      message.success(
        isEditing
          ? 'Test specification updated successfully'
          : 'Test specification created successfully'
      )
      onClose()
    } catch (error: any) {
      if (error.errorFields) {
        message.error('Please fix validation errors before saving')
      } else {
        message.error(
          isEditing
            ? 'Failed to update test specification'
            : 'Failed to create test specification'
        )
        throw error
      }
    }
  }

  const handleCancel = () => {
    if (hasChanges()) {
      Modal.confirm({
        title: 'Unsaved Changes',
        content: 'You have unsaved changes. Are you sure you want to close?',
        onOk: onClose,
      })
    } else {
      onClose()
    }
  }


  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            {isEditing ? 'Edit Test Specification' : 'Create Test Specification'}
          </Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {lastSaved && (
              <span style={{ fontSize: 12, color: '#666' }}>
                Last saved: {lastSaved.toLocaleTimeString()}
              </span>
            )}
            <Button
              type="text"
              size="small"
              onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
              style={{ color: autoSaveEnabled ? '#52c41a' : '#d9d9d9' }}
            >
              Auto-save {autoSaveEnabled ? 'ON' : 'OFF'}
            </Button>
          </div>
        </div>
      }
      open={visible}
      onCancel={handleCancel}
      width={800}
      footer={[
        <Button key="cancel" onClick={handleCancel} icon={<CloseOutlined />}>
          Cancel
        </Button>,
        <Button
          key="save"
          type="primary"
          loading={loading}
          onClick={handleSave}
          icon={<SaveOutlined />}
        >
          {isEditing ? 'Update' : 'Create'}
        </Button>,
      ]}
    >
      <Tabs defaultActiveKey="basic" size="small">
        <TabPane tab="Basic Information" key="basic">
          <Form
            form={form}
            layout="vertical"
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="Name"
                  name="name"
                  rules={formRules.name}
                >
                  <Input
                    placeholder="Enter test specification name"
                    maxLength={255}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="Functional Area"
                  name="functional_area"
                  rules={formRules.functional_area}
                >
                  <Select
                    placeholder="Select functional area"
                  >
                    {functionalAreas.map(area => (
                      <Option key={area.value} value={area.value}>
                        {area.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="Description"
              name="description"
              rules={formRules.description}
            >
              <TextArea
                placeholder="Enter test specification description"
                rows={3}
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="Precondition"
                  name="precondition"
                  rules={formRules.precondition}
                >
                  <TextArea
                    placeholder="Enter test precondition"
                    rows={2}
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="Postcondition"
                  name="postcondition"
                  rules={formRules.postcondition}
                >
                  <TextArea
                    placeholder="Enter test postcondition"
                    rows={2}
                  />
                </Form.Item>
              </Col>
            </Row>

          </Form>
        </TabPane>

        <TabPane tab="Test Steps" key="steps">
          <TestStepBuilder
            testSteps={testSteps}
            onStepsChange={setTestSteps}
            disabled={loading}
          />
        </TabPane>

        <TabPane tab="Requirements" key="requirements">
          <RequirementLinker
            linkedRequirementIds={linkedRequirementIds}
            onRequirementsChange={setLinkedRequirementIds}
            disabled={loading}
          />
        </TabPane>

        <TabPane tab="Test Data" key="testdata">
          <TestDataGenerator
            testDataDescription={testDataDescription}
            onTestDataChange={setTestDataDescription}
            disabled={loading}
          />
        </TabPane>
      </Tabs>
    </Modal>
  )
}
