import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { ParameterSelector } from '../../../components/testSpecs/ParameterSelector'
import { render } from '../../../test-utils/render'
import { Parameter } from '../../../types/parameters'

// Mock the parameters service
vi.mock('../../../services/parameters', () => ({
  parametersService: {
    getParameters: vi.fn(),
    getCategories: vi.fn(),
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

const mockCategories = [
  {
    id: 'cat-1',
    name: 'UDS',
    description: 'Unified Diagnostic Services',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
]

const mockProps = {
  parameterIds: ['param-1', 'param-2'],
  onParametersChange: vi.fn(),
  disabled: false,
}

describe('ParameterSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Mock the service calls
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockResolvedValue(mockParameters)
    vi.mocked(parametersService.getCategories).mockResolvedValue(mockCategories)
  })

  it('renders parameter selector', async () => {
    render(<ParameterSelector {...mockProps} />)

    expect(screen.getByText('Parameter Configuration')).toBeInTheDocument()
  })

  it('shows empty state when no parameters required', () => {
    render(<ParameterSelector {...mockProps} parameterIds={[]} />)

    expect(screen.getByText('No parameters required for the selected command')).toBeInTheDocument()
  })

  it('displays parameters with variants correctly', async () => {
    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('Authentication Level')).toBeInTheDocument()
      expect(screen.getByText('UDS')).toBeInTheDocument()
      expect(screen.getByText('Has Variants')).toBeInTheDocument()
      expect(screen.getByText('high')).toBeInTheDocument()
      expect(screen.getByText('BMW')).toBeInTheDocument()
      expect(screen.getByText('medium')).toBeInTheDocument()
      expect(screen.getByText('VW')).toBeInTheDocument()
    })
  })

  it('displays parameters without variants correctly', async () => {
    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('DID Value')).toBeInTheDocument()
      expect(screen.getByDisplayValue('0x22')).toBeInTheDocument()
    })
  })

  it('calls onParametersChange when parameter value changes', async () => {
    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      const radioButton = screen.getByDisplayValue('medium')
      fireEvent.click(radioButton)
    })

    expect(mockProps.onParametersChange).toHaveBeenCalledWith({
      'param-1': 'medium',
      'param-2': '0x22',
    })
  })

  it('calls onParametersChange when text input changes', async () => {
    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      const input = screen.getByDisplayValue('0x22')
      fireEvent.change(input, { target: { value: '0x33' } })
    })

    expect(mockProps.onParametersChange).toHaveBeenCalledWith({
      'param-1': 'high',
      'param-2': '0x33',
    })
  })

  it('filters parameters by search term', async () => {
    render(<ParameterSelector {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search parameters...')
    fireEvent.change(searchInput, { target: { value: 'Authentication' } })

    await waitFor(() => {
      expect(screen.getByText('Authentication Level')).toBeInTheDocument()
      expect(screen.queryByText('DID Value')).not.toBeInTheDocument()
    })
  })

  it('filters parameters by category', async () => {
    render(<ParameterSelector {...mockProps} />)

    const categorySelect = screen.getByDisplayValue('Filter by category')
    fireEvent.click(categorySelect)

    const udsOption = screen.getByText('UDS')
    fireEvent.click(udsOption)

    await waitFor(() => {
      expect(screen.getByText('Authentication Level')).toBeInTheDocument()
      expect(screen.getByText('DID Value')).toBeInTheDocument()
    })
  })

  it('shows parameter summary', async () => {
    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('Configure 2 required parameters')).toBeInTheDocument()
    })
  })

  it('handles disabled state', async () => {
    render(<ParameterSelector {...mockProps} disabled={true} />)

    await waitFor(() => {
      const radioButton = screen.getByDisplayValue('high')
      expect(radioButton).toBeDisabled()

      const input = screen.getByDisplayValue('0x22')
      expect(input).toBeDisabled()
    })
  })

  it('shows loading state', () => {
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<ParameterSelector {...mockProps} />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    const { parametersService } = await import('../../../services/parameters')
    vi.mocked(parametersService.getParameters).mockRejectedValue(new Error('Failed to load'))

    render(<ParameterSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('No parameters found')).toBeInTheDocument()
    })
  })
})
