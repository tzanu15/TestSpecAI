import {
    DeleteOutlined,
    DragOutlined,
    EditOutlined,
    EyeOutlined,
    PlusOutlined,
} from '@ant-design/icons'
import {
    closestCenter,
    DndContext,
    DragEndEvent,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core'
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    useSortable,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
    Button,
    Card,
    Form,
    Input,
    Modal,
    Popconfirm,
    Select,
    Space,
    Tooltip,
    Typography
} from 'antd'
import React, { useState } from 'react'
import { TestStep } from '../../types/testSpecs'

const { Title, Text } = Typography
const { TextArea } = Input
const { Option } = Select

interface TestStepBuilderProps {
  testSteps: TestStep[]
  onStepsChange: (steps: TestStep[]) => void
  onStepEdit?: (step: TestStep) => void
  onStepDelete?: (stepId: string) => void
  disabled?: boolean
}

interface SortableStepItemProps {
  step: TestStep
  onEdit: (step: TestStep) => void
  onDelete: (stepId: string) => void
  disabled?: boolean
}

const SortableStepItem: React.FC<SortableStepItemProps> = ({
  step,
  onEdit,
  onDelete,
  disabled = false,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: step.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <Card
      ref={setNodeRef}
      style={style}
      size="small"
      className="test-step-item"
      bodyStyle={{ padding: 12 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div
          {...attributes}
          {...listeners}
          style={{
            cursor: disabled ? 'not-allowed' : 'grab',
            padding: 4,
            display: 'flex',
            alignItems: 'center',
            opacity: disabled ? 0.5 : 1,
          }}
        >
          <DragOutlined />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Text strong>Step {step.sequence_number}</Text>
            {step.description && (
              <Text type="secondary" ellipsis style={{ maxWidth: 200 }}>
                {step.description}
              </Text>
            )}
          </div>

          <div style={{ display: 'flex', gap: 8, fontSize: 12 }}>
            <Text type="secondary">
              Action: {step.action.command_template || 'No action defined'}
            </Text>
            <Text type="secondary">
              Expected: {step.expected_result.command_template || 'No expected result'}
            </Text>
          </div>
        </div>

        <Space>
          <Tooltip title="View Details">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => onEdit(step)}
            />
          </Tooltip>
          <Tooltip title="Edit Step">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => onEdit(step)}
              disabled={disabled}
            />
          </Tooltip>
          <Popconfirm
            title="Delete Step"
            description="Are you sure you want to delete this test step?"
            onConfirm={() => onDelete(step.id)}
            okText="Yes"
            cancelText="No"
            okType="danger"
          >
            <Tooltip title="Delete Step">
              <Button
                type="text"
                size="small"
                danger
                icon={<DeleteOutlined />}
                disabled={disabled}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      </div>
    </Card>
  )
}

interface TestStepEditorProps {
  visible: boolean
  onClose: () => void
  onSave: (step: Omit<TestStep, 'id' | 'test_specification_id'>) => void
  step?: TestStep | null
  stepNumber: number
  loading?: boolean
}

