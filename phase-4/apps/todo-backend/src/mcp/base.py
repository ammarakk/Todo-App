# Implements: T013
# Phase III - AI-Powered Todo Chatbot
# MCP Tool Base Classes and Error Handling

from typing import Dict, Any, Optional
from enum import Enum


class MCPErrorCode(str, Enum):
    """Standard MCP error codes"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class MCPError(Exception):
    """
    Base exception for MCP tool errors.

    Attributes:
        code: Machine-readable error code
        message: Human-readable error message (bilingual if possible)
    """
    def __init__(self, code: MCPErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class ValidationError(MCPError):
    """Raised when input parameters fail validation"""
    def __init__(self, message: str):
        super().__init__(MCPErrorCode.VALIDATION_ERROR, message)


class NotFoundError(MCPError):
    """Raised when requested resource is not found"""
    def __init__(self, message: str):
        super().__init__(MCPErrorCode.NOT_FOUND, message)


class PermissionDeniedError(MCPError):
    """Raised when user lacks permission for an operation"""
    def __init__(self, message: str):
        super().__init__(MCPErrorCode.PERMISSION_DENIED, message)


def mcp_error_response(code: MCPErrorCode, message: str) -> Dict[str, Any]:
    """
    Format an error response for MCP tool execution.

    Args:
        code: Error code
        message: Error message

    Returns:
        JSON-serializable error response
    """
    return {
        "error": message,
        "code": code.value
    }


def mcp_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a success response for MCP tool execution.

    Args:
        data: Response data

    Returns:
        JSON-serializable success response
    """
    return data
