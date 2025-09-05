import {
    Requirement,
    RequirementCategory,
    RequirementCreate,
    RequirementUpdate,
} from '../types/requirements'
import { apiService } from './api'

export class RequirementsService {
  async getRequirements(params?: {
    skip?: number
    limit?: number
    category_id?: string
    search?: string
  }): Promise<Requirement[]> {
    return apiService.get<Requirement[]>('/requirements', params)
  }

  async getRequirement(id: string): Promise<Requirement> {
    return apiService.get<Requirement>(`/requirements/${id}`)
  }

  async createRequirement(data: RequirementCreate): Promise<Requirement> {
    return apiService.post<Requirement>('/requirements', data)
  }

  async updateRequirement(
    id: string,
    data: RequirementUpdate
  ): Promise<Requirement> {
    return apiService.put<Requirement>(`/requirements/${id}`, data)
  }

  async deleteRequirement(id: string): Promise<void> {
    return apiService.delete<void>(`/requirements/${id}`)
  }

  async getCategories(): Promise<RequirementCategory[]> {
    return apiService.get<RequirementCategory[]>('/requirements/categories')
  }
}

export const requirementsService = new RequirementsService()
