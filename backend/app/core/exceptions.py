"""Custom exception classes for dk_travel API."""
from typing import Optional, Dict, Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class ValidationError(AppException):
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
        )


class ConflictError(AppException):
    def __init__(self, message: str, resource: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details={"resource": resource} if resource else {},
        )


class RateLimitError(AppException):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            error_code="RATE_LIMITED",
            details={"retry_after_seconds": retry_after},
        )


class PaymentError(AppException):
    def __init__(self, message: str, payment_id: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=402,
            error_code="PAYMENT_ERROR",
            details={"payment_id": payment_id} if payment_id else {},
        )


class ExternalServiceError(AppException):
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service error ({service}): {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
        )
