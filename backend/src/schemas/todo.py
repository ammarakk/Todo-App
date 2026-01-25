"""
Todo schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class TodoCreateRequest(BaseModel):
    """Request schema for creating a todo."""

    title: str = Field(..., min_length=1, max_length=500, description="Todo title")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$", description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Due date")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class TodoUpdateRequest(BaseModel):
    """Request schema for updating a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Todo title")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$", description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Due date")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class TodoResponse(BaseModel):
    """Response schema for a todo."""

    id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    tags: Optional[List[str]]
    due_date: Optional[str]
    created_at: str
    updated_at: str


class TodoListResponse(BaseModel):
    """Response schema for todo list with pagination."""

    todos: List[TodoResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


__all__ = [
    "TodoCreateRequest",
    "TodoUpdateRequest",
    "TodoResponse",
    "TodoListResponse",
]
