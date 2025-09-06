import { SaveOutlined, SwapOutlined } from '@ant-design/icons'
import { Button, Card, Form, Input, Modal, Space, Typography, message } from 'antd'
import React, { useEffect, useState } from 'react'
import { GenericCommand, TestStep } from '../../types/testSpecs'
import { CommandSelector } from './CommandSelector'
import { ParameterSelector } from './ParameterSelector'

const { TextArea } = Input
const { Title, Text } = Typography

interface TestStepEditorProps {
  visible: boolean
  onClose: () => void
  onSave: (testStep: TestStep) => void
  testStep?: TestStep
  loading?: boolean
}

export const TestStepEditor: React.FC<TestStepEditorProps> = ({
  visible,
  onClose,
  onSave,
  testStep,
  loading = false,
}) => {
  const [form] = Form.useForm()
  const [actionCommand, setActionCommand] = useState<GenericCommand | null>(null)
  const [expectedResultCommand, setExpectedResultCommand] = useState<GenericCommand | null>(null)
  const [actionParameters, setActionParameters] = useState<Record<string, string>>({})
  const [expectedResultParameters, setExpectedResultParameters] = useState<Record<string, string>>({})
  const [description, setDescription] = useState('')

  const isEditing = !!testStep

  useEffect(() => {
    if (testStep) {
      // Initialize form with existing test step data
      setDescription(testStep.description || '')
      // Note: In a real implementation, you would need to load the actual command objects
      // based on the command_id from the test step
    } else {
      // Reset form for new test step
      setDescription('')
      setActionCommand(null)
      setExpectedResultCommand(null)
      setActionParameters({})
      setExpectedResultParameters({})
    }
  }, [testStep, visible])

  const handleSave = async () => {
    try {
      if (!actionCommand || !expectedResultCommand) {
        message.error('Please select both action and expected result commands')
        return
      }

      // Validate that all required parameters are provided
      const missingActionParams = actionCommand.required_parameters.filter(
        param => !actionParameters[param]
      )
      const missingExpectedParams = expectedResultCommand.required_parameters.filter(
        param => !expectedResultParameters[param]
      )

      if (missingActionParams.length > 0 || missingExpectedParams.length > 0) {
        message.error('Please provide values for all required parameters')
        return
      }

      const newTestStep: TestStep = {
        id: testStep?.id || `step-${Date.now()}`,
        test_specification_id: testStep?.test_specification_id || '',
        action: {
          command_id: actionCommand.id,
          command_template: actionCommand.template,
          populated_parameters: actionParameters,
        },
        expected_result: {
          command_id: expectedResultCommand.id,
          command_template: expectedResultCommand.template,
          populated_parameters: expectedResultParameters,
        },
        description: description,
        sequence_number: testStep?.sequence_number || 1,
      }

      onSave(newTestStep)
      message.success(isEditing ? 'Test step updated successfully' : 'Test step created successfully')
    } catch (error) {
      message.error('Failed to save test step')
      console.error('Error saving test step:', error)
    }
  }

  const handleActionCommandSelect = (command: GenericCommand) => {
    setActionCommand(command)
    // Reset action parameters when command changes
    setActionParameters({})
  }

  const handleExpectedResultCommandSelect = (command: GenericCommand) => {
    setExpectedResultCommand(command)
    // Reset expected result parameters when command changes
    setExpectedResultParameters({})
  }

  const swapCommands = () => {
    const tempCommand = actionCommand
    const tempParameters = actionParameters

    setActionCommand(expectedResultCommand)
    setActionParameters(expectedResultParameters)
    setExpectedResultCommand(tempCommand)
    setExpectedResultParameters(tempParameters)
  }

  return (
    <Modal
      title={isEditing ? 'Edit Test Step' : 'Create Test Step'}
      open={visible}
      onCancel={onClose}
      width={800}
      footer={[
        <Button key="cancel" onClick={onClose} disabled={loading}>
          Cancel
        </Button>,
        <Button
          key="save"
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          loading={loading}
        >
          {isEditing ? 'Update' : 'Create'}
        </Button>,
      ]}
    >
      <Form form={form} layout="vertical">
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* Description */}
          <Form.Item label="Step Description" required>
            <TextArea
              placeholder="Describe what this test step does..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              disabled={loading}
            />
          </Form.Item>

          {/* Action Command */}
          <Card title="Action Command" size="small">
            <CommandSelector
              onCommandSelect={handleActionCommandSelect}
              selectedCommandId={actionCommand?.id}
              disabled={loading}
              placeholder="Select action command..."
            />

            {actionCommand && (
              <ParameterSelector
                parameterIds={actionCommand.required_parameters}
                onParametersChange={setActionParameters}
                disabled={loading}
              />
            )}
          </Card>

          {/* Swap Button */}
          <div style={{ textAlign: 'center' }}>
            <Button
              type="dashed"
              icon={<SwapOutlined />}
              onClick={swapCommands}
              disabled={loading || !actionCommand || !expectedResultCommand}
            >
              Swap Action ↔ Expected Result
            </Button>
          </div>

          {/* Expected Result Command */}
          <Card title="Expected Result Command" size="small">
            <CommandSelector
              onCommandSelect={handleExpectedResultCommandSelect}
              selectedCommandId={expectedResultCommand?.id}
              disabled={loading}
              placeholder="Select expected result command..."
            />

            {expectedResultCommand && (
              <ParameterSelector
                parameterIds={expectedResultCommand.required_parameters}
                onParametersChange={setExpectedResultParameters}
                disabled={loading}
              />
            )}
          </Card>

          {/* Summary */}
          {actionCommand && expectedResultCommand && (
            <Card size="small" style={{ backgroundColor: '#f6ffed', border: '1px solid #b7eb8f' }}>
              <Title level={5} style={{ margin: 0, color: '#52c41a' }}>
                Test Step Summary
              </Title>
              <Space direction="vertical" size={4}>
                <Text>
                  <Text strong>Action:</Text> {actionCommand.template}
                </Text>
                <Text>
                  <Text strong>Expected Result:</Text> {expectedResultCommand.template}
                </Text>
                <Text type="secondary">
                  {description || 'No description provided'}
                </Text>
              </Space>
            </Card>
          )}
        </Space>
      </Form>
    </Modal>
  )
}
