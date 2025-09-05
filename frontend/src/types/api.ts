export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
  created_by: string
  is_active: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ApiError {
  detail: string
  type: string
}

export interface LoadingState {
  isLoading: boolean
  error: string | null
}
