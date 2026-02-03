"""
Session model for JWT token management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, ForeignKey, SQLModel, Text
from sqlalchemy import text, Index


class Session(SQLModel, table=True):
    """
    Session model for tracking active JWT tokens.

    Attributes:
        id: Unique session identifier (UUID)
        user_id: Associated user ID (foreign key)
        token: JWT token (hashed or partial)
        expires_at: Token expiration timestamp
        created_at: Session creation timestamp
        revoked_at: Optional revocation timestamp
        user_agent: Optional user agent string
        ip_address: Optional IP address
    """

    __tablename__ = 'sessions'

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description='Unique session identifier',
    )
    user_id: UUID = Field(
        default=None,
        foreign_key='users.id',
        nullable=False,
        index=True,
        description='Associated user ID',
    )
    token: str = Field(
        max_length=500,
        index=True,
        description='JWT token identifier',
    )
    expires_at: datetime = Field(
        description='Token expiration timestamp',
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=text('CURRENT_TIMESTAMP')),
        description='Session creation timestamp',
    )
    revoked_at: Optional[datetime] = Field(
        default=None,
        description='Revocation timestamp',
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description='User agent string',
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        description='IP address (IPv4 or IPv6)',
    )

    # Define indexes
    __table_args__ = (
        Index('idx_sessions_user_expires', 'user_id', 'expires_at'),
        Index('idx_sessions_token', 'token'),
    )

    def __repr__(self) -> str:
        return f'<Session {self.id}>'

    def is_valid(self) -> bool:
        """Check if session is valid (not expired and not revoked)."""
        if self.revoked_at is not None:
            return False
        return datetime.utcnow() < self.expires_at

    def revoke(self) -> None:
        """Revoke the session."""
        self.revoked_at = datetime.utcnow()


# Export for use in other modules
__all__ = ['Session']
