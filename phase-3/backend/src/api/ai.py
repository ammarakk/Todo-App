"""
AI API routes.

Provides endpoints for AI-powered todo features.
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from src.api.deps import get_current_user_id, get_db
from src.services.ai_service import ai_service
from sqlmodel import Session, select
from src.models.todo import Todo
from uuid import UUID


class AIGenerateRequest(BaseModel):
    """Request schema for AI todo generation."""

    goal: str


class AIGenerateResponse(BaseModel):
    """Response schema for AI todo generation."""

    todos: List[dict]
    message: str


class AISummarizeResponse(BaseModel):
    """Response schema for AI todo summarization."""

    summary: str
    breakdown: dict
    urgent_todos: List[str]


class AIPrioritizeResponse(BaseModel):
    """Response schema for AI todo prioritization."""

    prioritized_todos: List[dict]
    message: str


router = APIRouter()


@router.post(
    '/generate-todo',
    response_model=AIGenerateResponse,
    summary='Generate todos with AI',
    description='Generate todo suggestions from a goal using AI',
)
async def generate_todos(
    request: AIGenerateRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """Generate todos from a goal using AI."""
    try:
        result = ai_service.generate_todos(request.goal)
        return AIGenerateResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post(
    '/summarize',
    response_model=AISummarizeResponse,
    summary='Summarize todos with AI',
    description='Get an AI-powered summary of todos',
)
async def summarize_todos(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Summarize todos using AI."""
    try:
        # Get user's todos
        query = select(Todo).where(Todo.user_id == UUID(current_user_id))
        todos = db.exec(query).all()

        # Convert to dict format
        todos_dict = [
            {
                "title": t.title,
                "description": t.description,
                "priority": t.priority.value,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in todos
        ]

        result = ai_service.summarize_todos(todos_dict)
        return AISummarizeResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.post(
    '/prioritize',
    response_model=AIPrioritizeResponse,
    summary='Prioritize todos with AI',
    description='Get AI-powered todo prioritization',
)
async def prioritize_todos(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Prioritize todos using AI."""
    try:
        # Get user's todos
        query = select(Todo).where(Todo.user_id == UUID(current_user_id))
        todos = db.exec(query).all()

        # Convert to dict format with IDs
        todos_dict = [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "priority": t.priority.value,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in todos
        ]

        result = ai_service.prioritize_todos(todos_dict)
        return AIPrioritizeResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


__all__ = ['router']
