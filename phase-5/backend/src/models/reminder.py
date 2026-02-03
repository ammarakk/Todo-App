"""
Reminder Model
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Reminder(BaseModel):
    """Task reminder"""
    __tablename__ = "reminders"

    task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    trigger_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True
    )
    delivery_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="email"
    )
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "delivery_method IN ('email', 'push', 'sms')",
            name="check_delivery_method"
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'cancelled')",
            name="check_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, task_id={self.task_id}, status={self.status})>"
