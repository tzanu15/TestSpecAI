import { BaseEntity } from './api'

export interface GenericCommand extends BaseEntity {
  template: string
  category_id: string
  required_parameters: string[]
  description: string
}

export interface CommandCategory extends BaseEntity {
  name: string
  description: string
}

export interface GenericCommandCreate {
  template: string
  category_id: string
  required_parameters: string[]
  description: string
}

export interface GenericCommandUpdate {
  template?: string
  category_id?: string
  required_parameters?: string[]
  description?: string
}
