import { z } from 'zod'

// Requirement validation schemas
export const requirementCreateSchema = z.object({
  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(255, 'Title must not exceed 255 characters'),
  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must not exceed 2000 characters'),
  category_id: z.string().uuid('Invalid category ID'),
  source: z.enum(['manual', 'document', 'import']).default('manual'),
  metadata: z.record(z.any()).optional(),
})

export const requirementUpdateSchema = z.object({
  title: z.string()
    .min(3, 'Title must be at least 3 characters')
    .max(255, 'Title must not exceed 255 characters')
    .optional(),
  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must not exceed 2000 characters')
    .optional(),
  category_id: z.string().uuid('Invalid category ID').optional(),
  metadata: z.record(z.any()).optional(),
})

// Category validation schemas
export const categoryCreateSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must not exceed 100 characters'),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})

export const categoryUpdateSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must not exceed 100 characters')
    .optional(),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})

// Test specification validation schemas
export const testSpecCreateSchema = z.object({
  name: z.string()
    .min(3, 'Name must be at least 3 characters')
    .max(255, 'Name must not exceed 255 characters'),
  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must not exceed 2000 characters'),
  requirement_ids: z.array(z.string().uuid()).min(1, 'At least one requirement is required'),
  precondition: z.string()
    .min(5, 'Precondition must be at least 5 characters')
    .max(1000, 'Precondition must not exceed 1000 characters'),
  postcondition: z.string()
    .min(5, 'Postcondition must be at least 5 characters')
    .max(1000, 'Postcondition must not exceed 1000 characters'),
  functional_area: z.enum(['UDS', 'Communication', 'ErrorHandler', 'CyberSecurity']),
  test_data_description: z.record(z.any()).optional(),
})

export const testSpecUpdateSchema = z.object({
  name: z.string()
    .min(3, 'Name must be at least 3 characters')
    .max(255, 'Name must not exceed 255 characters')
    .optional(),
  description: z.string()
    .min(10, 'Description must be at least 10 characters')
    .max(2000, 'Description must not exceed 2000 characters')
    .optional(),
  requirement_ids: z.array(z.string().uuid()).min(1, 'At least one requirement is required').optional(),
  precondition: z.string()
    .min(5, 'Precondition must be at least 5 characters')
    .max(1000, 'Precondition must not exceed 1000 characters')
    .optional(),
  postcondition: z.string()
    .min(5, 'Postcondition must be at least 5 characters')
    .max(1000, 'Postcondition must not exceed 1000 characters')
    .optional(),
  functional_area: z.enum(['UDS', 'Communication', 'ErrorHandler', 'CyberSecurity']).optional(),
  test_data_description: z.record(z.any()).optional(),
})

// Parameter validation schemas
export const parameterCreateSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must not exceed 100 characters'),
  category_id: z.string().uuid('Invalid category ID'),
  has_variants: z.boolean().default(false),
  default_value: z.string().optional(),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})

export const parameterUpdateSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must not exceed 100 characters')
    .optional(),
  category_id: z.string().uuid('Invalid category ID').optional(),
  has_variants: z.boolean().optional(),
  default_value: z.string().optional(),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})

// Command validation schemas
export const commandCreateSchema = z.object({
  template: z.string()
    .min(5, 'Template must be at least 5 characters')
    .max(500, 'Template must not exceed 500 characters'),
  category_id: z.string().uuid('Invalid category ID'),
  required_parameters: z.array(z.string().uuid()).optional(),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})

export const commandUpdateSchema = z.object({
  template: z.string()
    .min(5, 'Template must be at least 5 characters')
    .max(500, 'Template must not exceed 500 characters')
    .optional(),
  category_id: z.string().uuid('Invalid category ID').optional(),
  required_parameters: z.array(z.string().uuid()).optional(),
  description: z.string()
    .min(5, 'Description must be at least 5 characters')
    .max(500, 'Description must not exceed 500 characters')
    .optional(),
})
