"""
AIRequest model for tracking AI feature usage.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, ForeignKey, SQLModel, Text
from sqlalchemy import text, Index


class AIRequestType(str, Enum):
    """Types of AI requests."""

    GENERATE_TODO = 'generate_todo'
    SUMMARIZE = 'summarize'
    PRIORITIZE = 'prioritize'


class AIRequest(SQLModel, table=True):
    """
    AIRequest model for tracking AI feature usage.

    Attributes:
        id: Unique request identifier (UUID)
        user_id: User who made the request (foreign key)
        request_type: Type of AI request
        input_data: Input data sent to AI
        output_data: Output data from AI
        model_used: AI model used for processing
        tokens_used: Optional number of tokens used
        processing_time_ms: Processing time in milliseconds
        created_at: Request timestamp
    """

    __tablename__ = 'ai_requests'

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description='Unique request identifier',
    )
    user_id: UUID = Field(
        default=None,
        foreign_key='users.id',
        nullable=False,
        index=True,
        description='User who made the request',
    )
    request_type: AIRequestType = Field(
        description='Type of AI request',
    )
    input_data: str = Field(
        sa_column=Column(Text),
        description='Input data sent to AI',
    )
    output_data: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description='Output data from AI',
    )
    model_used: str = Field(
        max_length=100,
        description='AI model used',
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description='Number of tokens used',
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        description='Processing time in milliseconds',
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=text('CURRENT_TIMESTAMP')),
        description='Request timestamp',
    )

    # Define indexes
    __table_args__ = (
        Index('idx_ai_requests_user_type', 'user_id', 'request_type'),
        Index('idx_ai_requests_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f'<AIRequest {self.request_type}>'


# Export for use in other modules
__all__ = ['AIRequest', 'AIRequestType']
