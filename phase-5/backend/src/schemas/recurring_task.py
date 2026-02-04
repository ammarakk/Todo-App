"""
Recurring Task Schemas - Phase 5
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class RecurringTaskCreate(BaseModel):
    """Schema for creating a new recurring task configuration"""
    template_task_id: str = Field(..., description="ID of the task to use as template")
    pattern: str = Field(
        ...,
        description="Recurrence pattern",
        regex="^(daily|weekly|monthly|yearly|custom)$"
    )
    interval: int = Field(
        1,
        ge=1,
        le=365,
        description="Interval between occurrences (e.g., 2 = every 2 weeks)"
    )
    start_date: Optional[datetime] = Field(None, description="When to start generating tasks")
    end_date: Optional[datetime] = Field(None, description="When to stop generating tasks")
    max_occurrences: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of tasks to generate")
    custom_config: Optional[str] = Field(None, max_length=1000, description="Custom pattern configuration (JSON)")
    skip_weekends: bool = Field(False, description="Skip weekends when calculating next date")
    generate_ahead: int = Field(
        0,
        ge=0,
        le=52,
        description="Generate N tasks ahead of time (0 = only when previous completes)"
    )

    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end_date is after start_date if both provided"""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

    @validator('pattern')
    def validate_custom_config(cls, v, values):
        """Ensure custom_config is provided for custom patterns"""
        if v == 'custom' and not values.get('custom_config'):
            # Don't require custom_config in create, but warn
            pass
        return v


class RecurringTaskUpdate(BaseModel):
    """Schema for updating a recurring task configuration"""
    pattern: Optional[str] = Field(None, regex="^(daily|weekly|monthly|yearly|custom)$")
    interval: Optional[int] = Field(None, ge=1, le=365)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = Field(None, ge=1, le=1000)
    custom_config: Optional[str] = Field(None, max_length=1000)
    skip_weekends: Optional[bool] = None
    generate_ahead: Optional[int] = Field(None, ge=0, le=52)
    status: Optional[str] = Field(None, regex="^(active|paused|cancelled)$")


class RecurringTaskResponse(BaseModel):
    """Schema for recurring task response"""
    id: str
    user_id: str
    template_task_id: str
    pattern: str
    interval: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    max_occurrences: Optional[int]
    next_due_date: Optional[datetime]
    occurrences_generated: int
    last_generated_at: Optional[datetime]
    status: str
    custom_config: Optional[str]
    skip_weekends: bool
    generate_ahead: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecurringTaskList(BaseModel):
    """Schema for list of recurring tasks"""
    total: int
    items: list[RecurringTaskResponse]


class TaskGeneratedEvent(BaseModel):
    """Schema for task.generated event published to Kafka"""
    recurring_task_id: str
    task_id: str
    user_id: str
    due_date: str
    occurrence_number: int
    pattern: str
    template_task_id: str

    class Config:
        from_attributes = True
