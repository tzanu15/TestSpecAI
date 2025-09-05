import { BaseEntity } from './api'

export interface Requirement extends BaseEntity {
  title: string
  description: string
  category_id: string
  source: string
  metadata: Record<string, any>
}

export interface RequirementCategory extends BaseEntity {
  name: string
  description: string
}

export interface RequirementCreate {
  title: string
  description: string
  category_id: string
  source?: string
  metadata?: Record<string, any>
}

export interface RequirementUpdate {
  title?: string
  description?: string
  category_id?: string
  metadata?: Record<string, any>
}
