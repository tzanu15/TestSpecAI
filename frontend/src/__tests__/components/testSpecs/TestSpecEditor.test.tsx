import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { TestSpecEditor } from '../../../components/testSpecs/TestSpecEditor'
import { render } from '../../../test-utils/render'
import { TestSpecification } from '../../../types/testSpecs'

const mockTestSpec: TestSpecification = {
  id: '1',
  name: 'UDS Diagnostic Test',
  description: 'Test UDS diagnostic capabilities',
  requirement_ids: ['req-1', 'req-2'],
  precondition: 'System is initialized',
  test_steps: [
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
  ],
  postcondition: 'Test completed successfully',
  test_data_description: { level: 'high' },
  functional_area: 'UDS',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  created_by: 'test-user',
  is_active: true,
}

const mockProps = {
  visible: true,
  onClose: vi.fn(),
  onSave: vi.fn(),
  testSpec: null,
  loading: false,
}

describe('TestSpecEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders create mode when no testSpec provided', () => {
    render(<TestSpecEditor {...mockProps} />)

    expect(screen.getByText('Create Test Specification')).toBeInTheDocument()
    expect(screen.getByDisplayValue('')).toBeInTheDocument() // Empty name field
  })

  it('renders edit mode when testSpec provided', () => {
    render(<TestSpecEditor {...mockProps} testSpec={mockTestSpec} />)

    expect(screen.getByText('Edit Test Specification')).toBeInTheDocument()
    expect(screen.getByDisplayValue('UDS Diagnostic Test')).toBeInTheDocument()
  })

  it('calls onClose when cancel button is clicked', () => {
    render(<TestSpecEditor {...mockProps} />)

    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    expect(mockProps.onClose).toHaveBeenCalled()
  })

  it('calls onSave when save button is clicked with valid data', async () => {
    render(<TestSpecEditor {...mockProps} />)

    // Fill in required fields
    const nameInput = screen.getByPlaceholderText('Enter test specification name')
    fireEvent.change(nameInput, { target: { value: 'New Test Spec' } })

    const descriptionInput = screen.getByPlaceholderText('Enter test specification description')
    fireEvent.change(descriptionInput, { target: { value: 'Test description' } })

    const preconditionInput = screen.getByPlaceholderText('Enter precondition')
    fireEvent.change(preconditionInput, { target: { value: 'System ready' } })

    const postconditionInput = screen.getByPlaceholderText('Enter postcondition')
    fireEvent.change(postconditionInput, { target: { value: 'Test complete' } })

    // Select functional area
    const functionalAreaSelect = screen.getByDisplayValue('Select functional area')
    fireEvent.click(functionalAreaSelect)

    const udsOption = screen.getByText('UDS')
    fireEvent.click(udsOption)

    // Click save button
    const saveButton = screen.getByText('Create')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockProps.onSave).toHaveBeenCalledWith({
        name: 'New Test Spec',
        description: 'Test description',
        functional_area: 'UDS',
        precondition: 'System ready',
        postcondition: 'Test complete',
        requirement_ids: [],
        test_data_description: {},
        test_steps: [],
      })
    })
  })

  it('shows validation errors for required fields', async () => {
    render(<TestSpecEditor {...mockProps} />)

    const saveButton = screen.getByText('Create')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Please fix validation errors before saving')).toBeInTheDocument()
    })
  })

  it('displays tabs for different sections', () => {
    render(<TestSpecEditor {...mockProps} />)

    expect(screen.getByText('Basic Information')).toBeInTheDocument()
    expect(screen.getByText('Test Steps')).toBeInTheDocument()
    expect(screen.getByText('Requirements')).toBeInTheDocument()
    expect(screen.getByText('Test Data')).toBeInTheDocument()
  })

  it('shows auto-save toggle', () => {
    render(<TestSpecEditor {...mockProps} />)

    expect(screen.getByText('Auto-save ON')).toBeInTheDocument()
  })

  it('toggles auto-save when clicked', () => {
    render(<TestSpecEditor {...mockProps} />)

    const autoSaveToggle = screen.getByText('Auto-save ON')
    fireEvent.click(autoSaveToggle)

    expect(screen.getByText('Auto-save OFF')).toBeInTheDocument()
  })

  it('displays loading state when loading prop is true', () => {
    render(<TestSpecEditor {...mockProps} loading={true} />)

    const saveButton = screen.getByText('Create')
    expect(saveButton).toBeDisabled()
  })

  it('handles form field changes', () => {
    render(<TestSpecEditor {...mockProps} />)

    const nameInput = screen.getByPlaceholderText('Enter test specification name')
    fireEvent.change(nameInput, { target: { value: 'Updated Name' } })

    expect(nameInput).toHaveValue('Updated Name')
  })
})
