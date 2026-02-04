"""
Reminder Schemas - Phase 5
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder"""
    task_id: str = Field(..., description="ID of the task to create reminder for")
    trigger_type: str = Field(
        ...,
        description="When to trigger the reminder",
        regex="^(at_due_time|before_15_min|before_30_min|before_1_hour|before_1_day|custom)$"
    )
    custom_offset_minutes: Optional[int] = Field(
        None,
        ge=1,
        le=10080,  # Max 1 week
        description="Custom offset in minutes (required if trigger_type is 'custom')"
    )
    delivery_method: str = Field(
        "email",
        regex="^(email|push|sms)$",
        description="How to deliver the reminder"
    )
    destination: str = Field(..., description="Destination address (email, phone, etc.)")
    custom_message: Optional[str] = Field(None, max_length=500, description="Custom message for the reminder")

    @validator('custom_offset_minutes')
    def validate_custom_offset(cls, v, values):
        """Ensure custom_offset is provided when trigger_type is 'custom'"""
        if values.get('trigger_type') == 'custom' and v is None:
            raise ValueError('custom_offset_minutes is required when trigger_type is "custom"')
        return v

    @validator('destination')
    def validate_destination(cls, v, values):
        """Validate destination based on delivery method"""
        method = values.get('delivery_method', 'email')
        if method == 'email':
            # Basic email validation (pydantic EmailStr would be better but requires email-validator package)
            if '@' not in v or '.' not in v.split('@')[1]:
                raise ValueError('Invalid email address')
        elif method == 'sms':
            # Basic phone validation (digits only, optional + prefix)
            if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
                raise ValueError('Invalid phone number')
        return v


class ReminderResponse(BaseModel):
    """Schema for reminder response"""
    id: str
    task_id: str
    trigger_type: str
    custom_offset_minutes: Optional[int]
    trigger_at: datetime
    status: str
    delivery_method: str
    destination: str
    custom_message: Optional[str]
    delivery_attempts: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder (limited fields)"""
    custom_message: Optional[str] = Field(None, max_length=500)
    destination: Optional[str] = None


class ReminderEvent(BaseModel):
    """Schema for reminder events published to Kafka"""
    reminder_id: str
    task_id: str
    user_id: str
    trigger_at: str
    delivery_method: str
    destination: str
    custom_message: Optional[str] = None

    # Task context (for email rendering)
    task_title: str
    task_description: Optional[str] = None
    task_due_date: str
    task_priority: Optional[str] = None

    class Config:
        from_attributes = True
