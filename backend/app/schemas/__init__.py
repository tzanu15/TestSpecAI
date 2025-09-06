"""
Pydantic schemas for TestSpecAI application.

This package contains all Pydantic schemas used for API validation,
request/response serialization, and data validation.
"""

from .base import (
    BaseSchema,
    BaseCreateSchema,
    BaseUpdateSchema,
    BaseResponseSchema,
    PaginationSchema,
    PaginatedResponseSchema,
    ErrorResponseSchema,
    SuccessResponseSchema
)

from .validators import (
    ValidationRules,
    BusinessRuleValidators,
    CrossEntityValidators
)

from .requirement import (
    RequirementBase,
    RequirementCreate,
    RequirementUpdate,
    RequirementResponse,
    RequirementListResponse
)

from .test_spec import (
    FunctionalArea,
    GenericCommandReference,
    TestStepBase,
    TestStepCreate,
    TestStepUpdate,
    TestStepResponse,
    TestSpecificationBase,
    TestSpecificationCreate,
    TestSpecificationUpdate,
    TestSpecificationResponse,
    TestSpecificationListResponse
)

from .parameter import (
    ParameterCategoryBase,
    ParameterCategoryCreate,
    ParameterCategoryUpdate,
    ParameterCategoryResponse,
    ParameterVariantBase,
    ParameterVariantCreate,
    ParameterVariantUpdate,
    ParameterVariantResponse,
    ParameterBase,
    ParameterCreate,
    ParameterUpdate,
    ParameterResponse,
    ParameterListResponse
)

from .command import (
    CommandCategoryBase,
    CommandCategoryCreate,
    CommandCategoryUpdate,
    CommandCategoryResponse,
    GenericCommandBase,
    GenericCommandCreate,
    GenericCommandUpdate,
    GenericCommandResponse,
    GenericCommandListResponse
)

from .category import (
    CategoryBase,
    RequirementCategoryCreate,
    RequirementCategoryUpdate,
    RequirementCategoryResponse,
    ParameterCategoryCreate,
    ParameterCategoryUpdate,
    ParameterCategoryResponse,
    CommandCategoryCreate,
    CommandCategoryUpdate,
    CommandCategoryResponse
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "BaseCreateSchema",
    "BaseUpdateSchema",
    "BaseResponseSchema",
    "PaginationSchema",
    "PaginatedResponseSchema",
    "ErrorResponseSchema",
    "SuccessResponseSchema",

    # Validators
    "ValidationRules",
    "BusinessRuleValidators",
    "CrossEntityValidators",

    # Requirement schemas
    "RequirementBase",
    "RequirementCreate",
    "RequirementUpdate",
    "RequirementResponse",
    "RequirementListResponse",

    # Test specification schemas
    "FunctionalArea",
    "GenericCommandReference",
    "TestStepBase",
    "TestStepCreate",
    "TestStepUpdate",
    "TestStepResponse",
    "TestSpecificationBase",
    "TestSpecificationCreate",
    "TestSpecificationUpdate",
    "TestSpecificationResponse",
    "TestSpecificationListResponse",

    # Parameter schemas
    "ParameterCategoryBase",
    "ParameterCategoryCreate",
    "ParameterCategoryUpdate",
    "ParameterCategoryResponse",
    "ParameterVariantBase",
    "ParameterVariantCreate",
    "ParameterVariantUpdate",
    "ParameterVariantResponse",
    "ParameterBase",
    "ParameterCreate",
    "ParameterUpdate",
    "ParameterResponse",
    "ParameterListResponse",

    # Command schemas
    "CommandCategoryBase",
    "CommandCategoryCreate",
    "CommandCategoryUpdate",
    "CommandCategoryResponse",
    "GenericCommandBase",
    "GenericCommandCreate",
    "GenericCommandUpdate",
    "GenericCommandResponse",
    "GenericCommandListResponse",

    # Category schemas
    "CategoryBase",
    "RequirementCategoryCreate",
    "RequirementCategoryUpdate",
    "RequirementCategoryResponse",
    "ParameterCategoryCreate",
    "ParameterCategoryUpdate",
    "ParameterCategoryResponse",
    "CommandCategoryCreate",
    "CommandCategoryUpdate",
    "CommandCategoryResponse"
]
