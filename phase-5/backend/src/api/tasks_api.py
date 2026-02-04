"""
Tasks API - Phase 5

CRUD operations for tasks with Dapr event publishing.
All state changes are published to Kafka for microservices to consume.
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.models.base import get_db
from src.models.task import Task as TaskModel
from src.orchestrator.event_publisher import EventPublisher
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
event_publisher = EventPublisher()


# Pydantic schemas for request/response
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "medium"
    tags: Optional[List[str]] = []
    reminder_config: Optional[dict] = None
    recurrence_rule: Optional[dict] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    reminder_config: Optional[dict] = None
    recurrence_rule: Optional[dict] = None


class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    due_date: Optional[str]
    priority: str
    tags: List[str]
    status: str
    reminder_config: Optional[dict]
    recurrence_rule: Optional[dict]
    created_at: str
    updated_at: str


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Create a new task and publish task.created event.

    Args:
        task_data: Task creation data
        user_id: User ID from authentication
        db: Database session

    Returns:
        Created task
    """
    try:
        # Create task in database
        task = TaskModel(
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority or "medium",
            tags=task_data.tags or [],
            reminder_config=task_data.reminder_config,
            recurrence_rule=task_data.recurrence_rule,
            user_id=user_id,
            status="active"
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(
            "task_created",
            task_id=str(task.id),
            user_id=user_id,
            title=task.title
        )

        # Publish events via Dapr
        await event_publisher.publish_task_event(
            "task.created",
            str(task.id),
            task.to_dict()
        )

        await event_publisher.publish_task_update(
            str(task.id),
            "created",
            task.to_dict()
        )

        await event_publisher.publish_audit_event(
            "Task",
            str(task.id),
            "CREATE",
            "user",
            user_id,
            new_values=task.to_dict()
        )

        return TaskResponse(**task.to_dict())

    except Exception as e:
        logger.error("create_task_failed", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List tasks for a user with optional filters.

    Args:
        user_id: User ID from authentication
        status: Filter by status (active, completed, deleted)
        priority: Filter by priority (low, medium, high)
        limit: Maximum number of tasks to return
        db: Database session

    Returns:
        List of tasks
    """
    try:
        query = db.query(TaskModel).filter(TaskModel.user_id == user_id)

        # Apply filters
        if status:
            query = query.filter(TaskModel.status == status)

        if priority:
            query = query.filter(TaskModel.priority == priority)

        # Exclude deleted tasks by default
        if status != "deleted":
            query = query.filter(TaskModel.status != "deleted")

        # Order by due date, then created date
        query = query.order_by(
            TaskModel.due_date.asc().nulls_last(),
            TaskModel.created_at.desc()
        )

        tasks = query.limit(limit).all()

        logger.info(
            "tasks_listed",
            user_id=user_id,
            count=len(tasks),
            status=status,
            priority=priority
        )

        return [TaskResponse(**task.to_dict()) for task in tasks]

    except Exception as e:
        logger.error("list_tasks_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID
        user_id: User ID from authentication
        db: Database session

    Returns:
        Task details
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse(**task.to_dict())


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Update a task and publish task.updated event.

    Args:
        task_id: Task ID
        updates: Fields to update
        user_id: User ID from authentication
        db: Database session

    Returns:
        Updated task
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    try:
        # Store old values for audit
        old_values = task.to_dict()

        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)

        logger.info(
            "task_updated",
            task_id=str(task.id),
            user_id=user_id,
            updated_fields=list(update_data.keys())
        )

        # Publish events
        await event_publisher.publish_task_event(
            "task.updated",
            str(task.id),
            {
                "old_values": old_values,
                "new_values": task.to_dict(),
                "updated_fields": list(update_data.keys())
            }
        )

        await event_publisher.publish_task_update(
            str(task.id),
            "updated",
            task.to_dict()
        )

        await event_publisher.publish_audit_event(
            "Task",
            str(task.id),
            "UPDATE",
            "user",
            user_id,
            old_values=old_values,
            new_values=task.to_dict()
        )

        return TaskResponse(**task.to_dict())

    except Exception as e:
        logger.error("update_task_failed", task_id=task_id, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark a task as complete and publish task.completed event.

    This event triggers the recurring task service to generate next instance.

    Args:
        task_id: Task ID
        user_id: User ID from authentication
        db: Database session

    Returns:
        Completed task
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is already completed"
        )

    try:
        old_values = task.to_dict()

        # Mark as completed
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(task)

        logger.info(
            "task_completed",
            task_id=str(task.id),
            user_id=user_id
        )

        # Publish events (triggers recurring service)
        await event_publisher.publish_task_event(
            "task.completed",
            str(task.id),
            {
                "old_values": old_values,
                "new_values": task.to_dict(),
                "completed_at": task.completed_at.isoformat()
            }
        )

        await event_publisher.publish_task_update(
            str(task.id),
            "completed",
            task.to_dict()
        )

        await event_publisher.publish_audit_event(
            "Task",
            str(task.id),
            "COMPLETE",
            "user",
            user_id,
            old_values=old_values,
            new_values=task.to_dict()
        )

        return TaskResponse(**task.to_dict())

    except Exception as e:
        logger.error("complete_task_failed", task_id=task_id, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete a task and publish task.deleted event.

    Args:
        task_id: Task ID
        user_id: User ID from authentication
        db: Database session

    Returns:
        Deletion confirmation
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    try:
        old_values = task.to_dict()

        # Soft delete
        task.status = "deleted"

        db.commit()

        logger.info(
            "task_deleted",
            task_id=str(task.id),
            user_id=user_id
        )

        # Publish events
        await event_publisher.publish_task_event(
            "task.deleted",
            str(task.id),
            {
                "old_values": old_values
            }
        )

        await event_publisher.publish_task_update(
            str(task.id),
            "deleted",
            task.to_dict()
        )

        await event_publisher.publish_audit_event(
            "Task",
            str(task.id),
            "DELETE",
            "user",
            user_id,
            old_values=old_values
        )

        return {
            "status": "deleted",
            "task_id": str(task.id),
            "message": "Task deleted successfully"
        }

    except Exception as e:
        logger.error("delete_task_failed", task_id=task_id, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )
