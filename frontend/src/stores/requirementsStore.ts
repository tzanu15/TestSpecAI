import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Requirement, RequirementCategory } from '../types/requirements'

interface RequirementsState {
  items: Requirement[]
  loading: boolean
  error: string | null
  selectedItem: Requirement | null
  categories: RequirementCategory[]
  filters: {
    category_id?: string
    search?: string
  }
}

interface RequirementsActions {
  setItems: (_items: Requirement[]) => void
  setLoading: (_loading: boolean) => void
  setError: (_error: string | null) => void
  setSelectedItem: (_item: Requirement | null) => void
  addItem: (_item: Requirement) => void
  updateItem: (_id: string, _updates: Partial<Requirement>) => void
  removeItem: (_id: string) => void
  reset: () => void
  setCategories: (_categories: RequirementCategory[]) => void
  setFilters: (_filters: Partial<RequirementsState['filters']>) => void
  clearFilters: () => void
}

const initialState: RequirementsState = {
  items: [],
  loading: false,
  error: null,
  selectedItem: null,
  categories: [],
  filters: {},
}

export const useRequirementsStore = create<
  RequirementsState & RequirementsActions
>()(
  devtools(
    set => ({
      ...initialState,

      setItems: items => set({ items }),
      setLoading: loading => set({ loading }),
      setError: error => set({ error }),
      setSelectedItem: selectedItem => set({ selectedItem }),

      addItem: item =>
        set(state => ({
          items: [...state.items, item],
        })),

      updateItem: (id, updates) =>
        set(state => ({
          items: state.items.map(item =>
            item.id === id ? { ...item, ...updates } : item
          ),
        })),

      removeItem: id =>
        set(state => ({
          items: state.items.filter(item => item.id !== id),
        })),

      reset: () => set(initialState),

      setCategories: categories => set({ categories }),
      setFilters: filters =>
        set(state => ({
          filters: { ...state.filters, ...filters },
        })),
      clearFilters: () => set({ filters: {} }),
    }),
    { name: 'requirements-store' }
  )
)
