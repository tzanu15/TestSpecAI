"""
Custom exceptions for TestSpecAI application.
"""
from typing import Any, Dict, Optional


class TestSpecAIException(Exception):
    """Base exception for TestSpecAI application."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(TestSpecAIException):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        super().__init__(message, details)


class NotFoundError(TestSpecAIException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message)


class ConflictError(TestSpecAIException):
    """Raised when there's a conflict with existing data."""

    def __init__(self, message: str, conflicting_field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.conflicting_field = conflicting_field
        super().__init__(message, details)


class AuthenticationError(TestSpecAIException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(TestSpecAIException):
    """Raised when authorization fails."""
    pass


class DatabaseError(TestSpecAIException):
    """Raised when database operations fail."""
    pass


class ExternalServiceError(TestSpecAIException):
    """Raised when external service calls fail."""

    def __init__(self, message: str, service_name: Optional[str] = None, status_code: Optional[int] = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message)


class ConfigurationError(TestSpecAIException):
    """Raised when configuration is invalid or missing."""
    pass


class ProcessingError(TestSpecAIException):
    """Raised when data processing fails."""

    def __init__(self, message: str, processing_stage: Optional[str] = None):
        self.processing_stage = processing_stage
        super().__init__(message)
