import { useEffect, useState } from 'react'
import { testSpecsService } from '../services/testSpecs'
import { useTestSpecsStore } from '../stores/testSpecsStore'
import {
    TestSpecificationCreate,
    TestSpecificationUpdate
} from '../types/testSpecs'

export const useTestSpecs = () => {
  const store = useTestSpecsStore()
  const [isInitialized, setIsInitialized] = useState(false)

  // Load test specifications on mount
  useEffect(() => {
    if (!isInitialized) {
      loadTestSpecifications()
      setIsInitialized(true)
    }
  }, [isInitialized])

  const loadTestSpecifications = async () => {
    try {
      store.setLoading(true)
      store.setError(null)
      const testSpecs = await testSpecsService.getTestSpecifications(store.filters)
      store.setItems(testSpecs)
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to load test specifications')
    } finally {
      store.setLoading(false)
    }
  }

  const createTestSpecification = async (data: TestSpecificationCreate) => {
    try {
      store.setLoading(true)
      const newTestSpec = await testSpecsService.createTestSpecification(data)
      store.addItem(newTestSpec)
      return newTestSpec
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to create test specification')
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const updateTestSpecification = async (id: string, data: TestSpecificationUpdate) => {
    try {
      store.setLoading(true)
      const updatedTestSpec = await testSpecsService.updateTestSpecification(id, data)
      store.updateItem(id, updatedTestSpec)
      return updatedTestSpec
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to update test specification')
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const deleteTestSpecification = async (id: string) => {
    try {
      store.setLoading(true)
      await testSpecsService.deleteTestSpecification(id)
      store.removeItem(id)
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to delete test specification')
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const duplicateTestSpecification = async (id: string) => {
    try {
      store.setLoading(true)
      const originalSpec = await testSpecsService.getTestSpecification(id)

      const duplicateData: TestSpecificationCreate = {
        name: `${originalSpec.name} (Copy)`,
        description: originalSpec.description,
        requirement_ids: originalSpec.requirement_ids,
        precondition: originalSpec.precondition,
        test_steps: originalSpec.test_steps.map(step => ({
          action: step.action,
          expected_result: step.expected_result,
          description: step.description,
          sequence_number: step.sequence_number,
        })),
        postcondition: originalSpec.postcondition,
        test_data_description: originalSpec.test_data_description,
        functional_area: originalSpec.functional_area,
      }

      const duplicatedSpec = await testSpecsService.createTestSpecification(duplicateData)
      store.addItem(duplicatedSpec)
      return duplicatedSpec
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to duplicate test specification')
      throw error
    } finally {
      store.setLoading(false)
    }
  }

  const searchTestSpecifications = async (search: string) => {
    try {
      store.setLoading(true)
      store.setError(null)
      const testSpecs = await testSpecsService.getTestSpecifications({
        ...store.filters,
        search,
      })
      store.setItems(testSpecs)
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to search test specifications')
    } finally {
      store.setLoading(false)
    }
  }

  const filterTestSpecifications = async (filters: { functional_area?: string }) => {
    try {
      store.setLoading(true)
      store.setError(null)
      store.setFilters(filters)
      const testSpecs = await testSpecsService.getTestSpecifications({
        ...store.filters,
        ...filters,
      })
      store.setItems(testSpecs)
    } catch (error) {
      store.setError(error instanceof Error ? error.message : 'Failed to filter test specifications')
    } finally {
      store.setLoading(false)
    }
  }

  return {
    // State
    testSpecifications: store.items,
    loading: store.loading,
    error: store.error,
    selectedTestSpec: store.selectedItem,
    filters: store.filters,

    // Actions
    loadTestSpecifications,
    createTestSpecification,
    updateTestSpecification,
    deleteTestSpecification,
    duplicateTestSpecification,
    searchTestSpecifications,
    filterTestSpecifications,
    setSelectedTestSpec: store.setSelectedItem,
    setFilters: store.setFilters,
    clearFilters: store.clearFilters,
  }
}
