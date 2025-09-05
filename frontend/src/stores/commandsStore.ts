import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { CommandCategory, GenericCommand } from '../types/commands'
import { createBaseStore } from './baseStore'

interface CommandsState {
  categories: CommandCategory[]
  filters: {
    category_id?: string
    search?: string
  }
}

interface CommandsActions {
  setCategories: (_categories: CommandCategory[]) => void
  setFilters: (_filters: Partial<CommandsState['filters']>) => void
  clearFilters: () => void
}

const initialState = {
  items: [] as GenericCommand[],
  loading: false,
  error: null,
  selectedItem: null,
  categories: [] as CommandCategory[],
  filters: {} as CommandsState['filters'],
}

export const useCommandsStore = create<CommandsState & CommandsActions>()(
  devtools(
    set => ({
      ...initialState,

      setCategories: categories => set({ categories }),
      setFilters: filters =>
        set(state => ({
          filters: { ...state.filters, ...filters },
        })),
      clearFilters: () => set({ filters: {} }),

      // Inherit base actions
      ...createBaseStore('commands', initialState),
    }),
    { name: 'commands-store' }
  )
)
