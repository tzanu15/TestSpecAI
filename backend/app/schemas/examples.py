"""
Example usage of TestSpecAI Pydantic schemas.

This module provides comprehensive examples of how to use the schemas
for API requests and responses, including validation scenarios.
"""

from uuid import uuid4
from datetime import datetime
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementResponse
from app.schemas.test_spec import (
    TestSpecificationCreate, TestStepCreate, GenericCommandReference,
    FunctionalArea, TestSpecificationResponse
)
from app.schemas.parameter import (
    ParameterCreate, ParameterVariantCreate, ParameterCategoryCreate,
    ParameterResponse, ParameterVariantResponse
)
from app.schemas.command import (
    GenericCommandCreate, CommandCategoryCreate, GenericCommandResponse
)


# Example UUIDs for demonstration
EXAMPLE_UUIDS = {
    "requirement_category": "550e8400-e29b-41d4-a716-446655440000",
    "parameter_category": "550e8400-e29b-41d4-a716-446655440001",
    "command_category": "550e8400-e29b-41d4-a716-446655440002",
    "requirement": "550e8400-e29b-41d4-a716-446655440003",
    "parameter": "550e8400-e29b-41d4-a716-446655440004",
    "command": "550e8400-e29b-41d4-a716-446655440005",
    "test_spec": "550e8400-e29b-41d4-a716-446655440006",
    "test_step": "550e8400-e29b-41d4-a716-446655440007",
}


