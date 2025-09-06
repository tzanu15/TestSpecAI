"""
Pydantic schemas for Category entities.

This module provides validation schemas for Categories including
create, update, and response schemas with appropriate validation rules.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from .base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from .validators import ValidationRules


class CategoryBase(BaseModel):
    """
    Base schema for Category entities with common fields and validation.
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
        description="Name of the category",
        examples=["UDS Requirements", "Communication Requirements", "Security Requirements"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the category",
        examples=["Requirements related to Unified Diagnostic Services", "Communication protocol requirements"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate category name."""
        return ValidationRules.validate_name_format(v, "Category name")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description."""
        if v is not None:
            return ValidationRules.validate_description_length(v, "Category description")
        return v


class RequirementCategoryCreate(CategoryBase, BaseCreateSchema):
    """
    Schema for creating new requirement categories.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "UDS Requirements",
                    "description": "Requirements related to Unified Diagnostic Services",
                    "created_by": "admin"
                }
            ]
        }
    }


class RequirementCategoryUpdate(BaseUpdateSchema):
    """
    Schema for updating existing requirement categories.
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
                    "name": "Updated UDS Requirements",
                    "description": "Updated description for UDS requirements"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the category",
        examples=["UDS Requirements", "Communication Requirements", "Security Requirements"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the category",
        examples=["Requirements related to Unified Diagnostic Services", "Communication protocol requirements"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Category name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description."""
        if v is not None:
            return ValidationRules.validate_description_length(v, "Category description")
        return v


class RequirementCategoryResponse(CategoryBase, BaseResponseSchema):
    """
    Schema for requirement category API responses.
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
                    "name": "UDS Requirements",
                    "description": "Requirements related to Unified Diagnostic Services",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "requirements_count": 5
                }
            ]
        }
    }

    # Add computed fields for response
    requirements_count: Optional[int] = Field(
        None,
        description="Number of requirements in this category",
        examples=[0, 1, 5, 10]
    )


class ParameterCategoryCreate(CategoryBase, BaseCreateSchema):
    """
    Schema for creating new parameter categories.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Authentication Parameters",
                    "description": "Parameters related to authentication levels",
                    "created_by": "admin"
                }
            ]
        }
    }


class ParameterCategoryUpdate(BaseUpdateSchema):
    """
    Schema for updating existing parameter categories.
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
                    "name": "Updated Authentication Parameters",
                    "description": "Updated description for authentication parameters"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the category",
        examples=["Authentication Parameters", "Engine Parameters", "UDS_DID"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the category",
        examples=["Parameters related to authentication levels", "Engine control parameters"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Category name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description."""
        if v is not None:
            return ValidationRules.validate_description_length(v, "Category description")
        return v


class ParameterCategoryResponse(CategoryBase, BaseResponseSchema):
    """
    Schema for parameter category API responses.
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
                    "name": "Authentication Parameters",
                    "description": "Parameters related to authentication levels",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "parameters_count": 3
                }
            ]
        }
    }

    # Add computed fields for response
    parameters_count: Optional[int] = Field(
        None,
        description="Number of parameters in this category",
        examples=[0, 1, 5, 10]
    )


class CommandCategoryCreate(CategoryBase, BaseCreateSchema):
    """
    Schema for creating new command categories.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "UDS Commands",
                    "description": "Generic commands for UDS operations",
                    "created_by": "admin"
                }
            ]
        }
    }


class CommandCategoryUpdate(BaseUpdateSchema):
    """
    Schema for updating existing command categories.
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
                    "name": "Updated UDS Commands",
                    "description": "Updated description for UDS commands"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the category",
        examples=["UDS Commands", "CAN Commands", "FlexRay Commands", "Error Handling"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the category",
        examples=["Generic commands for UDS operations", "CAN bus communication commands"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Category name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate category description."""
        if v is not None:
            return ValidationRules.validate_description_length(v, "Category description")
        return v


class CommandCategoryResponse(CategoryBase, BaseResponseSchema):
    """
    Schema for command category API responses.
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
                    "name": "UDS Commands",
                    "description": "Generic commands for UDS operations",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "commands_count": 8
                }
            ]
        }
    }

    # Add computed fields for response
    commands_count: Optional[int] = Field(
        None,
        description="Number of commands in this category",
        examples=[0, 1, 5, 10]
    )
