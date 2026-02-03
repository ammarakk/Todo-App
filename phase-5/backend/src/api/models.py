"""
Pydantic Models for API Requests/Responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Request Models
class TaskCreateRequest(BaseModel):
    """Request model for creating a task"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    tags: List[str] = Field(default_factory=list)


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|deleted)$")


class ChatCommandRequest(BaseModel):
    """Request model for chat command"""
    user_input: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None


# Response Models
class TaskResponse(BaseModel):
    """Response model for a task"""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: str
    tags: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatCommandResponse(BaseModel):
    """Response model for chat command"""
    response: str
    intent_detected: str
    skill_agent_used: str
    confidence_score: float
    requires_clarification: bool
    task_created: Optional[TaskResponse] = None
    data: Optional[dict] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    timestamp: datetime
    components: dict
