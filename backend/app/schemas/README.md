# TestSpecAI Pydantic Schemas Documentation

This directory contains all Pydantic schemas used for API validation, request/response serialization, and data validation in the TestSpecAI application.

## Overview

The schema system is organized into several modules:

- **`base.py`** - Foundational schema classes with common validation patterns
- **`validators.py`** - Custom validators and complex validation rules
- **`requirement.py`** - Schemas for Requirement entities
- **`test_spec.py`** - Schemas for TestSpecification and TestStep entities
- **`parameter.py`** - Schemas for Parameter, ParameterCategory, and ParameterVariant entities
- **`command.py`** - Schemas for GenericCommand and CommandCategory entities

## Base Schema Classes

### BaseSchema
The foundation for all entity schemas, providing common fields:
- `id`: UUID primary key
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `created_by`: User who created the entity
- `is_active`: Soft delete flag

### BaseCreateSchema
Schema for creating new entities, excluding system-managed fields.

### BaseUpdateSchema
Schema for updating existing entities with optional fields.

### BaseResponseSchema
Schema for API responses, inheriting from BaseSchema.

## Validation System

### ValidationRules
Static methods for common validation patterns:
- `validate_name_format()` - Validates entity names
- `validate_manufacturer_name()` - Validates manufacturer names
- `validate_parameter_placeholder()` - Validates parameter placeholders
- `validate_template_parameters()` - Extracts and validates template parameters
- `validate_parameter_value()` - Validates parameter values
- `validate_description_length()` - Validates description lengths
- `validate_unique_uuids()` - Ensures UUID list uniqueness
- `validate_sequence_numbers()` - Validates sequence number consistency

### BusinessRuleValidators
Validators for complex business rules:
- `validate_parameter_variants_consistency()` - Ensures parameter variants are consistent
- `validate_command_template_parameters()` - Validates command template parameters
- `validate_test_step_sequence_consistency()` - Validates test step sequences
- `validate_requirement_test_spec_relationship()` - Validates requirement relationships
- `validate_manufacturer_variant_uniqueness()` - Ensures unique manufacturers
- `validate_functional_area_consistency()` - Validates functional area consistency

### CrossEntityValidators
Validators for cross-entity relationships:
- `validate_parameter_command_compatibility()` - Validates parameter-command compatibility
- `validate_test_step_command_references()` - Validates test step command references
- `validate_category_entity_consistency()` - Validates category-entity consistency

## Entity Schemas

### Requirement Schemas
- `RequirementBase` - Base requirement schema
- `RequirementCreate` - Schema for creating requirements
- `RequirementUpdate` - Schema for updating requirements
- `RequirementResponse` - Schema for requirement responses
- `RequirementListResponse` - Schema for paginated requirement lists

### Test Specification Schemas
- `FunctionalArea` - Enum for functional areas (UDS, Communication, ErrorHandler, CyberSecurity)
- `GenericCommandReference` - Schema for referencing commands with parameters
- `TestStepBase` - Base test step schema
- `TestStepCreate` - Schema for creating test steps
- `TestStepUpdate` - Schema for updating test steps
- `TestStepResponse` - Schema for test step responses
- `TestSpecificationBase` - Base test specification schema
- `TestSpecificationCreate` - Schema for creating test specifications
- `TestSpecificationUpdate` - Schema for updating test specifications
- `TestSpecificationResponse` - Schema for test specification responses
- `TestSpecificationListResponse` - Schema for paginated test specification lists

### Parameter Schemas
- `ParameterCategoryBase` - Base parameter category schema
- `ParameterCategoryCreate` - Schema for creating parameter categories
- `ParameterCategoryUpdate` - Schema for updating parameter categories
- `ParameterCategoryResponse` - Schema for parameter category responses
- `ParameterVariantBase` - Base parameter variant schema
- `ParameterVariantCreate` - Schema for creating parameter variants
- `ParameterVariantUpdate` - Schema for updating parameter variants
- `ParameterVariantResponse` - Schema for parameter variant responses
- `ParameterBase` - Base parameter schema
- `ParameterCreate` - Schema for creating parameters
- `ParameterUpdate` - Schema for updating parameters
- `ParameterResponse` - Schema for parameter responses
- `ParameterListResponse` - Schema for paginated parameter lists

