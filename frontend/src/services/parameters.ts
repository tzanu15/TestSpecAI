import {
    Parameter,
    ParameterCategory,
    ParameterCreate,
    ParameterUpdate,
    ParameterVariant,
    ParameterVariantCreate,
    ParameterVariantUpdate,
} from '../types/parameters'
import { apiService } from './api'

export class ParametersService {
  async getParameters(params?: {
    skip?: number
    limit?: number
    category_id?: string
    search?: string
  }): Promise<Parameter[]> {
    return apiService.get<Parameter[]>('/parameters', params)
  }

  async getParameter(id: string): Promise<Parameter> {
    return apiService.get<Parameter>(`/parameters/${id}`)
  }

  async createParameter(data: ParameterCreate): Promise<Parameter> {
    return apiService.post<Parameter>('/parameters', data)
  }

  async updateParameter(id: string, data: ParameterUpdate): Promise<Parameter> {
    return apiService.put<Parameter>(`/parameters/${id}`, data)
  }

  async deleteParameter(id: string): Promise<void> {
    return apiService.delete<void>(`/parameters/${id}`)
  }

  async getCategories(): Promise<ParameterCategory[]> {
    return apiService.get<ParameterCategory[]>('/parameters/categories')
  }

  async createCategory(data: {
    name: string
    description: string
  }): Promise<ParameterCategory> {
    return apiService.post<ParameterCategory>('/parameters/categories', data)
  }

  async getVariants(parameterId: string): Promise<ParameterVariant[]> {
    return apiService.get<ParameterVariant[]>(
      `/parameters/${parameterId}/variants`
    )
  }

  async createVariant(data: ParameterVariantCreate): Promise<ParameterVariant> {
    return apiService.post<ParameterVariant>('/parameters/variants', data)
  }

  async updateVariant(
    id: string,
    data: ParameterVariantUpdate
  ): Promise<ParameterVariant> {
    return apiService.put<ParameterVariant>(`/parameters/variants/${id}`, data)
  }

  async deleteVariant(id: string): Promise<void> {
    return apiService.delete<void>(`/parameters/variants/${id}`)
  }
}

export const parametersService = new ParametersService()
