import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { RequirementLinker } from '../../../components/testSpecs/RequirementLinker'
import { render } from '../../../test-utils/render'
import { Requirement } from '../../../types/requirements'

// Mock the requirements service
vi.mock('../../../services/requirements', () => ({
  requirementsService: {
    getRequirements: vi.fn(),
  },
}))

const mockRequirements: Requirement[] = [
  {
    id: 'req-1',
    title: 'UDS Authentication',
    description: 'The system shall support UDS authentication',
    category_id: 'cat-1',
    source: 'manual',
    metadata: {},
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
  {
    id: 'req-2',
    title: 'Diagnostic Communication',
    description: 'The system shall establish diagnostic communication',
    category_id: 'cat-1',
    source: 'document',
    metadata: {},
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
  {
    id: 'req-3',
    title: 'Error Handling',
    description: 'The system shall handle errors gracefully',
    category_id: 'cat-2',
    source: 'ai_generated',
    metadata: {},
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
]

const mockProps = {
  linkedRequirementIds: ['req-1'],
  onRequirementsChange: vi.fn(),
  disabled: false,
}

describe('RequirementLinker', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Mock the service calls
    const { requirementsService } = await import('../../../services/requirements')
    vi.mocked(requirementsService.getRequirements).mockResolvedValue(mockRequirements)
  })

  it('renders requirement linker', async () => {
    render(<RequirementLinker {...mockProps} />)

    expect(screen.getByText('Requirement Linking')).toBeInTheDocument()
  })

  it('displays linked requirements', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('Linked Requirements (1)')).toBeInTheDocument()
      expect(screen.getByText('UDS Authentication')).toBeInTheDocument()
      expect(screen.getByText('manual')).toBeInTheDocument()
    })
  })

  it('displays available requirements', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('Available Requirements (2)')).toBeInTheDocument()
      expect(screen.getByText('Diagnostic Communication')).toBeInTheDocument()
      expect(screen.getByText('Error Handling')).toBeInTheDocument()
    })
  })

  it('calls onRequirementsChange when link button is clicked', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      const linkButtons = screen.getAllByTitle('Link Requirement')
      fireEvent.click(linkButtons[0]) // Link the first available requirement
    })

    expect(mockProps.onRequirementsChange).toHaveBeenCalledWith(['req-1', 'req-2'])
  })

  it('calls onRequirementsChange when unlink button is clicked', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      const unlinkButtons = screen.getAllByTitle('Unlink Requirement')
      fireEvent.click(unlinkButtons[0])
    })

    expect(mockProps.onRequirementsChange).toHaveBeenCalledWith([])
  })

  it('filters requirements by search term', async () => {
    render(<RequirementLinker {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search requirements...')
    fireEvent.change(searchInput, { target: { value: 'Diagnostic' } })

    await waitFor(() => {
      expect(screen.getByText('Available Requirements (1)')).toBeInTheDocument()
      expect(screen.getByText('Diagnostic Communication')).toBeInTheDocument()
      expect(screen.queryByText('Error Handling')).not.toBeInTheDocument()
    })
  })

  it('shows correct source tags', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('manual')).toBeInTheDocument()
      expect(screen.getByText('document')).toBeInTheDocument()
      expect(screen.getByText('ai_generated')).toBeInTheDocument()
    })
  })

  it('shows summary information', async () => {
    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('1 requirement linked to this test specification')).toBeInTheDocument()
    })
  })

  it('handles empty search results', async () => {
    render(<RequirementLinker {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search requirements...')
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } })

    await waitFor(() => {
      expect(screen.getByText('No requirements match your search')).toBeInTheDocument()
    })
  })

  it('handles no available requirements', async () => {
    render(<RequirementLinker {...mockProps} linkedRequirementIds={['req-1', 'req-2', 'req-3']} />)

    await waitFor(() => {
      expect(screen.getByText('No available requirements to link')).toBeInTheDocument()
    })
  })

  it('handles disabled state', async () => {
    render(<RequirementLinker {...mockProps} disabled={true} />)

    await waitFor(() => {
      const linkButtons = screen.getAllByTitle('Link Requirement')
      expect(linkButtons[0]).toBeDisabled()

      const unlinkButtons = screen.getAllByTitle('Unlink Requirement')
      expect(unlinkButtons[0]).toBeDisabled()
    })
  })

  it('shows loading state', () => {
    const { requirementsService } = await import('../../../services/requirements')
    vi.mocked(requirementsService.getRequirements).mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<RequirementLinker {...mockProps} />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    const { requirementsService } = await import('../../../services/requirements')
    vi.mocked(requirementsService.getRequirements).mockRejectedValue(new Error('Failed to load'))

    render(<RequirementLinker {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('No requirements found')).toBeInTheDocument()
    })
  })
})
