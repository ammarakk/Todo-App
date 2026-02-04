"""
Recurring Task Model - Phase 5
Handles automatically repeating tasks
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, DateTime, Integer, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class RecurrencePattern(str, Enum):
    """Supported recurrence patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RecurringTaskStatus(str, Enum):
    """Status of recurring task configuration"""
    ACTIVE = "active"          # Currently generating new tasks
    PAUSED = "paused"          # Temporarily stopped
    COMPLETED = "completed"    # Reached end date/max occurrences
    CANCELLED = "cancelled"    # User cancelled


class RecurringTask(BaseModel):
    """
    Recurring Task Configuration

    Manages tasks that automatically repeat on a schedule.
    When a task instance is marked complete, the next occurrence
    is automatically generated.
    """
    __tablename__ = "recurring_tasks"

    # Foreign key to the original task template
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    template_task_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Recurrence configuration
    pattern: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="weekly"
    )
    interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1"
    )  # Every N days/weeks/months

    # Schedule constraints
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )  # When to start generating tasks
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )  # When to stop (optional)
    max_occurrences: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # Maximum number of tasks to generate (optional)

    # Tracking
    next_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )  # When the next task should be generated
    occurrences_generated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )  # How many tasks have been created so far
    last_generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )  # When the last task was created

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        index=True
    )

    # Additional configuration
    custom_config: Mapped[Optional[dict]] = mapped_column(
        Text,
        nullable=True
    )  # JSON string for custom patterns (e.g., "every Monday and Wednesday")
    skip_weekends: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=False,
        server_default="false"
    )  # Skip weekends when calculating next date
    generate_ahead: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )  # Generate N tasks ahead of time (0 = only generate when previous completes)

    __table_args__ = (
        CheckConstraint("pattern IN ('daily', 'weekly', 'monthly', 'yearly', 'custom')", name="check_pattern"),
        CheckConstraint("status IN ('active', 'paused', 'completed', 'cancelled')", name="check_status"),
        CheckConstraint("interval > 0", name="check_interval_positive"),
        CheckConstraint("occurrences_generated >= 0", name="check_occurrences_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<RecurringTask(id={self.id}, pattern={self.pattern}, status={self.status}, next_due={self.next_due_date})>"

    def to_dict(self) -> dict:
        """Convert recurring task to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "template_task_id": str(self.template_task_id),
            "pattern": self.pattern,
            "interval": self.interval,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "max_occurrences": self.max_occurrences,
            "next_due_date": self.next_due_date.isoformat() if self.next_due_date else None,
            "occurrences_generated": self.occurrences_generated,
            "last_generated_at": self.last_generated_at.isoformat() if self.last_generated_at else None,
            "status": self.status,
            "custom_config": self.custom_config,
            "skip_weekends": self.skip_weekends,
            "generate_ahead": self.generate_ahead,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def should_stop_generating(self) -> bool:
        """Check if this recurring task should stop generating new occurrences."""
        # Check if max occurrences reached
        if self.max_occurrences and self.occurrences_generated >= self.max_occurrences:
            return True

        # Check if end date passed
        if self.end_date and datetime.utcnow() > self.end_date:
            return True

        # Check if cancelled or completed
        if self.status in [RecurringTaskStatus.CANCELLED, RecurringTaskStatus.COMPLETED]:
            return True

        return False

    def calculate_next_due_date(self, last_task_due_date: datetime) -> Optional[datetime]:
        """
        Calculate the next due date based on pattern and interval.

        Args:
            last_task_due_date: The due date of the most recently completed task

        Returns:
            Next due date or None if should stop
        """
        from datetime import timedelta

        if self.should_stop_generating():
            return None

        if self.pattern == RecurrencePattern.DAILY:
            next_date = last_task_due_date + timedelta(days=self.interval)
        elif self.pattern == RecurrencePattern.WEEKLY:
            next_date = last_task_due_date + timedelta(weeks=self.interval)
        elif self.pattern == RecurrencePattern.MONTHLY:
            # Add months (handle year rollover)
            year = last_task_due_date.year
            month = last_task_due_date.month + self.interval
            while month > 12:
                month -= 12
                year += 1
            next_date = last_task_due_date.replace(year=year, month=month)
        elif self.pattern == RecurrencePattern.YEARLY:
            next_date = last_task_due_date.replace(year=last_task_due_date.year + self.interval)
        else:  # CUSTOM
            # Custom patterns would be parsed from custom_config JSON
            # For now, default to weekly
            next_date = last_task_due_date + timedelta(weeks=self.interval)

        # Skip weekends if configured
        if self.skip_weekends:
            while next_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                next_date += timedelta(days=1)

        # Check if next_date exceeds end_date
        if self.end_date and next_date > self.end_date:
            return None

        return next_date

    def mark_as_completed(self):
        """Mark recurring task as completed (reached end)."""
        self.status = RecurringTaskStatus.COMPLETED

    def pause(self):
        """Pause recurring task generation."""
        self.status = RecurringTaskStatus.PAUSED

    def resume(self):
        """Resume recurring task generation."""
        if self.status == RecurringTaskStatus.PAUSED:
            self.status = RecurringTaskStatus.ACTIVE

    def cancel(self):
        """Cancel recurring task."""
        self.status = RecurringTaskStatus.CANCELLED
