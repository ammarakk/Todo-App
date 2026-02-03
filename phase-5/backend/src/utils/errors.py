"""
Error Handling and Custom Exceptions
"""
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details,
        )


class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class DaprError(AppError):
    """Dapr service error"""
    def __init__(self, message: str = "Dapr service error", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DAPR_ERROR",
            details=details,
        )


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler for FastAPI"""
    from .logging import get_logger
    
    logger = get_logger(__name__)
    
    if isinstance(exc, AppError):
        # Handle known application errors
        logger.warning(
            "application_error",
            error_code=exc.error_code,
            status_code=exc.status_code,
            message=exc.message,
            path=request.url.path,
            details=exc.details,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
    
    elif isinstance(exc, HTTPException):
        # Handle FastAPI HTTP exceptions
        logger.warning(
            "http_exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                }
            },
        )
    
    else:
        # Handle unexpected errors
        logger.error(
            "unexpected_error",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            exc_info=exc,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
