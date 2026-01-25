"""
Pydantic schemas for authentication operations.

Used for request/response validation in auth endpoints.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Schema for user registration request."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name",
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters, must include letter and number)",
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default='bearer', description="Token type")
    user: dict = Field(..., description="User information")


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str = Field(default='Successfully logged out', description="Logout message")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")


# Export schemas
__all__ = ['SignupRequest', 'LoginRequest', 'AuthResponse', 'LogoutResponse', 'ErrorResponse']
