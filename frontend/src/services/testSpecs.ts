import {
  TestSpecification,
  TestSpecificationCreate,
  TestSpecificationUpdate,
} from '../types/testSpecs'
import { apiService } from './api'

export class TestSpecsService {
  async getTestSpecifications(params?: {
    skip?: number
    limit?: number
    functional_area?: string
    search?: string
  }): Promise<TestSpecification[]> {
    const response = await apiService.get<{ items: TestSpecification[]; total: number; page: number; per_page: number; total_pages: number }>('/test-specifications', params)
    return response.items
  }

  async getTestSpecification(id: string): Promise<TestSpecification> {
    return apiService.get<TestSpecification>(`/test-specifications/${id}`)
  }

  async createTestSpecification(
    data: TestSpecificationCreate
  ): Promise<TestSpecification> {
    return apiService.post<TestSpecification>('/test-specifications', data)
  }

  async updateTestSpecification(
    id: string,
    data: TestSpecificationUpdate
  ): Promise<TestSpecification> {
    return apiService.put<TestSpecification>(`/test-specifications/${id}`, data)
  }

  async deleteTestSpecification(id: string): Promise<void> {
    return apiService.delete<void>(`/test-specifications/${id}`)
  }
}

export const testSpecsService = new TestSpecsService()
