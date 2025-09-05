"""
Pydantic schemas for Parameter and ParameterCategory entities.

This module provides validation schemas for Parameters, ParameterCategories,
and ParameterVariants including create, update, and response schemas with
appropriate validation rules.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from .base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from .validators import ValidationRules, BusinessRuleValidators


class ParameterCategoryBase(BaseModel):
    """
    Base schema for Parameter Category entities with common fields and validation.
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
        description="Name of the parameter category",
        examples=["Authentication", "Engine Parameters", "UDS_DID", "CAN Signals"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the parameter category",
        examples=["Parameters related to authentication levels", "Engine-specific parameters for different manufacturers"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate parameter category name."""
        if not v or not v.strip():
            raise ValueError('Parameter category name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter category description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class ParameterCategoryCreate(ParameterCategoryBase, BaseCreateSchema):
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
                    "name": "Authentication",
                    "description": "Parameters related to authentication levels and security",
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
                    "name": "Updated Authentication",
                    "description": "Updated description of authentication parameters"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the parameter category",
        examples=["Authentication", "Engine Parameters", "UDS_DID", "CAN Signals"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the parameter category",
        examples=["Parameters related to authentication levels", "Engine-specific parameters for different manufacturers"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Parameter category name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter category description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class ParameterCategoryResponse(ParameterCategoryBase, BaseResponseSchema):
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
                    "name": "Authentication",
                    "description": "Parameters related to authentication levels and security",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "parameters_count": 5
                }
            ]
        }
    }

    # Add computed fields for response
    parameters_count: Optional[int] = Field(
        None,
        description="Number of parameters in this category",
        examples=[0, 1, 5, 20]
    )


class ParameterVariantBase(BaseModel):
    """
    Base schema for Parameter Variant entities with common fields and validation.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid"
    }

    parameter_id: UUID = Field(
        ...,
        description="ID of the parameter this variant belongs to",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    manufacturer: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Manufacturer name for this variant",
        examples=["BMW", "VW", "Audi", "Mercedes", "Ford", "General Motors"]
    )
    value: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Value for this manufacturer variant",
        examples=["Level1", "Level2", "0x01", "0x02", "Active", "Inactive"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of this variant",
        examples=["Level 1 authentication for BMW vehicles", "Active state for VW ECUs"]
    )

    @field_validator('manufacturer')
    @classmethod
    def validate_manufacturer(cls, v: str) -> str:
        """Validate manufacturer name."""
        if not v or not v.strip():
            raise ValueError('Manufacturer name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Validate variant value."""
        if not v or not v.strip():
            raise ValueError('Variant value cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate variant description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class ParameterVariantCreate(ParameterVariantBase, BaseCreateSchema):
    """
    Schema for creating new parameter variants.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "parameter_id": "550e8400-e29b-41d4-a716-446655440000",
                    "manufacturer": "BMW",
                    "value": "Level1",
                    "description": "Level 1 authentication for BMW vehicles",
                    "created_by": "admin"
                }
            ]
        }
    }


class ParameterVariantUpdate(BaseUpdateSchema):
    """
    Schema for updating existing parameter variants.
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
                    "manufacturer": "BMW",
                    "value": "Level2",
                    "description": "Updated description for BMW variant"
                }
            ]
        }
    }

    parameter_id: Optional[UUID] = Field(
        None,
        description="ID of the parameter this variant belongs to",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    manufacturer: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Manufacturer name for this variant",
        examples=["BMW", "VW", "Audi", "Mercedes", "Ford", "General Motors"]
    )
    value: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Value for this manufacturer variant",
        examples=["Level1", "Level2", "0x01", "0x02", "Active", "Inactive"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of this variant",
        examples=["Level 1 authentication for BMW vehicles", "Active state for VW ECUs"]
    )

    @field_validator('manufacturer')
    @classmethod
    def validate_manufacturer(cls, v: Optional[str]) -> Optional[str]:
        """Validate manufacturer name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Manufacturer name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Optional[str]) -> Optional[str]:
        """Validate variant value."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Variant value cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate variant description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class ParameterVariantResponse(ParameterVariantBase, BaseResponseSchema):
    """
    Schema for parameter variant API responses.
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
                    "parameter_id": "550e8400-e29b-41d4-a716-446655440001",
                    "manufacturer": "BMW",
                    "value": "Level1",
                    "description": "Level 1 authentication for BMW vehicles",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True
                }
            ]
        }
    }


class ParameterBase(BaseModel):
    """
    Base schema for Parameter entities with common fields and validation.
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
        description="Name of the parameter",
        examples=["Authentication", "DTC_Type", "Session_Type", "Security_Level"]
    )
    category_id: UUID = Field(
        ...,
        description="ID of the parameter category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    has_variants: bool = Field(
        default=False,
        description="Whether this parameter has manufacturer-specific variants",
        examples=[True, False]
    )
    default_value: Optional[str] = Field(
        None,
        max_length=500,
        description="Default value for parameters without variants",
        examples=["Level1", "0x01", "Active", "All"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the parameter",
        examples=["Authentication level parameter", "Type of diagnostic trouble codes to read"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate parameter name."""
        if not v or not v.strip():
            raise ValueError('Parameter name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('default_value')
    @classmethod
    def validate_default_value(cls, v: Optional[str]) -> Optional[str]:
        """Validate default value."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @model_validator(mode='after')
    def validate_variants_and_default_value(self):
        """Validate that parameters with variants don't have default values and vice versa."""
        if self.has_variants and self.default_value:
            raise ValueError('Parameters with variants should not have default values')
        if not self.has_variants and not self.default_value:
            raise ValueError('Parameters without variants must have a default value')
        return self


class ParameterCreate(ParameterBase, BaseCreateSchema):
    """
    Schema for creating new parameters.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Authentication",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "has_variants": True,
                    "description": "Authentication level parameter for different manufacturers",
                    "created_by": "admin"
                },
                {
                    "name": "Session_Type",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "has_variants": False,
                    "default_value": "DefaultSession",
                    "description": "Type of diagnostic session",
                    "created_by": "admin"
                }
            ]
        }
    }


class ParameterUpdate(BaseUpdateSchema):
    """
    Schema for updating existing parameters.
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
                    "name": "Updated Authentication",
                    "has_variants": True,
                    "description": "Updated description for authentication parameter"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the parameter",
        examples=["Authentication", "DTC_Type", "Session_Type", "Security_Level"]
    )
    category_id: Optional[UUID] = Field(
        None,
        description="ID of the parameter category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    has_variants: Optional[bool] = Field(
        None,
        description="Whether this parameter has manufacturer-specific variants",
        examples=[True, False]
    )
    default_value: Optional[str] = Field(
        None,
        max_length=500,
        description="Default value for parameters without variants",
        examples=["Level1", "0x01", "Active", "All"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the parameter",
        examples=["Authentication level parameter", "Type of diagnostic trouble codes to read"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Parameter name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('default_value')
    @classmethod
    def validate_default_value(cls, v: Optional[str]) -> Optional[str]:
        """Validate default value."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate parameter description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @model_validator(mode='after')
    def validate_variants_and_default_value(self):
        """Validate that parameters with variants don't have default values and vice versa."""
        # Only validate if both fields are provided
        if self.has_variants is not None and self.default_value is not None:
            if self.has_variants and self.default_value:
                raise ValueError('Parameters with variants should not have default values')
            if not self.has_variants and not self.default_value:
                raise ValueError('Parameters without variants must have a default value')
        return self


class ParameterResponse(ParameterBase, BaseResponseSchema):
    """
    Schema for parameter API responses.
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
                    "name": "Authentication",
                    "category_id": "550e8400-e29b-41d4-a716-446655440001",
                    "has_variants": True,
                    "default_value": None,
                    "description": "Authentication level parameter for different manufacturers",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "category_name": "Authentication",
                    "variants_count": 3,
                    "variants": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440002",
                            "manufacturer": "BMW",
                            "value": "Level1",
                            "description": "Level 1 authentication for BMW vehicles"
                        }
                    ]
                }
            ]
        }
    }

    # Add computed fields for response
    category_name: Optional[str] = Field(
        None,
        description="Name of the parameter category",
        examples=["Authentication", "Engine Parameters", "UDS_DID"]
    )
    variants_count: Optional[int] = Field(
        None,
        description="Number of variants for this parameter",
        examples=[0, 1, 3, 5]
    )
    variants: Optional[List[ParameterVariantResponse]] = Field(
        None,
        description="List of parameter variants (included when requested)"
    )


class ParameterListResponse(BaseModel):
    """
    Schema for parameter list responses with pagination.
    """

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

    items: List[ParameterResponse] = Field(
        ...,
        description="List of parameters"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of parameters",
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