class SchemaExamples:
    """Collection of schema usage examples."""

    @staticmethod
    def requirement_examples():
        """Examples for Requirement schemas."""

        # Create a new requirement
        create_example = RequirementCreate(
            created_by="user@example.com",
            title="Implement User Authentication",
            description="The system shall allow users to authenticate using username and password with support for multi-factor authentication.",
            category_id=EXAMPLE_UUIDS["requirement_category"],
            source="manual",
            metadata={
                "priority": "high",
                "version": "1.0",
                "reviewer": "john.doe@example.com",
                "tags": ["security", "authentication", "user-management"]
            }
        )

        # Update an existing requirement
        update_example = RequirementUpdate(
            title="Implement Enhanced User Authentication",
            description="The system shall allow users to authenticate using username and password with support for multi-factor authentication and biometric verification.",
            metadata={
                "priority": "high",
                "version": "1.1",
                "reviewer": "jane.smith@example.com",
                "tags": ["security", "authentication", "user-management", "biometric"]
            }
        )

        # Response example
        response_example = RequirementResponse(
            id=EXAMPLE_UUIDS["requirement"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 14, 30, 0),
            created_by="user@example.com",
            is_active=True,
            title="Implement User Authentication",
            description="The system shall allow users to authenticate using username and password with support for multi-factor authentication.",
            category_id=EXAMPLE_UUIDS["requirement_category"],
            source="manual",
            metadata={
                "priority": "high",
                "version": "1.0",
                "reviewer": "john.doe@example.com",
                "tags": ["security", "authentication", "user-management"]
            }
        )

        return {
            "create": create_example,
            "update": update_example,
            "response": response_example
        }

    @staticmethod
    def test_specification_examples():
        """Examples for Test Specification schemas."""

        # Create a test step
        test_step = TestStepCreate(
            created_by="user@example.com",
            test_specification_id=EXAMPLE_UUIDS["test_spec"],
            action=GenericCommandReference(
                command_id=EXAMPLE_UUIDS["command"],
                populated_parameters={
                    "Authentication": "Level 3",
                    "Timeout": "5000ms"
                }
            ),
            expected_result=GenericCommandReference(
                command_id=uuid4(),  # Different command for expected result
                populated_parameters={
                    "Response": "Success",
                    "Status": "Authenticated"
                }
            ),
            description="Perform authentication with Level 3 and verify successful response.",
            sequence_number=1
        )

        # Create a test specification
        create_example = TestSpecificationCreate(
            created_by="user@example.com",
            name="Verify Authentication Level 3",
            description="This test verifies the authentication mechanism at Level 3 for UDS communication.",
            requirement_ids=[EXAMPLE_UUIDS["requirement"]],
            precondition="System is in a clean state with no active sessions.",
            postcondition="System returns to initial state with authentication level set to Level 3.",
            test_data_description={
                "Authentication": "Level 3",
                "Timeout": "5000ms",
                "Expected_Response": "Success"
            },
            functional_area=FunctionalArea.UDS
        )

        # Response example
        response_example = TestSpecificationResponse(
            id=EXAMPLE_UUIDS["test_spec"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 14, 30, 0),
            created_by="user@example.com",
            is_active=True,
            name="Verify Authentication Level 3",
            description="This test verifies the authentication mechanism at Level 3 for UDS communication.",
            requirement_ids=[EXAMPLE_UUIDS["requirement"]],
            precondition="System is in a clean state with no active sessions.",
            test_steps=[],
            postcondition="System returns to initial state with authentication level set to Level 3.",
            test_data_description={
                "Authentication": "Level 3",
                "Timeout": "5000ms",
                "Expected_Response": "Success"
            },
            functional_area=FunctionalArea.UDS
        )

        return {
            "create": create_example,
            "response": response_example
        }

    @staticmethod
    def parameter_examples():
        """Examples for Parameter schemas."""

        # Create parameter category
        category_example = ParameterCategoryCreate(
            created_by="user@example.com",
            name="Authentication",
            description="Parameters related to authentication levels and security mechanisms."
        )

        # Create parameter variant
        variant_example = ParameterVariantCreate(
            created_by="user@example.com",
            parameter_id=EXAMPLE_UUIDS["parameter"],
            manufacturer="BMW",
            value="Level 3",
            description="Authentication level 3 for BMW vehicles with enhanced security features."
        )

        # Create parameter with variants
        create_example = ParameterCreate(
            created_by="user@example.com",
            name="Authentication Level",
            category_id=EXAMPLE_UUIDS["parameter_category"],
            has_variants=True,
            description="Authentication level parameter with manufacturer-specific variants."
        )

        # Create parameter without variants
        simple_parameter = ParameterCreate(
            created_by="user@example.com",
            name="Timeout",
            category_id=EXAMPLE_UUIDS["parameter_category"],
            has_variants=False,
            default_value="5000ms",
            description="Default timeout value for all operations."
        )

        # Response example
        response_example = ParameterResponse(
            id=EXAMPLE_UUIDS["parameter"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 14, 30, 0),
            created_by="user@example.com",
            is_active=True,
            name="Authentication Level",
            category_id=EXAMPLE_UUIDS["parameter_category"],
            has_variants=True,
            default_value=None,
            description="Authentication level parameter with manufacturer-specific variants.",
            variants=[
                ParameterVariantResponse(
                    id=uuid4(),
                    created_at=datetime(2023, 1, 1, 12, 0, 0),
                    updated_at=datetime(2023, 1, 15, 14, 30, 0),
                    created_by="user@example.com",
                    is_active=True,
                    parameter_id=EXAMPLE_UUIDS["parameter"],
                    manufacturer="BMW",
                    value="Level 3",
                    description="Authentication level 3 for BMW vehicles with enhanced security features."
                )
            ]
        )

        return {
            "category": category_example,
            "create_with_variants": create_example,
            "create_simple": simple_parameter,
            "response": response_example
        }

    @staticmethod
    def command_examples():
        """Examples for Command schemas."""

        # Create command category
        category_example = CommandCategoryCreate(
            created_by="user@example.com",
            name="UDS",
            description="Unified Diagnostic Services commands for automotive diagnostics."
        )

        # Create generic command
        create_example = GenericCommandCreate(
            created_by="user@example.com",
            template="Set level of authentication {Authentication} with timeout {Timeout}",
            category_id=EXAMPLE_UUIDS["command_category"],
            required_parameter_ids=[EXAMPLE_UUIDS["parameter"]],
            description="Command to set the authentication level with configurable timeout."
        )

        # Response example
        response_example = GenericCommandResponse(
            id=EXAMPLE_UUIDS["command"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 14, 30, 0),
            created_by="user@example.com",
            is_active=True,
            template="Set level of authentication {Authentication} with timeout {Timeout}",
            category_id=EXAMPLE_UUIDS["command_category"],
            required_parameter_ids=[EXAMPLE_UUIDS["parameter"]],
            description="Command to set the authentication level with configurable timeout."
        )

        return {
            "category": category_example,
            "create": create_example,
            "response": response_example
        }

    @staticmethod
    def validation_examples():
        """Examples of validation scenarios."""

        examples = {
            "valid_requirement": {
                "title": "Valid Requirement Title",
                "description": "This is a valid requirement description.",
                "source": "manual"
            },
            "invalid_requirement": {
                "title": "",  # Empty title - should fail
                "description": "This is a valid requirement description.",
                "source": "manual"
            },
            "valid_parameter_variants": {
                "has_variants": True,
                "default_value": None,
                "variants": [
                    {"manufacturer": "BMW", "value": "Level 3"},
                    {"manufacturer": "VW", "value": "Level 2"}
                ]
            },
            "invalid_parameter_variants": {
                "has_variants": True,
                "default_value": "Level 1",  # Should fail - can't have default with variants
                "variants": []
            },
            "valid_command_template": {
                "template": "Set level of authentication {Authentication}",
                "required_parameter_ids": [EXAMPLE_UUIDS["parameter"]]
            },
            "invalid_command_template": {
                "template": "Set level of authentication {InvalidParam}",  # Invalid parameter
                "required_parameter_ids": [EXAMPLE_UUIDS["parameter"]]
            }
        }

        return examples


def print_examples():
    """Print all schema examples."""
    examples = SchemaExamples()

    print("=" * 80)
    print("TestSpecAI Schema Usage Examples")
    print("=" * 80)

    print("\n1. Requirement Examples:")
    print("-" * 40)
    req_examples = examples.requirement_examples()
    print("Create Example:")
    print(req_examples["create"].model_dump_json(indent=2))

    print("\n2. Test Specification Examples:")
    print("-" * 40)
    test_examples = examples.test_specification_examples()
    print("Create Example:")
    print(test_examples["create"].model_dump_json(indent=2))

    print("\n3. Parameter Examples:")
    print("-" * 40)
    param_examples = examples.parameter_examples()
    print("Create with Variants Example:")
    print(param_examples["create_with_variants"].model_dump_json(indent=2))

    print("\n4. Command Examples:")
    print("-" * 40)
    cmd_examples = examples.command_examples()
    print("Create Example:")
    print(cmd_examples["create"].model_dump_json(indent=2))

    print("\n5. Validation Examples:")
    print("-" * 40)
    validation_examples = examples.validation_examples()
    print("Valid Parameter Variants:")
    print(validation_examples["valid_parameter_variants"])
    print("\nInvalid Parameter Variants:")
    print(validation_examples["invalid_parameter_variants"])


if __name__ == "__main__":
    print_examples()
