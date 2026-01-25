"""
Todo API routes.

Provides endpoints for todo CRUD operations.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlmodel import Session, select

from src.api.deps import get_current_user_id, get_db
from src.models.todo import Priority, Status, Todo
from src.schemas.todo import TodoCreateRequest, TodoResponse, TodoUpdateRequest

router = APIRouter()


@router.get(
    '/',
    response_model=list[TodoResponse],
    summary='List todos',
    description='Get all todos for the current user with optional filtering',
)
async def list_todos(
    skip: int = Query(0, ge=0, description='Number of todos to skip'),
    limit: int = Query(20, ge=1, le=100, description='Number of todos to return'),
    status_filter: Optional[str] = Query(None, alias='status', description='Filter by status'),
    priority: Optional[str] = Query(None, description='Filter by priority'),
    search: Optional[str] = Query(None, description='Search in title and description'),
    sort_by: str = Query('created_at', description='Sort by field'),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List todos for the current user with filtering and pagination."""
    # Build base query with user isolation
    query = select(Todo).where(Todo.user_id == UUID(current_user_id))

    # Apply filters
    if status_filter:
        query = query.where(Todo.status == Status(status_filter))
    if priority:
        query = query.where(Todo.priority == Priority(priority))
    if search:
        search_pattern = f'%{search}%'
        query = query.where(
            (Todo.title.ilike(search_pattern)) | (Todo.description.ilike(search_pattern))
        )

    # Apply sorting
    if sort_by == 'created_at':
        query = query.order_by(Todo.created_at.desc())
    elif sort_by == 'due_date':
        query = query.order_by(Todo.due_date.asc().nulls_last())
    elif sort_by == 'priority':
        query = query.order_by(Todo.priority.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    todos = db.exec(query).all()

    return [
        TodoResponse(
            id=str(todo.id),
            user_id=str(todo.user_id),
            title=todo.title,
            description=todo.description,
            status=todo.status.value,
            priority=todo.priority.value,
            tags=todo.tags,
            due_date=todo.due_date.isoformat() if todo.due_date else None,
            created_at=todo.created_at.isoformat(),
            updated_at=todo.updated_at.isoformat(),
        )
        for todo in todos
    ]


@router.post(
    '/',
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create todo',
    description='Create a new todo',
)
async def create_todo(
    todo_data: TodoCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new todo for the current user."""
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
        priority=Priority(todo_data.priority) if todo_data.priority else Priority.MEDIUM,
        due_date=todo_data.due_date,
        tags=todo_data.tags,
        user_id=UUID(current_user_id),
        status=Status.PENDING,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        tags=todo.tags,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


# IMPORTANT: More specific routes must come BEFORE parameterized routes
@router.post(
    '/{todo_id}/toggle',
    response_model=TodoResponse,
    summary='Toggle todo completion (POST)',
    description='Toggle todo completion status - POST method for frontend compatibility',
)
async def toggle_todo_post(
    todo_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Toggle todo completion status using POST method."""
    query = select(Todo).where(
        Todo.id == UUID(todo_id),
        Todo.user_id == UUID(current_user_id)
    )
    todo = db.exec(query).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found',
        )

    # Toggle status - flip between completed and pending
    if todo.status == Status.PENDING:
        todo.status = Status.COMPLETED
        if not todo.completed_at:
            todo.completed_at = datetime.utcnow()
    else:
        todo.status = Status.PENDING
        todo.completed_at = None

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        tags=todo.tags,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


@router.patch(
    '/{todo_id}/complete',
    response_model=TodoResponse,
    summary='Toggle todo completion',
    description='Toggle todo completion status',
)
async def toggle_complete(
    todo_id: str,
    completed: bool = True,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Toggle todo completion status."""
    query = select(Todo).where(
        Todo.id == UUID(todo_id),
        Todo.user_id == UUID(current_user_id)
    )
    todo = db.exec(query).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found',
        )

    # Toggle status
    todo.status = Status.COMPLETED if completed else Status.PENDING
    if completed and not todo.completed_at:
        todo.completed_at = datetime.utcnow()
    elif not completed:
        todo.completed_at = None

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        tags=todo.tags,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


@router.get(
    '/{todo_id}',
    response_model=TodoResponse,
    summary='Get todo',
    description='Get a specific todo by ID',
)
async def get_todo(
    todo_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific todo."""
    query = select(Todo).where(
        Todo.id == UUID(todo_id),
        Todo.user_id == UUID(current_user_id)
    )
    todo = db.exec(query).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found',
        )

    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        tags=todo.tags,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


@router.put(
    '/{todo_id}',
    response_model=TodoResponse,
    summary='Update todo',
    description='Update a todo',
)
async def update_todo(
    todo_id: str,
    todo_data: TodoUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update a todo."""
    query = select(Todo).where(
        Todo.id == UUID(todo_id),
        Todo.user_id == UUID(current_user_id)
    )
    todo = db.exec(query).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found',
        )

    # Update fields
    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.priority is not None:
        todo.priority = Priority(todo_data.priority)
    if todo_data.due_date is not None:
        todo.due_date = todo_data.due_date
    if todo_data.tags is not None:
        todo.tags = todo_data.tags

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return TodoResponse(
        id=str(todo.id),
        user_id=str(todo.user_id),
        title=todo.title,
        description=todo.description,
        status=todo.status.value,
        priority=todo.priority.value,
        tags=todo.tags,
        due_date=todo.due_date.isoformat() if todo.due_date else None,
        created_at=todo.created_at.isoformat(),
        updated_at=todo.updated_at.isoformat(),
    )


@router.delete(
    '/{todo_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete todo',
    description='Delete a todo',
)
async def delete_todo(
    todo_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a todo."""
    query = select(Todo).where(
        Todo.id == UUID(todo_id),
        Todo.user_id == UUID(current_user_id)
    )
    todo = db.exec(query).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found',
        )

    db.delete(todo)
    db.commit()
    return None


__all__ = ['router']