const TestStepEditor: React.FC<TestStepEditorProps> = ({
  visible,
  onClose,
  onSave,
  step,
  stepNumber,
  loading = false,
}) => {
  const [form] = Form.useForm()
  const isEditing = !!step

  const handleSave = async () => {
    try {
      const values = await form.validateFields()

      const stepData: Omit<TestStep, 'id' | 'test_specification_id'> = {
        action: values.action,
        expected_result: values.expected_result,
        description: values.description,
        sequence_number: stepNumber,
      }

      onSave(stepData)
      form.resetFields()
      onClose()
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  const handleCancel = () => {
    form.resetFields()
    onClose()
  }

  // Mock command options - TODO: Load from API
  const mockCommands = [
    { id: 'cmd1', template: 'Set authentication level to {level}', category: 'UDS' },
    { id: 'cmd2', template: 'Send diagnostic request {did}', category: 'UDS' },
    { id: 'cmd3', template: 'Verify response code {code}', category: 'UDS' },
    { id: 'cmd4', template: 'Send CAN message {message}', category: 'Communication' },
    { id: 'cmd5', template: 'Check error state {error}', category: 'ErrorHandler' },
  ]

  return (
    <Modal
      title={`${isEditing ? 'Edit' : 'Add'} Test Step ${stepNumber}`}
      open={visible}
      onCancel={handleCancel}
      width={600}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button
          key="save"
          type="primary"
          loading={loading}
          onClick={handleSave}
        >
          {isEditing ? 'Update' : 'Add'} Step
        </Button>,
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          action: step?.action || { command_id: '', command_template: '', populated_parameters: {} },
          expected_result: step?.expected_result || { command_id: '', command_template: '', populated_parameters: {} },
          description: step?.description || '',
        }}
      >
        <Form.Item
          label="Step Description"
          name="description"
          rules={[{ required: true, message: 'Please enter step description' }]}
        >
          <TextArea
            placeholder="Describe what this test step does"
            rows={2}
          />
        </Form.Item>

        <Form.Item
          label="Action Command"
          name={['action', 'command_id']}
          rules={[{ required: true, message: 'Please select an action command' }]}
        >
          <Select
            placeholder="Select action command"
            showSearch
            optionFilterProp="children"
          >
            {mockCommands.map(cmd => (
              <Option key={cmd.id} value={cmd.id}>
                <div>
                  <div>{cmd.template}</div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {cmd.category}
                  </Text>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="Expected Result Command"
          name={['expected_result', 'command_id']}
          rules={[{ required: true, message: 'Please select an expected result command' }]}
        >
          <Select
            placeholder="Select expected result command"
            showSearch
            optionFilterProp="children"
          >
            {mockCommands.map(cmd => (
              <Option key={cmd.id} value={cmd.id}>
                <div>
                  <div>{cmd.template}</div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {cmd.category}
                  </Text>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="Action Parameters"
          name={['action', 'populated_parameters']}
        >
          <Input
            placeholder="Enter parameters as JSON (e.g., {'level': 'high'})"
            disabled
          />
        </Form.Item>

        <Form.Item
          label="Expected Result Parameters"
          name={['expected_result', 'populated_parameters']}
        >
          <Input
            placeholder="Enter parameters as JSON (e.g., {'code': '0x00'})"
            disabled
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export const TestStepBuilder: React.FC<TestStepBuilderProps> = ({
  testSteps,
  onStepsChange,
  onStepEdit,
  onStepDelete,
  disabled = false,
}) => {
  const [editorVisible, setEditorVisible] = useState(false)
  const [editingStep, setEditingStep] = useState<TestStep | null>(null)
  const [nextStepNumber, setNextStepNumber] = useState(1)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      const oldIndex = testSteps.findIndex(step => step.id === active.id)
      const newIndex = testSteps.findIndex(step => step.id === over.id)

      const newSteps = arrayMove(testSteps, oldIndex, newIndex)

      // Update sequence numbers
      const updatedSteps = newSteps.map((step, index) => ({
        ...step,
        sequence_number: index + 1,
      }))

      onStepsChange(updatedSteps)
    }
  }

  const handleAddStep = () => {
    setEditingStep(null)
    setNextStepNumber(testSteps.length + 1)
    setEditorVisible(true)
  }

  const handleEditStep = (step: TestStep) => {
    setEditingStep(step)
    setNextStepNumber(step.sequence_number)
    setEditorVisible(true)
  }

  const handleDeleteStep = (stepId: string) => {
    const newSteps = testSteps
      .filter(step => step.id !== stepId)
      .map((step, index) => ({
        ...step,
        sequence_number: index + 1,
      }))

    onStepsChange(newSteps)
    onStepDelete?.(stepId)
  }

  const handleSaveStep = (stepData: Omit<TestStep, 'id' | 'test_specification_id'>) => {
    if (editingStep) {
      // Update existing step
      const updatedSteps = testSteps.map(step =>
        step.id === editingStep.id
          ? { ...step, ...stepData }
          : step
      )
      onStepsChange(updatedSteps)
    } else {
      // Add new step
      const newStep: TestStep = {
        id: `step-${Date.now()}`, // Temporary ID
        test_specification_id: '', // Will be set when saving the test spec
        ...stepData,
      }
      onStepsChange([...testSteps, newStep])
    }
  }

  const handleCloseEditor = () => {
    setEditorVisible(false)
    setEditingStep(null)
  }

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Title level={5} style={{ margin: 0 }}>
            Test Steps ({testSteps.length})
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddStep}
            disabled={disabled}
            size="small"
          >
            Add Step
          </Button>
        </div>
      }
      bodyStyle={{ padding: 16 }}
    >
      {testSteps.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 24, color: '#999' }}>
          <Text type="secondary">No test steps defined yet</Text>
          <br />
          <Text type="secondary">Click "Add Step" to create your first test step</Text>
        </div>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={testSteps.map(step => step.id)}
            strategy={verticalListSortingStrategy}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              {testSteps.map(step => (
                <SortableStepItem
                  key={step.id}
                  step={step}
                  onEdit={handleEditStep}
                  onDelete={handleDeleteStep}
                  disabled={disabled}
                />
              ))}
            </Space>
          </SortableContext>
        </DndContext>
      )}

      <TestStepEditor
        visible={editorVisible}
        onClose={handleCloseEditor}
        onSave={handleSaveStep}
        step={editingStep}
        stepNumber={nextStepNumber}
      />
    </Card>
  )
}
