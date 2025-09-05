import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export interface BaseStoreState<T> {
  items: T[]
  loading: boolean
  error: string | null
  selectedItem: T | null
}

export interface BaseStoreActions<T> {
  setItems: (_items: T[]) => void
  setLoading: (_loading: boolean) => void
  setError: (_error: string | null) => void
  setSelectedItem: (_item: T | null) => void
  addItem: (_item: T) => void
  updateItem: (_id: string, _updates: Partial<T>) => void
  removeItem: (_id: string) => void
  reset: () => void
}

export function createBaseStore<T extends { id: string }>(
  name: string,
  initialState: BaseStoreState<T>
) {
  return create<BaseStoreState<T> & BaseStoreActions<T>>()(
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
      }),
      { name }
    )
  )
}
