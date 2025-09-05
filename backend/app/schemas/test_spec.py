"""
Pydantic schemas for Test Specification and Test Step entities.

This module provides validation schemas for TestSpecifications and TestSteps
including create, update, and response schemas with appropriate validation rules.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from .base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from .validators import ValidationRules, BusinessRuleValidators, CrossEntityValidators


class FunctionalArea(str, Enum):
    """Enum for functional areas."""
    UDS = "UDS"
    COMMUNICATION = "Communication"
    ERROR_HANDLER = "ErrorHandler"
    CYBER_SECURITY = "CyberSecurity"


class GenericCommandReference(BaseModel):
    """
    Schema for generic command references with populated parameters.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "extra": "forbid"
    }

    command_id: UUID = Field(
        ...,
        description="ID of the generic command",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    command_template: Optional[str] = Field(
        None,
        description="Template of the generic command (for reference)",
        examples=["Set level of authentication {Authentication}", "Read DTC {DTC_Type}"]
    )
    populated_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters populated for this command instance",
        examples=[{"Authentication": "Level1", "DTC_Type": "All"}]
    )

    @field_validator('populated_parameters')
    @classmethod
    def validate_populated_parameters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate populated parameters."""
        if not isinstance(v, dict):
            raise ValueError('Populated parameters must be a dictionary')
        return v


class TestStepBase(BaseModel):
    """
    Base schema for Test Step entities with common fields and validation.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid"
    }

    test_specification_id: UUID = Field(
        ...,
        description="ID of the test specification this step belongs to",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    action: GenericCommandReference = Field(
        ...,
        description="Action to be performed in this test step"
    )
    expected_result: GenericCommandReference = Field(
        ...,
        description="Expected result for this test step"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the test step",
        examples=["Initialize the ECU", "Verify authentication level", "Check DTC status"]
    )
    sequence_number: int = Field(
        ...,
        ge=1,
        description="Sequence number of the test step within the test specification",
        examples=[1, 2, 3, 10]
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate test step description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @model_validator(mode='after')
    def validate_action_and_result(self):
        """Validate that action and expected_result have different command_ids."""
        if self.action.command_id == self.expected_result.command_id:
            raise ValueError('Action and expected result cannot use the same command')
        return self


class TestStepCreate(TestStepBase, BaseCreateSchema):
    """
    Schema for creating new test steps.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "test_specification_id": "550e8400-e29b-41d4-a716-446655440000",
                    "action": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440001",
                        "populated_parameters": {"Authentication": "Level1"}
                    },
                    "expected_result": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440002",
                        "populated_parameters": {"Status": "Success"}
                    },
                    "description": "Initialize authentication",
                    "sequence_number": 1,
                    "created_by": "admin"
                }
            ]
        }
    }


class TestStepUpdate(BaseUpdateSchema):
    """
    Schema for updating existing test steps.
    All fields are optional to allow partial updates.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "action": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440001",
                        "populated_parameters": {"Authentication": "Level2"}
                    },
                    "expected_result": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440002",
                        "populated_parameters": {"Status": "Success"}
                    },
                    "description": "Updated test step description",
                    "sequence_number": 2
                }
            ]
        }
    }

    test_specification_id: Optional[UUID] = Field(
        None,
        description="ID of the test specification this step belongs to",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    action: Optional[GenericCommandReference] = Field(
        None,
        description="Action to be performed in this test step"
    )
    expected_result: Optional[GenericCommandReference] = Field(
        None,
        description="Expected result for this test step"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the test step",
        examples=["Initialize the ECU", "Verify authentication level", "Check DTC status"]
    )
    sequence_number: Optional[int] = Field(
        None,
        ge=1,
        description="Sequence number of the test step within the test specification",
        examples=[1, 2, 3, 10]
    )

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate test step description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @model_validator(mode='after')
    def validate_action_and_result(self):
        """Validate that action and expected_result have different command_ids if both provided."""
        if self.action and self.expected_result:
            if self.action.command_id == self.expected_result.command_id:
                raise ValueError('Action and expected result cannot use the same command')
        return self


class TestStepResponse(TestStepBase, BaseResponseSchema):
    """
    Schema for test step API responses.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": False,  # Responses are read-only
        "str_strip_whitespace": False,  # Don't modify response data
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "test_specification_id": "550e8400-e29b-41d4-a716-446655440001",
                    "action": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440002",
                        "command_template": "Set level of authentication {Authentication}",
                        "populated_parameters": {"Authentication": "Level1"}
                    },
                    "expected_result": {
                        "command_id": "550e8400-e29b-41d4-a716-446655440003",
                        "command_template": "Verify authentication status {Status}",
                        "populated_parameters": {"Status": "Success"}
                    },
                    "description": "Initialize authentication",
                    "sequence_number": 1,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True
                }
            ]
        }
    }


class TestSpecificationBase(BaseModel):
    """
    Base schema for Test Specification entities with common fields and validation.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid"
    }

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the test specification",
        examples=["UDS Authentication Test", "CAN Communication Test", "DTC Reading Test"]
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of the test specification",
        examples=["This test specification verifies the UDS authentication functionality of the ECU including level 1 and level 2 authentication procedures."]
    )
    precondition: Optional[str] = Field(
        None,
        description="Precondition for executing the test specification",
        examples=["ECU is powered on", "Diagnostic session is established", "Authentication level 0 is active"]
    )
    postcondition: Optional[str] = Field(
        None,
        description="Postcondition after executing the test specification",
        examples=["Authentication level 2 is established", "All DTCs are cleared", "ECU is in normal operation mode"]
    )
    test_data_description: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Description of test data and parameter variants used",
        examples=[{"Authentication": ["Level1", "Level2"], "DTC_Type": ["All", "Active", "Stored"]}]
    )
    functional_area: FunctionalArea = Field(
        ...,
        description="Functional area this test specification belongs to",
        examples=["UDS", "Communication", "ErrorHandler", "CyberSecurity"]
    )
    requirement_ids: List[UUID] = Field(
        default_factory=list,
        description="List of requirement IDs this test specification addresses",
        examples=[["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate test specification name."""
        if not v or not v.strip():
            raise ValueError('Test specification name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate test specification description."""
        if not v or not v.strip():
            raise ValueError('Test specification description cannot be empty or only whitespace')
        return v.strip()

    @field_validator('precondition')
    @classmethod
    def validate_precondition(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification precondition."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('postcondition')
    @classmethod
    def validate_postcondition(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification postcondition."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('test_data_description')
    @classmethod
    def validate_test_data_description(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate test data description."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('Test data description must be a dictionary')
        return v

    @field_validator('requirement_ids')
    @classmethod
    def validate_requirement_ids(cls, v: List[UUID]) -> List[UUID]:
        """Validate requirement IDs list."""
        if not isinstance(v, list):
            raise ValueError('Requirement IDs must be a list')
        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for req_id in v:
            if req_id not in seen:
                seen.add(req_id)
                unique_ids.append(req_id)
        return unique_ids


class TestSpecificationCreate(TestSpecificationBase, BaseCreateSchema):
    """
    Schema for creating new test specifications.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "UDS Authentication Test",
                    "description": "This test specification verifies the UDS authentication functionality of the ECU including level 1 and level 2 authentication procedures.",
                    "precondition": "ECU is powered on and diagnostic session is established",
                    "postcondition": "Authentication level 2 is established",
                    "test_data_description": {"Authentication": ["Level1", "Level2"]},
                    "functional_area": "UDS",
                    "requirement_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                    "created_by": "admin"
                }
            ]
        }
    }


class TestSpecificationUpdate(BaseUpdateSchema):
    """
    Schema for updating existing test specifications.
    All fields are optional to allow partial updates.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Updated UDS Authentication Test",
                    "description": "Updated description of the test specification",
                    "precondition": "Updated precondition",
                    "postcondition": "Updated postcondition",
                    "test_data_description": {"Authentication": ["Level1", "Level2", "Level3"]},
                    "functional_area": "UDS",
                    "requirement_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the test specification",
        examples=["UDS Authentication Test", "CAN Communication Test", "DTC Reading Test"]
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        description="Detailed description of the test specification",
        examples=["This test specification verifies the UDS authentication functionality of the ECU including level 1 and level 2 authentication procedures."]
    )
    precondition: Optional[str] = Field(
        None,
        description="Precondition for executing the test specification",
        examples=["ECU is powered on", "Diagnostic session is established", "Authentication level 0 is active"]
    )
    postcondition: Optional[str] = Field(
        None,
        description="Postcondition after executing the test specification",
        examples=["Authentication level 2 is established", "All DTCs are cleared", "ECU is in normal operation mode"]
    )
    test_data_description: Optional[Dict[str, Any]] = Field(
        None,
        description="Description of test data and parameter variants used",
        examples=[{"Authentication": ["Level1", "Level2"], "DTC_Type": ["All", "Active", "Stored"]}]
    )
    functional_area: Optional[FunctionalArea] = Field(
        None,
        description="Functional area this test specification belongs to",
        examples=["UDS", "Communication", "ErrorHandler", "CyberSecurity"]
    )
    requirement_ids: Optional[List[UUID]] = Field(
        None,
        description="List of requirement IDs this test specification addresses",
        examples=[["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Test specification name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification description."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Test specification description cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('precondition')
    @classmethod
    def validate_precondition(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification precondition."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('postcondition')
    @classmethod
    def validate_postcondition(cls, v: Optional[str]) -> Optional[str]:
        """Validate test specification postcondition."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('test_data_description')
    @classmethod
    def validate_test_data_description(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate test data description."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Test data description must be a dictionary')
        return v

    @field_validator('requirement_ids')
    @classmethod
    def validate_requirement_ids(cls, v: Optional[List[UUID]]) -> Optional[List[UUID]]:
        """Validate requirement IDs list."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('Requirement IDs must be a list')
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for req_id in v:
                if req_id not in seen:
                    seen.add(req_id)
                    unique_ids.append(req_id)
            return unique_ids
        return v


class TestSpecificationResponse(TestSpecificationBase, BaseResponseSchema):
    """
    Schema for test specification API responses.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": False,  # Responses are read-only
        "str_strip_whitespace": False,  # Don't modify response data
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "UDS Authentication Test",
                    "description": "This test specification verifies the UDS authentication functionality of the ECU including level 1 and level 2 authentication procedures.",
                    "precondition": "ECU is powered on and diagnostic session is established",
                    "postcondition": "Authentication level 2 is established",
                    "test_data_description": {"Authentication": ["Level1", "Level2"]},
                    "functional_area": "UDS",
                    "requirement_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "requirements_count": 1,
                    "test_steps_count": 5
                }
            ]
        }
    }

    # Add computed fields for response
    requirements_count: Optional[int] = Field(
        None,
        description="Number of requirements associated with this test specification",
        examples=[0, 1, 5, 10]
    )
    test_steps_count: Optional[int] = Field(
        None,
        description="Number of test steps in this test specification",
        examples=[0, 1, 5, 20]
    )
    test_steps: Optional[List[TestStepResponse]] = Field(
        None,
        description="List of test steps (included when requested)"
    )


class TestSpecificationListResponse(BaseModel):
    """
    Schema for test specification list responses with pagination.
    """

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

    items: List[TestSpecificationResponse] = Field(
        ...,
        description="List of test specifications"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of test specifications",
        examples=[0, 1, 100, 1000]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1, 2, 3]
    )
    per_page: int = Field(
        ...,
        ge=1,
        le=1000,
        description="Number of items per page",
        examples=[10, 25, 50, 100]
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
        examples=[0, 1, 10, 100]
    )
