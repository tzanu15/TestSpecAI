import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { TestStepEditor } from '../../../components/testSpecs/TestStepEditor'
import { render } from '../../../test-utils/render'
import { TestStep } from '../../../types/testSpecs'

// Mock the command and parameter selectors
vi.mock('../../../components/testSpecs/CommandSelector', () => ({
  CommandSelector: ({ onChange, value, disabled }: any) => (
    <select
      data-testid="command-selector"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      disabled={disabled}
    >
      <option value="">Select a command</option>
      <option value="cmd-1">Set Authentication Level</option>
      <option value="cmd-2">Read DID</option>
    </select>
  ),
}))

vi.mock('../../../components/testSpecs/ParameterSelector', () => ({
  ParameterSelector: ({ onChange, value, disabled }: any) => (
    <select
      data-testid="parameter-selector"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      disabled={disabled}
    >
      <option value="">Select a parameter</option>
      <option value="param-1">Authentication Level</option>
      <option value="param-2">DID Value</option>
    </select>
  ),
}))

const mockTestStep: TestStep = {
  id: 'step-1',
  test_specification_id: 'spec-1',
  action: {
    command_id: 'cmd-1',
    command_template: 'Set level of authentication {Authentication}',
    populated_parameters: {
      'Authentication': 'high',
    },
  },
  expected_result: {
    command_id: 'cmd-2',
    command_template: 'Read DID {DID}',
    populated_parameters: {
      'DID': '0x22',
    },
  },
  description: 'Test authentication level setting',
  sequence_number: 1,
}

const mockProps = {
  visible: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
  step: null,
  stepNumber: 1,
  loading: false,
}

describe('TestStepEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders test step editor modal', () => {
    render(<TestStepEditor {...mockProps} />)

    expect(screen.getByText('Add Test Step 1')).toBeInTheDocument()
    expect(screen.getByText('Step Description')).toBeInTheDocument()
    expect(screen.getByText('Action Command')).toBeInTheDocument()
    expect(screen.getByText('Expected Result Command')).toBeInTheDocument()
  })

  it('renders in edit mode when step is provided', () => {
    render(<TestStepEditor {...mockProps} step={mockTestStep} />)

    expect(screen.getByText('Edit Test Step 1')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Test authentication level setting')).toBeInTheDocument()
  })

  it('calls onClose when cancel button is clicked', () => {
    render(<TestStepEditor {...mockProps} />)

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('calls onClose when modal is closed', () => {
    render(<TestStepEditor {...mockProps} />)

    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)

    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('validates required fields', async () => {
    render(<TestStepEditor {...mockProps} />)

    const saveButton = screen.getByText('Add Step')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Please enter step description')).toBeInTheDocument()
      expect(screen.getByText('Please select an action command')).toBeInTheDocument()
      expect(screen.getByText('Please select an expected result command')).toBeInTheDocument()
    })
  })

  it('calls onSave with form data when save button is clicked', async () => {
    render(<TestStepEditor {...mockProps} />)

    // Fill in the form
    const descriptionInput = screen.getByPlaceholderText('Describe what this test step does')
    fireEvent.change(descriptionInput, { target: { value: 'Test step description' } })

    const actionCommandSelector = screen.getByTestId('command-selector')
    fireEvent.change(actionCommandSelector, { target: { value: 'cmd-1' } })

    const expectedResultCommandSelector = screen.getAllByTestId('command-selector')[1]
    fireEvent.change(expectedResultCommandSelector, { target: { value: 'cmd-2' } })

    const saveButton = screen.getByText('Add Step')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalledWith({
        action: {
          command_id: 'cmd-1',
          command_template: '',
          populated_parameters: {},
        },
        expected_result: {
          command_id: 'cmd-2',
          command_template: '',
          populated_parameters: {},
        },
        description: 'Test step description',
        sequence_number: 1,
      })
    })
  })

  it('populates form fields when editing existing step', () => {
    render(<TestStepEditor {...mockProps} step={mockTestStep} />)

    expect(screen.getByDisplayValue('Test authentication level setting')).toBeInTheDocument()
    expect(screen.getByDisplayValue('cmd-1')).toBeInTheDocument()
    expect(screen.getByDisplayValue('cmd-2')).toBeInTheDocument()
  })

  it('shows loading state on save button', () => {
    render(<TestStepEditor {...mockProps} loading={true} />)

    const saveButton = screen.getByText('Add Step')
    expect(saveButton).toBeDisabled()
  })

  it('disables form fields when loading', () => {
    render(<TestStepEditor {...mockProps} loading={true} />)

    const descriptionInput = screen.getByPlaceholderText('Describe what this test step does')
    expect(descriptionInput).toBeDisabled()

    const actionCommandSelector = screen.getByTestId('command-selector')
    expect(actionCommandSelector).toBeDisabled()
  })

  it('resets form when modal is closed', () => {
    const { rerender } = render(<TestStepEditor {...mockProps} />)

    // Fill in some data
    const descriptionInput = screen.getByPlaceholderText('Describe what this test step does')
    fireEvent.change(descriptionInput, { target: { value: 'Test description' } })

    // Close modal
    rerender(<TestStepEditor {...mockProps} visible={false} />)

    // Reopen modal
    rerender(<TestStepEditor {...mockProps} visible={true} />)

    expect(screen.getByPlaceholderText('Describe what this test step does')).toHaveValue('')
  })

  it('shows correct button text for add vs edit mode', () => {
    const { rerender } = render(<TestStepEditor {...mockProps} />)
    expect(screen.getByText('Add Step')).toBeInTheDocument()

    rerender(<TestStepEditor {...mockProps} step={mockTestStep} />)
    expect(screen.getByText('Update Step')).toBeInTheDocument()
  })

  it('handles parameter selection for action command', async () => {
    render(<TestStepEditor {...mockProps} />)

    const actionCommandSelector = screen.getByTestId('command-selector')
    fireEvent.change(actionCommandSelector, { target: { value: 'cmd-1' } })

    await waitFor(() => {
      expect(screen.getByText('Action Parameters')).toBeInTheDocument()
    })
  })

  it('handles parameter selection for expected result command', async () => {
    render(<TestStepEditor {...mockProps} />)

    const expectedResultCommandSelector = screen.getAllByTestId('command-selector')[1]
    fireEvent.change(expectedResultCommandSelector, { target: { value: 'cmd-2' } })

    await waitFor(() => {
      expect(screen.getByText('Expected Result Parameters')).toBeInTheDocument()
    })
  })
})
