"""
Custom exception classes for the Hospital Management System API.

This module defines application-specific exceptions to replace generic HTTPException
usage across the codebase, enabling consistent error handling and better logging.
"""

from fastapi import status
from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to JSON-serializable dictionary."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class DuplicateResourceError(BaseAPIException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource_type: str, field: str, value: Any):
        message = f"{resource_type} with {field} '{value}' already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_RESOURCE",
            details={"resource_type": resource_type, "field": field, "value": value},
        )


class ValidationError(BaseAPIException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors or {}},
        )


class InvalidOperationError(BaseAPIException):
    """Raised when attempting an invalid operation."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_OPERATION",
        )


class UnauthorizedError(BaseAPIException):
    """Raised when authentication is required but not provided."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(BaseAPIException):
    """Raised when user lacks permission for the operation."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class DatabaseError(BaseAPIException):
    """Raised when a database operation fails."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details,
        )

# Alias for backward compatibility and convenience
APIException = BaseAPIException