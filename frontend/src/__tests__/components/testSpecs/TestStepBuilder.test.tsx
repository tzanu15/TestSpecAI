import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { TestStepBuilder } from '../../../components/testSpecs/TestStepBuilder'
import { render } from '../../../test-utils/render'
import { TestStep } from '../../../types/testSpecs'

const mockTestSteps: TestStep[] = [
  {
    id: 'step-1',
    test_specification_id: '1',
    action: {
      command_id: 'cmd-1',
      command_template: 'Set authentication level to {level}',
      populated_parameters: { level: 'high' },
    },
    expected_result: {
      command_id: 'cmd-2',
      command_template: 'Verify response code {code}',
      populated_parameters: { code: '0x00' },
    },
    description: 'Set authentication level',
    sequence_number: 1,
  },
  {
    id: 'step-2',
    test_specification_id: '1',
    action: {
      command_id: 'cmd-3',
      command_template: 'Send diagnostic request {did}',
      populated_parameters: { did: '0x22' },
    },
    expected_result: {
      command_id: 'cmd-4',
      command_template: 'Check response data {data}',
      populated_parameters: { data: '0x1234' },
    },
    description: 'Send diagnostic request',
    sequence_number: 2,
  },
]

const mockProps = {
  testSteps: mockTestSteps,
  onStepsChange: vi.fn(),
  onStepEdit: vi.fn(),
  onStepDelete: vi.fn(),
  disabled: false,
}

describe('TestStepBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders test steps list', () => {
    render(<TestStepBuilder {...mockProps} />)

    expect(screen.getByText('Test Steps (2)')).toBeInTheDocument()
    expect(screen.getByText('Step 1')).toBeInTheDocument()
    expect(screen.getByText('Step 2')).toBeInTheDocument()
  })

  it('shows empty state when no test steps', () => {
    render(<TestStepBuilder {...mockProps} testSteps={[]} />)

    expect(screen.getByText('Test Steps (0)')).toBeInTheDocument()
    expect(screen.getByText('No test steps defined yet')).toBeInTheDocument()
    expect(screen.getByText('Click "Add Step" to create your first test step')).toBeInTheDocument()
  })

  it('calls onStepsChange when add step button is clicked', () => {
    render(<TestStepBuilder {...mockProps} />)

    const addButton = screen.getByText('Add Step')
    fireEvent.click(addButton)

    // Should open the step editor modal
    expect(screen.getByText('Add Test Step 3')).toBeInTheDocument()
  })

  it('calls onStepEdit when edit button is clicked', () => {
    render(<TestStepBuilder {...mockProps} />)

    const editButtons = screen.getAllByTitle('Edit Step')
    fireEvent.click(editButtons[0])

    // Should open the step editor modal
    expect(screen.getByText('Edit Test Step 1')).toBeInTheDocument()
  })

  it('calls onStepDelete when delete button is clicked', async () => {
    render(<TestStepBuilder {...mockProps} />)

    const deleteButtons = screen.getAllByTitle('Delete Step')
    fireEvent.click(deleteButtons[0])

    // Confirm deletion in popconfirm
    const confirmButton = screen.getByText('Yes')
    fireEvent.click(confirmButton)

    expect(mockProps.onStepDelete).toHaveBeenCalledWith('step-1')
  })

  it('displays step information correctly', () => {
    render(<TestStepBuilder {...mockProps} />)

    expect(screen.getByText('Set authentication level')).toBeInTheDocument()
    expect(screen.getByText('Action: Set authentication level to {level}')).toBeInTheDocument()
    expect(screen.getByText('Expected: Verify response code {code}')).toBeInTheDocument()
  })

  it('shows drag handle for reordering', () => {
    render(<TestStepBuilder {...mockProps} />)

    const dragHandles = screen.getAllByTitle('Drag to reorder')
    expect(dragHandles).toHaveLength(2)
  })

  it('handles disabled state', () => {
    render(<TestStepBuilder {...mockProps} disabled={true} />)

    const addButton = screen.getByText('Add Step')
    expect(addButton).toBeDisabled()

    const editButtons = screen.getAllByTitle('Edit Step')
    expect(editButtons[0]).toBeDisabled()
  })

  it('opens step editor modal when add step is clicked', () => {
    render(<TestStepBuilder {...mockProps} />)

    const addButton = screen.getByText('Add Step')
    fireEvent.click(addButton)

    expect(screen.getByText('Add Test Step 3')).toBeInTheDocument()
    expect(screen.getByText('Step Description')).toBeInTheDocument()
    expect(screen.getByText('Action Command')).toBeInTheDocument()
    expect(screen.getByText('Expected Result Command')).toBeInTheDocument()
  })

  it('closes step editor modal when cancel is clicked', () => {
    render(<TestStepBuilder {...mockProps} />)

    const addButton = screen.getByText('Add Step')
    fireEvent.click(addButton)

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(screen.queryByText('Add Test Step 3')).not.toBeInTheDocument()
  })

  it('saves new step when save button is clicked', async () => {
    render(<TestStepBuilder {...mockProps} />)

    const addButton = screen.getByText('Add Step')
    fireEvent.click(addButton)

    // Fill in step details
    const descriptionInput = screen.getByPlaceholderText('Describe what this test step does')
    fireEvent.change(descriptionInput, { target: { value: 'New test step' } })

    const saveButton = screen.getByText('Add Step')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockProps.onStepsChange).toHaveBeenCalled()
    })
  })
})
