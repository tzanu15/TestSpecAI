import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { TestDataGenerator } from '../../../components/testSpecs/TestDataGenerator'
import { render } from '../../../test-utils/render'
import { Parameter } from '../../../types/parameters'

// Mock the parameters service
vi.mock('../../../services/parameters', () => ({
  parametersService: {
    getParameters: vi.fn(),
  },
}))

const mockParameters: Parameter[] = [
  {
    id: 'param-1',
    name: 'Authentication Level',
    category_id: 'cat-1',
    has_variants: true,
    default_value: 'low',
    variants: [
      {
        id: 'var-1',
        parameter_id: 'param-1',
        manufacturer: 'BMW',
        value: 'high',
        description: 'High security level for BMW',
      },
      {
        id: 'var-2',
        parameter_id: 'param-1',
        manufacturer: 'VW',
        value: 'medium',
        description: 'Medium security level for VW',
      },
    ],
    description: 'Authentication level for UDS communication',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
  {
    id: 'param-2',
    name: 'DID Value',
    category_id: 'cat-1',
    has_variants: false,
    default_value: '0x22',
    variants: [],
    description: 'Diagnostic Identifier value',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
]

const mockTestData = {
  'Authentication Level': {
    value: 'high',
    manufacturer: 'BMW',
    description: 'High security level for BMW',
  },
  'DID Value': '0x22',
}

const mockProps = {
  testDataDescription: mockTestData,
  onTestDataChange: vi.fn(),
  disabled: false,
}

describe('TestDataGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Mock the service calls
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockResolvedValue(mockParameters)
  })

  it('renders test data generator', async () => {
    render(<TestDataGenerator {...mockProps} />)

    expect(screen.getByText('Test Data Generation')).toBeInTheDocument()
  })

  it('displays existing test data entries', async () => {
    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('Authentication Level')).toBeInTheDocument()
      expect(screen.getByDisplayValue('high')).toBeInTheDocument()
      expect(screen.getByDisplayValue('BMW')).toBeInTheDocument()
      expect(screen.getByDisplayValue('DID Value')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0x22')).toBeInTheDocument()
    })
  })

  it('generates test data when generate button is clicked', async () => {
    render(<TestDataGenerator {...mockProps} />)

    const generateButton = screen.getByText('Generate')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Test data generated successfully')).toBeInTheDocument()
    })
  })

  it('calls onTestDataChange when parameter value changes', async () => {
    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      const valueInput = screen.getByDisplayValue('high')
      fireEvent.change(valueInput, { target: { value: 'medium' } })
    })

    expect(mockProps.onTestDataChange).toHaveBeenCalled()
  })

  it('adds new custom entry when add button is clicked', async () => {
    render(<TestDataGenerator {...mockProps} />)

    const addButton = screen.getByText('Add Custom Entry')
    fireEvent.click(addButton)

    await waitFor(() => {
      const parameterInputs = screen.getAllByPlaceholderText('Parameter name')
      expect(parameterInputs).toHaveLength(3) // 2 existing + 1 new
    })
  })

  it('removes entry when remove button is clicked', async () => {
    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      const removeButtons = screen.getAllByText('Remove')
      fireEvent.click(removeButtons[0])
    })

    await waitFor(() => {
      const parameterInputs = screen.getAllByPlaceholderText('Parameter name')
      expect(parameterInputs).toHaveLength(1) // 2 existing - 1 removed
    })
  })

  it('saves test data when save button is clicked', async () => {
    render(<TestDataGenerator {...mockProps} />)

    const saveButton = screen.getByText('Save Test Data')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Test data saved successfully')).toBeInTheDocument()
    })

    expect(mockProps.onTestDataChange).toHaveBeenCalled()
  })

  it('filters parameters by search term', async () => {
    render(<TestDataGenerator {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search parameters...')
    fireEvent.change(searchInput, { target: { value: 'Authentication' } })

    await waitFor(() => {
      expect(screen.getByText('Authentication Level')).toBeInTheDocument()
      expect(screen.queryByText('DID Value')).not.toBeInTheDocument()
    })
  })

  it('shows manufacturer selection', async () => {
    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByDisplayValue('BMW')).toBeInTheDocument()
    })
  })

  it('changes manufacturer when selected', async () => {
    render(<TestDataGenerator {...mockProps} />)

    const manufacturerSelect = screen.getByDisplayValue('BMW')
    fireEvent.click(manufacturerSelect)

    const vwOption = screen.getByText('VW')
    fireEvent.click(vwOption)

    await waitFor(() => {
      expect(screen.getByDisplayValue('VW')).toBeInTheDocument()
    })
  })

  it('shows summary information', async () => {
    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('2 test data entries configured')).toBeInTheDocument()
    })
  })

  it('handles disabled state', async () => {
    render(<TestDataGenerator {...mockProps} disabled={true} />)

    const generateButton = screen.getByText('Generate')
    expect(generateButton).toBeDisabled()

    const saveButton = screen.getByText('Save Test Data')
    expect(saveButton).toBeDisabled()

    await waitFor(() => {
      const valueInput = screen.getByDisplayValue('high')
      expect(valueInput).toBeDisabled()
    })
  })

  it('shows loading state', () => {
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<TestDataGenerator {...mockProps} />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockRejectedValue(new Error('Failed to load'))

    render(<TestDataGenerator {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('No parameters found')).toBeInTheDocument()
    })
  })
})
