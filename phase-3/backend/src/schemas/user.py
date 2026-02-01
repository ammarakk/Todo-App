"""
Pydantic schemas for User model.

Used for request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)",
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserProfileUpdateRequest(BaseModel):
    """Schema for updating user profile (minimal)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")


class UserResponse(UserBase):
    """Schema for user response (excluding sensitive data)."""

    id: UUID = Field(..., description="User ID")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True  # Enable ORM mode


# Export schemas
__all__ = ['UserBase', 'UserCreate', 'UserLogin', 'UserUpdate', 'UserResponse', 'UserProfileUpdateRequest']
