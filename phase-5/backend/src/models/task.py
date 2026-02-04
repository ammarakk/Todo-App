"""
Task Model
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ARRAY, Text, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Task(BaseModel):
    """Task with AI-enhanced features"""
    __tablename__ = "tasks"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        server_default="medium"
    )
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list, server_default="{}")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        index=True
    )
    reminder_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    recurrence_rule: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    reminder: Mapped[Optional["Reminder"]] = relationship("Reminder", back_populates="task", uselist=False)

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "tags": self.tags or [],
            "status": self.status,
            "reminder_config": self.reminder_config,
            "recurrence_rule": self.recurrence_rule,
            "ai_metadata": self.ai_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name="check_priority"
        ),
        CheckConstraint(
            "status IN ('active', 'completed', 'deleted')",
            name="check_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
