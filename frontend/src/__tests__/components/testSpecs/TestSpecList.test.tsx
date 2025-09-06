import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { TestSpecList } from '../../../components/testSpecs/TestSpecList'
import { render } from '../../../test-utils/render'
import { TestSpecification } from '../../../types/testSpecs'

const mockTestSpecifications: TestSpecification[] = [
  {
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
  },
  {
    id: '2',
    name: 'CAN Communication Test',
    description: 'Test CAN communication functionality',
    requirement_ids: ['req-3'],
    precondition: 'CAN bus is available',
    test_steps: [],
    postcondition: 'Communication established',
    test_data_description: {},
    functional_area: 'Communication',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
]

const mockProps = {
  testSpecifications: mockTestSpecifications,
  loading: false,
  onEdit: vi.fn(),
  onDelete: vi.fn(),
  onCreate: vi.fn(),
  onDuplicate: vi.fn(),
  onSearch: vi.fn(),
  onFilterChange: vi.fn(),
}

describe('TestSpecList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders test specifications list', () => {
    render(<TestSpecList {...mockProps} />)

    expect(screen.getByText('UDS Diagnostic Test')).toBeInTheDocument()
    expect(screen.getByText('CAN Communication Test')).toBeInTheDocument()
  })

  it('displays loading state', () => {
    render(<TestSpecList {...mockProps} loading={true} />)

    expect(screen.getByRole('table')).toBeInTheDocument()
    // Ant Design Table shows loading spinner
  })

  it('calls onEdit when edit button is clicked', async () => {
    render(<TestSpecList {...mockProps} />)

    const editButtons = screen.getAllByText('Edit')
    fireEvent.click(editButtons[0])

    expect(mockProps.onEdit).toHaveBeenCalledWith('1', mockTestSpecifications[0])
  })

  it('calls onDelete when delete button is clicked', async () => {
    render(<TestSpecList {...mockProps} />)

    const deleteButtons = screen.getAllByText('Delete')
    fireEvent.click(deleteButtons[0])

    // Confirm deletion in popconfirm
    const confirmButton = screen.getByText('Yes')
    fireEvent.click(confirmButton)

    expect(mockProps.onDelete).toHaveBeenCalledWith('1')
  })

  it('calls onDuplicate when duplicate button is clicked', async () => {
    render(<TestSpecList {...mockProps} />)

    const duplicateButtons = screen.getAllByText('Duplicate')
    fireEvent.click(duplicateButtons[0])

    expect(mockProps.onDuplicate).toHaveBeenCalledWith('1')
  })

  it('displays functional area tags correctly', () => {
    render(<TestSpecList {...mockProps} />)

    expect(screen.getByText('UDS')).toBeInTheDocument()
    expect(screen.getByText('Communication')).toBeInTheDocument()
  })

  it('handles empty test specifications list', () => {
    render(<TestSpecList {...mockProps} testSpecifications={[]} />)

    expect(screen.getByRole('table')).toBeInTheDocument()
    // Table should be empty but still render
  })

  it('calls onSearch when search input changes', async () => {
    render(<TestSpecList {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search test specifications...')
    fireEvent.change(searchInput, { target: { value: 'UDS' } })

    await waitFor(() => {
      expect(mockProps.onSearch).toHaveBeenCalledWith('UDS')
    })
  })

  it('calls onFilterChange when functional area filter changes', async () => {
    render(<TestSpecList {...mockProps} />)

    const filterSelect = screen.getByDisplayValue('All Areas')
    fireEvent.click(filterSelect)

    const udsOption = screen.getByText('UDS')
    fireEvent.click(udsOption)

    await waitFor(() => {
      expect(mockProps.onFilterChange).toHaveBeenCalledWith({ functional_area: 'UDS' })
    })
  })
})
