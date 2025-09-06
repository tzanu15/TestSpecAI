import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { TestSpecification } from '../types/testSpecs'
import { BaseStoreActions, BaseStoreState } from './baseStore'

interface TestSpecsState extends BaseStoreState<TestSpecification> {
  filters: {
    functional_area?: string
    search?: string
  }
}

interface TestSpecsActions extends BaseStoreActions<TestSpecification> {
  setFilters: (_filters: Partial<TestSpecsState['filters']>) => void
  clearFilters: () => void
}

const initialState: TestSpecsState = {
  items: [] as TestSpecification[],
  loading: false,
  error: null,
  selectedItem: null,
  filters: {},
}

export const useTestSpecsStore = create<TestSpecsState & TestSpecsActions>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Base store actions
      setItems: (items) => set({ items }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      setSelectedItem: (selectedItem) => set({ selectedItem }),

      addItem: (item) => set((state) => ({
        items: [...state.items, item]
      })),

      updateItem: (id, updates) => set((state) => ({
        items: state.items.map(item =>
          item.id === id ? { ...item, ...updates } : item
        )
      })),

      removeItem: (id) => set((state) => ({
        items: state.items.filter(item => item.id !== id)
      })),

      reset: () => set(initialState),

      // Test specs specific actions
      setFilters: filters =>
        set(state => ({
          filters: { ...state.filters, ...filters },
        })),
      clearFilters: () => set({ filters: {} }),
    }),
    { name: 'test-specs-store' }
  )
)
