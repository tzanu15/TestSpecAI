import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

// Mock API handlers
export const handlers = [
  // Requirements endpoints
  http.get('/api/v1/requirements', () => {
    return HttpResponse.json([
      {
        id: '1',
        title: 'Test Requirement',
        description: 'Test Description',
        category_id: 'test-category',
        source: 'manual',
        metadata: {},
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        created_by: 'test-user',
        is_active: true,
      },
    ])
  }),

  http.post('/api/v1/requirements', () => {
    return HttpResponse.json({
      id: '2',
      title: 'New Requirement',
      description: 'New Description',
      category_id: 'test-category',
      source: 'manual',
      metadata: {},
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      created_by: 'test-user',
      is_active: true,
    })
  }),

  // Test specifications endpoints
  http.get('/api/v1/test-specifications', () => {
    return HttpResponse.json([])
  }),

  // Parameters endpoints
  http.get('/api/v1/parameters', () => {
    return HttpResponse.json([])
  }),

  // Commands endpoints
  http.get('/api/v1/commands', () => {
    return HttpResponse.json([])
  }),
]

export const server = setupServer(...handlers)
