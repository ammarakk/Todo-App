"""
Todo model for task management.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import Field as PydanticField
from sqlmodel import Column, DateTime, Field, ForeignKey, SQLModel, Text
from sqlalchemy import text, Index, ARRAY, String


class Priority(str, Enum):
    """Todo priority levels."""

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Status(str, Enum):
    """Todo status values."""

    PENDING = 'pending'
    COMPLETED = 'completed'


class Todo(SQLModel, table=True):
    """
    Todo model representing user tasks.

    Attributes:
        id: Unique todo identifier (UUID)
        title: Todo title
        description: Optional detailed description
        status: Current status (pending, in_progress, completed, cancelled)
        priority: Priority level (low, medium, high)
        due_date: Optional due date
        completed_at: Optional completion timestamp
        user_id: Owner user ID (foreign key)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = 'todos'

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description='Unique todo identifier',
    )
    title: str = Field(max_length=255, description='Todo title')
    description: Optional[str] = Field(
        default=None, sa_column=Column(Text), description='Detailed description'
    )
    status: Status = Field(
        default=Status.PENDING,
        description='Current status',
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description='Priority level',
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description='Due date',
    )
    tags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(String)),  # PostgreSQL array type
        description='Tags for categorization',
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description='Completion timestamp',
    )
    user_id: UUID = Field(
        default=None,
        foreign_key='users.id',
        nullable=False,
        index=True,
        description='Owner user ID',
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(), server_default=text('CURRENT_TIMESTAMP')),
        description='Creation timestamp',
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

    # Define indexes
    __table_args__ = (
        Index('idx_todos_user_status', 'user_id', 'status'),
        Index('idx_todos_user_priority', 'user_id', 'priority'),
        Index('idx_todos_due_date', 'due_date'),
    )

    def __repr__(self) -> str:
        return f'<Todo {self.title}>'

    def mark_completed(self) -> None:
        """Mark todo as completed."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        """Check if todo is overdue."""
        if self.due_date is None or self.status == Status.COMPLETED:
            return False
        return datetime.utcnow() > self.due_date


# Export for use in other modules
__all__ = ['Todo', 'Priority', 'Status']
