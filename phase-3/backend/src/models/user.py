"""
User model for authentication and profile.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, SQLModel
from sqlalchemy import text


class User(SQLModel, table=True):
    """
    User model representing application users.

    Attributes:
        id: Unique user identifier (UUID)
        name: User's full name
        email: User's email address (unique)
        password_hash: Bcrypt hashed password
        avatar_url: Optional Cloudinary avatar URL
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'users'

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description='Unique user identifier',
    )
    name: str = Field(max_length=255, description="User's full name")
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User's email address",
    )
    password_hash: str = Field(max_length=255, description='Bcrypt hashed password', exclude=True)
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description='Cloudinary avatar URL'
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=text('CURRENT_TIMESTAMP')),
        description='Account creation timestamp',
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(),
            server_default=text('CURRENT_TIMESTAMP'),
            onupdate=text('CURRENT_TIMESTAMP'),
        ),
        description='Last update timestamp',
    )

    def __repr__(self) -> str:
        return f'<User {self.email}>'


# Export for use in other modules
__all__ = ['User']
