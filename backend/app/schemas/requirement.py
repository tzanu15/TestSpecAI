"""
Pydantic schemas for Requirement entities.

This module provides validation schemas for Requirements including
create, update, and response schemas with appropriate validation rules.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from .base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from .validators import ValidationRules, BusinessRuleValidators


class RequirementBase(BaseModel):
    """
    Base schema for Requirement entities with common fields and validation.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "populate_by_name": True
    }

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Title of the requirement",
        examples=["System shall provide diagnostic capabilities", "ECU must handle CAN communication"]
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of the requirement",
        examples=["The system shall provide comprehensive diagnostic capabilities for all ECU modules including DTC reading, clearing, and live data monitoring."]
    )
    category_id: UUID = Field(
        ...,
        description="ID of the requirement category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    source: str = Field(
        default="manual",
        min_length=1,
        max_length=255,
        description="Source of the requirement (manual, document, etc.)",
        examples=["manual", "document", "import", "ai_generated"]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="metadata_json",
        serialization_alias="metadata",
        description="Additional metadata for the requirement",
        examples=[{"priority": "high", "version": "1.0", "reviewer": "john.doe@example.com"}]
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate requirement title."""
        return ValidationRules.validate_name_format(v, "Requirement title")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate requirement description."""
        return ValidationRules.validate_description_length(v, "Requirement description")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate requirement source."""
        if not v or not v.strip():
            raise ValueError('Requirement source cannot be empty or only whitespace')
        return v.strip()

    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate requirement metadata."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class RequirementCreate(RequirementBase, BaseCreateSchema):
    """
    Schema for creating new requirements.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "title": "System shall provide diagnostic capabilities",
                    "description": "The system shall provide comprehensive diagnostic capabilities for all ECU modules including DTC reading, clearing, and live data monitoring.",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "source": "manual",
                    "metadata": {"priority": "high", "version": "1.0"},
                    "created_by": "admin"
                }
            ]
        }
    }


class RequirementUpdate(BaseUpdateSchema):
    """
    Schema for updating existing requirements.
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
                    "title": "Updated requirement title",
                    "description": "Updated requirement description",
                    "category_id": "550e8400-e29b-41d4-a716-446655440001",
                    "source": "document",
                    "metadata": {"priority": "medium", "version": "1.1"}
                }
            ]
        }
    }

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Title of the requirement",
        examples=["System shall provide diagnostic capabilities", "ECU must handle CAN communication"]
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        description="Detailed description of the requirement",
        examples=["The system shall provide comprehensive diagnostic capabilities for all ECU modules including DTC reading, clearing, and live data monitoring."]
    )
    category_id: Optional[UUID] = Field(
        None,
        description="ID of the requirement category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    source: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Source of the requirement (manual, document, etc.)",
        examples=["manual", "document", "import", "ai_generated"]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata_json",
        serialization_alias="metadata",
        description="Additional metadata for the requirement",
        examples=[{"priority": "high", "version": "1.0", "reviewer": "john.doe@example.com"}]
    )

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate requirement title."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Requirement title cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate requirement description."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Requirement description cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate requirement source."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Requirement source cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate requirement metadata."""
        if v is not None and not isinstance(v, dict):
            raise ValueError('Metadata must be a dictionary')
        return v


class RequirementResponse(RequirementBase, BaseResponseSchema):
    """
    Schema for requirement API responses.
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
                    "title": "System shall provide diagnostic capabilities",
                    "description": "The system shall provide comprehensive diagnostic capabilities for all ECU modules including DTC reading, clearing, and live data monitoring.",
                    "category_id": "550e8400-e29b-41d4-a716-446655440001",
                    "source": "manual",
                    "metadata": {"priority": "high", "version": "1.0"},
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True
                }
            ]
        }
    }

    # Add computed fields for response
    test_specifications_count: Optional[int] = Field(
        None,
        description="Number of test specifications associated with this requirement",
        examples=[0, 1, 5, 10]
    )
    category_name: Optional[str] = Field(
        None,
        description="Name of the requirement category",
        examples=["UDS Requirements", "Communication Requirements", "Security Requirements"]
    )


class RequirementListResponse(BaseModel):
    """
    Schema for requirement list responses with pagination.
    """

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

    items: List[RequirementResponse] = Field(
        ...,
        description="List of requirements"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of requirements",
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