### Command Schemas
- `CommandCategoryBase` - Base command category schema
- `CommandCategoryCreate` - Schema for creating command categories
- `CommandCategoryUpdate` - Schema for updating command categories
- `CommandCategoryResponse` - Schema for command category responses
- `GenericCommandBase` - Base generic command schema
- `GenericCommandCreate` - Schema for creating generic commands
- `GenericCommandUpdate` - Schema for updating generic commands
- `GenericCommandResponse` - Schema for generic command responses
- `GenericCommandListResponse` - Schema for paginated generic command lists

## Usage Examples

### Creating a Requirement
```python
from app.schemas.requirement import RequirementCreate

requirement_data = RequirementCreate(
    created_by="user@example.com",
    title="Implement User Authentication",
    description="The system shall allow users to authenticate using username and password.",
    category_id="550e8400-e29b-41d4-a716-446655440000",
    source="manual",
    metadata={"priority": "high", "version": "1.0"}
)
```

### Creating a Test Specification
```python
from app.schemas.test_spec import TestSpecificationCreate, TestStepCreate, GenericCommandReference

test_step = TestStepCreate(
    created_by="user@example.com",
    test_specification_id="550e8400-e29b-41d4-a716-446655440000",
    action=GenericCommandReference(
        command_id="550e8400-e29b-41d4-a716-446655440001",
        populated_parameters={"Authentication": "Level 3"}
    ),
    expected_result=GenericCommandReference(
        command_id="550e8400-e29b-41d4-a716-446655440002",
        populated_parameters={"Response": "Success"}
    ),
    description="Perform authentication with Level 3.",
    sequence_number=1
)

test_spec = TestSpecificationCreate(
    created_by="user@example.com",
    name="Verify Authentication Level 3",
    description="This test verifies the authentication mechanism at Level 3.",
    requirement_ids=["550e8400-e29b-41d4-a716-446655440000"],
    precondition="System is in a clean state.",
    test_steps=[test_step],
    postcondition="System returns to initial state.",
    test_data_description={"Authentication": "Level 3"},
    functional_area="CyberSecurity"
)
```

### Creating a Parameter with Variants
```python
from app.schemas.parameter import ParameterCreate, ParameterVariantCreate

parameter_variant = ParameterVariantCreate(
    created_by="user@example.com",
    parameter_id="550e8400-e29b-41d4-a716-446655440000",
    manufacturer="BMW",
    value="Level 3",
    description="Authentication level 3 for BMW vehicles."
)

parameter = ParameterCreate(
    created_by="user@example.com",
    name="Authentication",
    category_id="550e8400-e29b-41d4-a716-446655440001",
    has_variants=True,
    description="Authentication level parameter.",
    variants=[parameter_variant]
)
```

### Creating a Generic Command
```python
from app.schemas.command import GenericCommandCreate

command = GenericCommandCreate(
    created_by="user@example.com",
    template="Set level of authentication {Authentication}",
    category_id="550e8400-e29b-41d4-a716-446655440000",
    required_parameter_ids=["550e8400-e29b-41d4-a716-446655440001"],
    description="Command to set the authentication level."
)
```

## Validation Examples

### Custom Validation
```python
from app.schemas.validators import ValidationRules

# Validate name format
try:
    valid_name = ValidationRules.validate_name_format("Test Parameter", "parameter name")
    print(f"Valid name: {valid_name}")
except ValueError as e:
    print(f"Invalid name: {e}")

# Validate template parameters
try:
    template = "Set level of authentication {Authentication} and read {DTC_Code}"
    params = ValidationRules.validate_template_parameters(template)
    print(f"Template parameters: {params}")
except ValueError as e:
    print(f"Invalid template: {e}")
```

### Business Rule Validation
```python
from app.schemas.validators import BusinessRuleValidators

# Validate parameter variants consistency
try:
    BusinessRuleValidators.validate_parameter_variants_consistency(
        has_variants=True,
        default_value=None,
        variants=[{"manufacturer": "BMW", "value": "Level 3"}]
    )
    print("Parameter variants are consistent")
except ValueError as e:
    print(f"Inconsistent variants: {e}")
```

## Error Handling

All schemas include comprehensive error handling with descriptive error messages. Common error types include:

- **ValidationError**: Field validation failures
- **ValueError**: Business rule violations
- **TypeError**: Type mismatches

## Configuration

Schemas use Pydantic v2 configuration with:
- `from_attributes=True` for ORM integration
- `validate_assignment=True` for assignment validation
- `str_strip_whitespace=True` for automatic whitespace trimming
- `extra="forbid"` to prevent extra fields
- Custom JSON encoders for datetime and UUID fields

## Testing

Run the validator test suite to verify all validation rules:

```bash
cd backend
python test_validators.py
```

This will test all custom validators and business rules to ensure they work correctly.
