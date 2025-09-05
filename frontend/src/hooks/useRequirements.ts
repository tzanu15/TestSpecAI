import { useEffect, useState } from 'react'
import { requirementsService } from '../services/requirements'
import { useRequirementsStore } from '../stores/requirementsStore'
import { RequirementCreate, RequirementUpdate } from '../types/requirements'

export const useRequirements = () => {
  const store = useRequirementsStore()
  const [isInitialized, setIsInitialized] = useState(false)

  // Load requirements on mount
  useEffect(() => {
    if (!isInitialized) {
      loadRequirements()
      loadCategories()
      setIsInitialized(true)
    }
  }, [isInitialized])

  const loadRequirements = async () => {
    try {
      store.setLoading(true)
      store.setError(null)
      const requirements = await requirementsService.getRequirements(
        store.filters
      )
      store.setItems(requirements)
    } catch (error) {
      store.setError(
        error instanceof Error ? error.message : 'Failed to load requirements'
      )
    } finally {
      store.setLoading(false)
    }
  }

  const createRequirement = async (data: RequirementCreate) => {
    try {
      store.setLoading(true)
      const newRequirement = await requirementsService.createRequirement(data)
      store.addItem(newRequirement)
      return newRequirement
    } catch (error) {
      store.setError(
        error instanceof Error ? error.message : 'Failed to create requirement'
      )
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const updateRequirement = async (id: string, data: RequirementUpdate) => {
    try {
      store.setLoading(true)
      const updatedRequirement = await requirementsService.updateRequirement(
        id,
        data
      )
      store.updateItem(id, updatedRequirement)
      return updatedRequirement
    } catch (error) {
      store.setError(
        error instanceof Error ? error.message : 'Failed to update requirement'
      )
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const deleteRequirement = async (id: string) => {
    try {
      store.setLoading(true)
      await requirementsService.deleteRequirement(id)
      store.removeItem(id)
    } catch (error) {
      store.setError(
        error instanceof Error ? error.message : 'Failed to delete requirement'
      )
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const categories = await requirementsService.getCategories()
      store.setCategories(categories)
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  return {
    // State
    requirements: store.items,
    categories: store.categories,
    loading: store.loading,
    error: store.error,
    selectedRequirement: store.selectedItem,
    filters: store.filters,

    // Actions
    loadRequirements,
    createRequirement,
    updateRequirement,
    deleteRequirement,
    setSelectedRequirement: store.setSelectedItem,
    setFilters: store.setFilters,
    clearFilters: store.clearFilters,
  }
}
