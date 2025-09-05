import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Parameter, ParameterCategory } from '../types/parameters'
import { createBaseStore } from './baseStore'

interface ParametersState {
  categories: ParameterCategory[]
  filters: {
    category_id?: string
    search?: string
  }
}

interface ParametersActions {
  setCategories: (_categories: ParameterCategory[]) => void
  setFilters: (_filters: Partial<ParametersState['filters']>) => void
  clearFilters: () => void
}

const initialState = {
  items: [] as Parameter[],
  loading: false,
  error: null,
  selectedItem: null,
  categories: [] as ParameterCategory[],
  filters: {} as ParametersState['filters'],
}

export const useParametersStore = create<ParametersState & ParametersActions>()(
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
      ...createBaseStore('parameters', initialState),
    }),
    { name: 'parameters-store' }
  )
)
