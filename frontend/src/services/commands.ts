import {
    CommandCategory,
    GenericCommand,
    GenericCommandCreate,
    GenericCommandUpdate,
} from '../types/commands'
import { apiService } from './api'

export class CommandsService {
  async getCommands(params?: {
    skip?: number
    limit?: number
    category_id?: string
    search?: string
  }): Promise<GenericCommand[]> {
    return apiService.get<GenericCommand[]>('/commands', params)
  }

  async getCommand(id: string): Promise<GenericCommand> {
    return apiService.get<GenericCommand>(`/commands/${id}`)
  }

  async createCommand(data: GenericCommandCreate): Promise<GenericCommand> {
    return apiService.post<GenericCommand>('/commands', data)
  }

  async updateCommand(
    id: string,
    data: GenericCommandUpdate
  ): Promise<GenericCommand> {
    return apiService.put<GenericCommand>(`/commands/${id}`, data)
  }

  async deleteCommand(id: string): Promise<void> {
    return apiService.delete<void>(`/commands/${id}`)
  }

  async getCategories(): Promise<CommandCategory[]> {
    return apiService.get<CommandCategory[]>('/commands/categories')
  }

  async createCategory(data: {
    name: string
    description: string
  }): Promise<CommandCategory> {
    return apiService.post<CommandCategory>('/commands/categories', data)
  }
}

export const commandsService = new CommandsService()
