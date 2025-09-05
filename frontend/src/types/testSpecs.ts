import { BaseEntity } from './api'

export interface TestStep {
  id: string
  test_specification_id: string
  action: GenericCommandReference
  expected_result: GenericCommandReference
  description?: string
  sequence_number: number
}

export interface TestSpecification extends BaseEntity {
  name: string
  description: string
  requirement_ids: string[]
  precondition: string
  test_steps: TestStep[]
  postcondition: string
  test_data_description: Record<string, any>
  functional_area: 'UDS' | 'Communication' | 'ErrorHandler' | 'CyberSecurity'
}

export interface GenericCommandReference {
  command_id: string
  command_template: string
  populated_parameters: Record<string, string>
}

export interface TestSpecificationCreate {
  name: string
  description: string
  requirement_ids: string[]
  precondition: string
  test_steps: Omit<TestStep, 'id' | 'test_specification_id'>[]
  postcondition: string
  test_data_description: Record<string, any>
  functional_area: 'UDS' | 'Communication' | 'ErrorHandler' | 'CyberSecurity'
}

export interface TestSpecificationUpdate {
  name?: string
  description?: string
  requirement_ids?: string[]
  precondition?: string
  test_steps?: Omit<TestStep, 'id' | 'test_specification_id'>[]
  postcondition?: string
  test_data_description?: Record<string, any>
  functional_area?: 'UDS' | 'Communication' | 'ErrorHandler' | 'CyberSecurity'
}
