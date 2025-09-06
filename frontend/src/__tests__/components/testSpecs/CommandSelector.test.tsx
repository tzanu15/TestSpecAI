import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { CommandSelector } from '../../../components/testSpecs/CommandSelector'
import { render } from '../../../test-utils/render'
import { GenericCommand } from '../../../types/commands'

// Mock the commands service
vi.mock('../../../services/commands', () => ({
  commandsService: {
    getCommands: vi.fn(),
    getCategories: vi.fn(),
  },
}))

const mockCommands: GenericCommand[] = [
  {
    id: 'cmd-1',
    template: 'Set authentication level to {level}',
    category_id: 'cat-1',
    required_parameters: ['level'],
    description: 'Set the authentication level for UDS communication',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    created_by: 'test-user',
    is_active: true,
  },
  {
    id: 'cmd-2',
    template: 'Send diagnostic request {did}',
    category_id: 'cat-1',
    required_parameters: ['did'],
    description: 'Send a diagnostic request with specified DID',
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
  onCommandSelect: vi.fn(),
  selectedCommandId: undefined,
  disabled: false,
  placeholder: 'Select a command...',
}

describe('CommandSelector', () => {
  beforeEach(async () => {
    vi.clearAllMocks()

    // Mock the service calls
    const { commandsService } = await import('../../../services/commands')
    vi.mocked(commandsService.getCommands).mockResolvedValue(mockCommands)
    vi.mocked(commandsService.getCategories).mockResolvedValue(mockCategories)
  })

  it('renders command selector', async () => {
    render(<CommandSelector {...mockProps} />)

    expect(screen.getByText('Command Selection')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Select a command...')).toBeInTheDocument()
  })

  it('loads and displays commands', async () => {
    render(<CommandSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('Set authentication level to {level}')).toBeInTheDocument()
      expect(screen.getByText('Send diagnostic request {did}')).toBeInTheDocument()
    })
  })

  it('calls onCommandSelect when command is selected', async () => {
    render(<CommandSelector {...mockProps} />)

    const select = screen.getByPlaceholderText('Select a command...')
    fireEvent.click(select)

    await waitFor(() => {
      const option = screen.getByText('Set authentication level to {level}')
      fireEvent.click(option)
    })

    expect(mockProps.onCommandSelect).toHaveBeenCalledWith(mockCommands[0])
  })

  it('filters commands by search term', async () => {
    render(<CommandSelector {...mockProps} />)

    const searchInput = screen.getByPlaceholderText('Search commands...')
    fireEvent.change(searchInput, { target: { value: 'authentication' } })

    await waitFor(() => {
      expect(screen.getByText('Set authentication level to {level}')).toBeInTheDocument()
      expect(screen.queryByText('Send diagnostic request {did}')).not.toBeInTheDocument()
    })
  })

  it('filters commands by category', async () => {
    render(<CommandSelector {...mockProps} />)

    const categorySelect = screen.getByDisplayValue('Filter by category')
    fireEvent.click(categorySelect)

    const udsOption = screen.getByText('UDS')
    fireEvent.click(udsOption)

    await waitFor(() => {
      expect(screen.getByText('Set authentication level to {level}')).toBeInTheDocument()
      expect(screen.getByText('Send diagnostic request {did}')).toBeInTheDocument()
    })
  })

  it('displays command information correctly', async () => {
    render(<CommandSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('UDS')).toBeInTheDocument()
      expect(screen.getByText('1 params')).toBeInTheDocument()
      expect(screen.getByText('Set the authentication level for UDS communication')).toBeInTheDocument()
    })
  })

  it('shows selected command info when command is selected', async () => {
    render(<CommandSelector {...mockProps} selectedCommandId="cmd-1" />)

    await waitFor(() => {
      expect(screen.getByText('Selected command requires 1 parameters')).toBeInTheDocument()
    })
  })

  it('handles disabled state', () => {
    render(<CommandSelector {...mockProps} disabled={true} />)

    const select = screen.getByPlaceholderText('Select a command...')
    expect(select).toBeDisabled()

    const searchInput = screen.getByPlaceholderText('Search commands...')
    expect(searchInput).toBeDisabled()
  })

  it('shows loading state', async () => {
    const { commandsService } = await import('../../../services/commands')
    vi.mocked(commandsService.getCommands).mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<CommandSelector {...mockProps} />)

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    const { commandsService } = await import('../../../services/commands')
    vi.mocked(commandsService.getCommands).mockRejectedValue(new Error('Failed to load'))

    render(<CommandSelector {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText('No commands found')).toBeInTheDocument()
    })
  })
})
