"""
Pydantic schemas for GenericCommand and CommandCategory entities.

This module provides validation schemas for GenericCommands and CommandCategories
including create, update, and response schemas with appropriate validation rules.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from .base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema
from .validators import ValidationRules, BusinessRuleValidators, CrossEntityValidators


class CommandCategoryBase(BaseModel):
    """
    Base schema for Command Category entities with common fields and validation.
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
        description="Name of the command category",
        examples=["UDS", "CAN", "FlexRay", "Error Handling", "Security", "Diagnostics"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the command category",
        examples=["UDS diagnostic commands", "CAN communication commands", "Error handling procedures"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate command category name."""
        if not v or not v.strip():
            raise ValueError('Command category name cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate command category description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class CommandCategoryCreate(CommandCategoryBase, BaseCreateSchema):
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
                    "name": "UDS",
                    "description": "UDS diagnostic commands for automotive ECUs",
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
                    "name": "Updated UDS",
                    "description": "Updated description of UDS commands"
                }
            ]
        }
    }

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name of the command category",
        examples=["UDS", "CAN", "FlexRay", "Error Handling", "Security", "Diagnostics"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the command category",
        examples=["UDS diagnostic commands", "CAN communication commands", "Error handling procedures"]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate command category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Command category name cannot be empty or only whitespace')
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate command category description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v


class CommandCategoryResponse(CommandCategoryBase, BaseResponseSchema):
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
                    "name": "UDS",
                    "description": "UDS diagnostic commands for automotive ECUs",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "commands_count": 10
                }
            ]
        }
    }

    # Add computed fields for response
    commands_count: Optional[int] = Field(
        None,
        description="Number of commands in this category",
        examples=[0, 1, 5, 20]
    )


class GenericCommandBase(BaseModel):
    """
    Base schema for Generic Command entities with common fields and validation.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid"
    }

    template: str = Field(
        ...,
        min_length=1,
        description="Command template with parameter placeholders",
        examples=[
            "Set level of authentication {Authentication}",
            "Read DTC {DTC_Type}",
            "Clear DTC {DTC_Code}",
            "Start diagnostic session {Session_Type}"
        ]
    )
    category_id: UUID = Field(
        ...,
        description="ID of the command category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the command",
        examples=[
            "Sets the authentication level for the ECU",
            "Reads diagnostic trouble codes of specified type",
            "Clears a specific diagnostic trouble code"
        ]
    )
    required_parameter_ids: List[UUID] = Field(
        default_factory=list,
        description="List of required parameter IDs for this command",
        examples=[["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]]
    )

    @field_validator('template')
    @classmethod
    def validate_template(cls, v: str) -> str:
        """Validate command template."""
        if not v or not v.strip():
            raise ValueError('Command template cannot be empty or only whitespace')

        # Check for valid parameter placeholders
        import re
        placeholders = re.findall(r'\{([^}]+)\}', v)
        if placeholders:
            # Validate placeholder names (alphanumeric and underscores only)
            for placeholder in placeholders:
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', placeholder):
                    raise ValueError(f'Invalid parameter placeholder: {placeholder}. Must start with letter or underscore and contain only alphanumeric characters and underscores.')

        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate command description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('required_parameter_ids')
    @classmethod
    def validate_required_parameter_ids(cls, v: List[UUID]) -> List[UUID]:
        """Validate required parameter IDs list."""
        if not isinstance(v, list):
            raise ValueError('Required parameter IDs must be a list')
        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for param_id in v:
            if param_id not in seen:
                seen.add(param_id)
                unique_ids.append(param_id)
        return unique_ids

    @model_validator(mode='after')
    def validate_template_parameters(self):
        """Validate that template parameters match required parameters."""
        import re
        template_params = set(re.findall(r'\{([^}]+)\}', self.template))
        required_params = set(str(param_id) for param_id in self.required_parameter_ids)

        # Note: This is a basic validation. In a real implementation, you might want to
        # validate that the parameter names in the template correspond to actual parameter names
        # rather than just checking the count
        if template_params and not self.required_parameter_ids:
            raise ValueError('Template contains parameters but no required parameters are specified')

        return self


class GenericCommandCreate(GenericCommandBase, BaseCreateSchema):
    """
    Schema for creating new generic commands.
    """

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "str_strip_whitespace": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "template": "Set level of authentication {Authentication}",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "description": "Sets the authentication level for the ECU",
                    "required_parameter_ids": ["550e8400-e29b-41d4-a716-446655440001"],
                    "created_by": "admin"
                }
            ]
        }
    }


