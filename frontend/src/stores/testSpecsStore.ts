import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { TestSpecification } from '../types/testSpecs'
import { createBaseStore } from './baseStore'

interface TestSpecsState {
  filters: {
    functional_area?: string
    search?: string
  }
}

interface TestSpecsActions {
  setFilters: (_filters: Partial<TestSpecsState['filters']>) => void
  clearFilters: () => void
}

const initialState = {
  items: [] as TestSpecification[],
  loading: false,
  error: null,
  selectedItem: null,
  filters: {} as TestSpecsState['filters'],
}

export const useTestSpecsStore = create<TestSpecsState & TestSpecsActions>()(
  devtools(
    set => ({
      ...initialState,

      setFilters: filters =>
        set(state => ({
          filters: { ...state.filters, ...filters },
        })),
      clearFilters: () => set({ filters: {} }),

      // Inherit base actions
      ...createBaseStore('testSpecs', initialState),
    }),
    { name: 'test-specs-store' }
  )
)
