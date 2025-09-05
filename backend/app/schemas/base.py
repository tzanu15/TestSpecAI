"""
Base Pydantic schemas for TestSpecAI application.

This module provides foundational schema classes that implement common validation
patterns and configurations to be inherited by all entity schemas.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID
from .validators import ValidationRules


class BaseSchema(BaseModel):
    """
    Base schema class with common attributes and methods for all entities.

    Provides common fields like id, timestamps, created_by, and is_active
    that are shared across all entities in the system.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="forbid"
    )

    id: UUID = Field(
        ...,
        description="Unique identifier for the entity",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000",
            "format": "uuid"
        }
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the entity was created",
        examples=["2023-01-01T00:00:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the entity was last updated",
        examples=["2023-01-01T00:00:00Z"]
    )
    created_by: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User who created the entity",
        examples=["admin", "user@example.com"]
    )
    is_active: bool = Field(
        default=True,
        description="Whether the entity is active or soft-deleted",
        examples=[True, False]
    )

    @field_validator('created_by')
    @classmethod
    def validate_created_by(cls, v: str) -> str:
        """Validate created_by field format."""
        if not v or not v.strip():
            raise ValueError('created_by cannot be empty or only whitespace')
        return v.strip()


class BaseCreateSchema(BaseModel):
    """
    Base schema for creating new entities.

    Excludes system-managed fields like id, timestamps, and created_by
    which are automatically set by the system.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="forbid"
    )

    created_by: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User who is creating the entity",
        examples=["admin", "user@example.com"]
    )

    @field_validator('created_by')
    @classmethod
    def validate_created_by(cls, v: str) -> str:
        """Validate created_by field format."""
        if not v or not v.strip():
            raise ValueError('created_by cannot be empty or only whitespace')
        return v.strip()


class BaseUpdateSchema(BaseModel):
    """
    Base schema for updating existing entities.

    All fields are optional to allow partial updates.
    Excludes system-managed fields that should not be updated.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        extra="forbid"
    )


class BaseResponseSchema(BaseSchema):
    """
    Base schema for API responses.

    Inherits all fields from BaseSchema and adds response-specific
    configuration for API serialization.
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        validate_assignment=False,  # Responses are read-only
        str_strip_whitespace=False,  # Don't modify response data
        extra="forbid"
    )


class PaginationSchema(BaseModel):
    """
    Schema for pagination metadata in list responses.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-based)",
        examples=[1, 2, 3]
    )
    per_page: int = Field(
        ...,
        ge=1,
        le=1000,
        description="Number of items per page",
        examples=[10, 25, 50, 100]
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items across all pages",
        examples=[0, 1, 100, 1000]
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
        examples=[0, 1, 10, 100]
    )


class PaginatedResponseSchema(BaseModel):
    """
    Base schema for paginated API responses.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    items: list = Field(
        ...,
        description="List of items for the current page"
    )
    pagination: PaginationSchema = Field(
        ...,
        description="Pagination metadata"
    )


class ErrorResponseSchema(BaseModel):
    """
    Schema for error responses.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    detail: str = Field(
        ...,
        description="Error message describing what went wrong",
        examples=["Resource not found", "Validation error occurred"]
    )
    type: str = Field(
        ...,
        description="Error type for programmatic handling",
        examples=["NotFoundError", "ValidationError", "ConflictError"]
    )
    field: Optional[str] = Field(
        None,
        description="Field name that caused the error (for validation errors)",
        examples=["title", "email", "password"]
    )


class SuccessResponseSchema(BaseModel):
    """
    Schema for success responses with optional data.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

    message: str = Field(
        ...,
        description="Success message",
        examples=["Operation completed successfully", "Resource created"]
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional response data"
    )