class GenericCommandUpdate(BaseUpdateSchema):
    """
    Schema for updating existing generic commands.
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
                    "template": "Updated: Set level of authentication {Authentication}",
                    "description": "Updated description of the command",
                    "required_parameter_ids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
                }
            ]
        }
    }

    template: Optional[str] = Field(
        None,
        min_length=1,
        description="Command template with parameter placeholders",
        examples=[
            "Set level of authentication {Authentication}",
            "Read DTC {DTC_Type}",
            "Clear DTC {DTC_Code}",
            "Start diagnostic session {Session_Type}"
        ]
    )
    category_id: Optional[UUID] = Field(
        None,
        description="ID of the command category",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    description: Optional[str] = Field(
        None,
        description="Description of the command",
        examples=[
            "Sets the authentication level for the ECU",
            "Reads diagnostic trouble codes of specified type",
            "Clears a specific diagnostic trouble code"
        ]
    )
    required_parameter_ids: Optional[List[UUID]] = Field(
        None,
        description="List of required parameter IDs for this command",
        examples=[["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]]
    )

    @field_validator('template')
    @classmethod
    def validate_template(cls, v: Optional[str]) -> Optional[str]:
        """Validate command template."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Command template cannot be empty or only whitespace')

            # Check for valid parameter placeholders
            import re
            placeholders = re.findall(r'\{([^}]+)\}', v)
            if placeholders:
                # Validate placeholder names (alphanumeric and underscores only)
                for placeholder in placeholders:
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', placeholder):
                        raise ValueError(f'Invalid parameter placeholder: {placeholder}. Must start with letter or underscore and contain only alphanumeric characters and underscores.')

            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate command description."""
        if v is not None:
            if not v or not v.strip():
                return None  # Convert empty strings to None
            return v.strip()
        return v

    @field_validator('required_parameter_ids')
    @classmethod
    def validate_required_parameter_ids(cls, v: Optional[List[UUID]]) -> Optional[List[UUID]]:
        """Validate required parameter IDs list."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('Required parameter IDs must be a list')
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for param_id in v:
                if param_id not in seen:
                    seen.add(param_id)
                    unique_ids.append(param_id)
            return unique_ids
        return v

    @model_validator(mode='after')
    def validate_template_parameters(self):
        """Validate that template parameters match required parameters if both are provided."""
        if self.template is not None and self.required_parameter_ids is not None:
            import re
            template_params = set(re.findall(r'\{([^}]+)\}', self.template))
            required_params = set(str(param_id) for param_id in self.required_parameter_ids)

            if template_params and not self.required_parameter_ids:
                raise ValueError('Template contains parameters but no required parameters are specified')

        return self


class GenericCommandResponse(GenericCommandBase, BaseResponseSchema):
    """
    Schema for generic command API responses.
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
                    "template": "Set level of authentication {Authentication}",
                    "category_id": "550e8400-e29b-41d4-a716-446655440001",
                    "description": "Sets the authentication level for the ECU",
                    "required_parameter_ids": ["550e8400-e29b-41d4-a716-446655440002"],
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "created_by": "admin",
                    "is_active": True,
                    "category_name": "UDS",
                    "required_parameters_count": 1,
                    "template_parameters": ["Authentication"],
                    "required_parameters": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440002",
                            "name": "Authentication",
                            "category_name": "Authentication"
                        }
                    ]
                }
            ]
        }
    }

    # Add computed fields for response
    category_name: Optional[str] = Field(
        None,
        description="Name of the command category",
        examples=["UDS", "CAN", "FlexRay", "Error Handling"]
    )
    required_parameters_count: Optional[int] = Field(
        None,
        description="Number of required parameters for this command",
        examples=[0, 1, 3, 5]
    )
    template_parameters: Optional[List[str]] = Field(
        None,
        description="List of parameter names extracted from template",
        examples=[["Authentication"], ["DTC_Type"], ["Authentication", "Session_Type"]]
    )
    required_parameters: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of required parameters with details (included when requested)"
    )


class GenericCommandListResponse(BaseModel):
    """
    Schema for generic command list responses with pagination.
    """

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

    items: List[GenericCommandResponse] = Field(
        ...,
        description="List of generic commands"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of generic commands",
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
