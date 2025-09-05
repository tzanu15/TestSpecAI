import { BaseEntity } from './api'

export interface ParameterVariant {
  id: string
  parameter_id: string
  manufacturer: string
  value: string
  description: string
}

export interface Parameter extends BaseEntity {
  name: string
  category_id: string
  has_variants: boolean
  default_value?: string
  variants: ParameterVariant[]
  description: string
}

export interface ParameterCategory extends BaseEntity {
  name: string
  description: string
}

export interface ParameterCreate {
  name: string
  category_id: string
  has_variants: boolean
  default_value?: string
  description: string
}

export interface ParameterUpdate {
  name?: string
  category_id?: string
  has_variants?: boolean
  default_value?: string
  description?: string
}

export interface ParameterVariantCreate {
  parameter_id: string
  manufacturer: string
  value: string
  description: string
}

export interface ParameterVariantUpdate {
  manufacturer?: string
  value?: string
  description?: string
}
