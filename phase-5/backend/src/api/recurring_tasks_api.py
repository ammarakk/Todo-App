"""
Recurring Task API Endpoints - Phase 5
CRUD operations for recurring task configurations
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.task import Task
from src.models.recurring_task import RecurringTask, RecurringTaskStatus
from src.services.recurring_task_service import get_recurring_task_service
from src.schemas.recurring_task import (
    RecurringTaskCreate,
    RecurringTaskResponse,
    RecurringTaskUpdate,
    RecurringTaskList
)
from src.orchestrator.event_publisher import EventPublisher
from src.utils.logger import get_logger

router = APIRouter(prefix="/api/recurring-tasks", tags=["recurring-tasks"])
logger = get_logger(__name__)
event_publisher = EventPublisher()


@router.post("/", response_model=RecurringTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_task(
    recurring_data: RecurringTaskCreate,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new recurring task configuration.

    This converts an existing task into a recurring task template.
    The task will automatically generate new occurrences on the specified schedule.

    Example:
    ```json
    {
        "template_task_id": "uuid-here",
        "pattern": "weekly",
        "interval": 1,
        "end_date": "2026-12-31T23:59:59Z",
        "skip_weekends": true
    }
    ```
    """
    logger.info("Creating recurring task", user_id=user_id, template_task_id=recurring_data.template_task_id)

    # Step 1: Validate template task exists and belongs to user
    template_task = db.query(Task).filter(Task.id == UUID(recurring_data.template_task_id)).first()
    if not template_task:
        logger.warning("Template task not found", task_id=recurring_data.template_task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template task not found"
        )

    if str(template_task.user_id) != user_id:
        logger.warning("Unauthorized recurring task creation", user_id=user_id, task_owner=str(template_task.user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create recurring tasks from your own tasks"
        )

    # Step 2: Check if task is already recurring
    if template_task.recurrence_rule:
        logger.warning("Task is already recurring", task_id=str(template_task.id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is already part of a recurring task configuration"
        )

    # Step 3: Validate template task has due date (required for recurrence)
    if not template_task.due_date:
        logger.warning("Template task has no due date", task_id=str(template_task.id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template task must have a due date to create recurring task"
        )

    # Step 4: Calculate initial next_due_date
    start_date = recurring_data.start_date or template_task.due_date
    next_due_date = start_date

    # Step 5: Create recurring task configuration
    recurring_task = RecurringTask(
        user_id=UUID(user_id),
        template_task_id=UUID(recurring_data.template_task_id),
        pattern=recurring_data.pattern,
        interval=recurring_data.interval,
        start_date=start_date,
        end_date=recurring_data.end_date,
        max_occurrences=recurring_data.max_occurrences,
        next_due_date=next_due_date,
        occurrences_generated=1,  # Count the template task as first occurrence
        last_generated_at=datetime.utcnow(),
        status=RecurringTaskStatus.ACTIVE,
        custom_config=recurring_data.custom_config,
        skip_weekends=recurring_data.skip_weekends,
        generate_ahead=recurring_data.generate_ahead
    )

    db.add(recurring_task)
    db.flush()  # Get the ID

    # Step 6: Update template task with recurrence_rule
    template_task.recurrence_rule = {"recurring_task_id": str(recurring_task.id)}
    db.commit()

    logger.info(
        "Recurring task created successfully",
        recurring_task_id=str(recurring_task.id),
        pattern=recurring_task.pattern,
        interval=recurring_task.interval
    )

    # Step 7: Publish events
    async def publish_events():
        await event_publisher.publish_user_action(
            entity_type="recurring_task",
            entity_id=str(recurring_task.id),
            action="created",
            user_id=user_id,
            changes={
                "pattern": recurring_task.pattern,
                "interval": recurring_task.interval,
                "template_task_id": str(template_task.id)
            }
        )

    background_tasks.add_task(publish_events)

    return RecurringTaskResponse(
        id=str(recurring_task.id),
        user_id=str(recurring_task.user_id),
        template_task_id=str(recurring_task.template_task_id),
        pattern=recurring_task.pattern,
        interval=recurring_task.interval,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        next_due_date=recurring_task.next_due_date,
        occurrences_generated=recurring_task.occurrences_generated,
        last_generated_at=recurring_task.last_generated_at,
        status=recurring_task.status,
        custom_config=recurring_task.custom_config,
        skip_weekends=recurring_task.skip_weekends,
        generate_ahead=recurring_task.generate_ahead,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.get("/", response_model=RecurringTaskList)
async def list_recurring_tasks(
    user_id: str,
    status_filter: Optional[str] = None,
    pattern_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all recurring task configurations for the current user.

    Query Parameters:
    - status: Filter by status (active, paused, completed, cancelled)
    - pattern: Filter by pattern (daily, weekly, monthly, yearly, custom)
    """
    logger.info("Listing recurring tasks", user_id=user_id, status=status_filter, pattern=pattern_filter)

    query = db.query(RecurringTask).filter(RecurringTask.user_id == UUID(user_id))

    if status_filter:
        query = query.filter(RecurringTask.status == status_filter)

    if pattern_filter:
        query = query.filter(RecurringTask.pattern == pattern_filter)

    recurring_tasks = query.order_by(RecurringTask.created_at.desc()).all()

    logger.info("Recurring tasks retrieved", count=len(recurring_tasks))

    return RecurringTaskList(
        total=len(recurring_tasks),
        items=[
            RecurringTaskResponse(
                id=str(rt.id),
                user_id=str(rt.user_id),
                template_task_id=str(rt.template_task_id),
                pattern=rt.pattern,
                interval=rt.interval,
                start_date=rt.start_date,
                end_date=rt.end_date,
                max_occurrences=rt.max_occurrences,
                next_due_date=rt.next_due_date,
                occurrences_generated=rt.occurrences_generated,
                last_generated_at=rt.last_generated_at,
                status=rt.status,
                custom_config=rt.custom_config,
                skip_weekends=rt.skip_weekends,
                generate_ahead=rt.generate_ahead,
                created_at=rt.created_at,
                updated_at=rt.updated_at
            )
            for rt in recurring_tasks
        ]
    )


@router.get("/{recurring_task_id}", response_model=RecurringTaskResponse)
async def get_recurring_task(
    recurring_task_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific recurring task configuration."""
    logger.info("Fetching recurring task", recurring_task_id=recurring_task_id, user_id=user_id)

    recurring_task = db.query(RecurringTask).filter(
        RecurringTask.id == UUID(recurring_task_id)
    ).first()

    if not recurring_task:
        logger.warning("Recurring task not found", recurring_task_id=recurring_task_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found"
        )

    if str(recurring_task.user_id) != user_id:
        logger.warning("Unauthorized access", user_id=user_id, owner=str(recurring_task.user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own recurring tasks"
        )

    return RecurringTaskResponse(
        id=str(recurring_task.id),
        user_id=str(recurring_task.user_id),
        template_task_id=str(recurring_task.template_task_id),
        pattern=recurring_task.pattern,
        interval=recurring_task.interval,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        next_due_date=recurring_task.next_due_date,
        occurrences_generated=recurring_task.occurrences_generated,
        last_generated_at=recurring_task.last_generated_at,
        status=recurring_task.status,
        custom_config=recurring_task.custom_config,
        skip_weekends=recurring_task.skip_weekends,
        generate_ahead=recurring_task.generate_ahead,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.patch("/{recurring_task_id}", response_model=RecurringTaskResponse)
async def update_recurring_task(
    recurring_task_id: str,
    update_data: RecurringTaskUpdate,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Update a recurring task configuration.

    Note: Changing pattern/interval will affect future occurrences only.
    """
    logger.info("Updating recurring task", recurring_task_id=recurring_task_id, user_id=user_id)

    recurring_task = db.query(RecurringTask).filter(
        RecurringTask.id == UUID(recurring_task_id)
    ).first()

    if not recurring_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found"
        )

    if str(recurring_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own recurring tasks"
        )

    # Update fields
    old_values = {
        "pattern": recurring_task.pattern,
        "interval": recurring_task.interval,
        "status": recurring_task.status
    }

    if update_data.pattern is not None:
        recurring_task.pattern = update_data.pattern
    if update_data.interval is not None:
        recurring_task.interval = update_data.interval
    if update_data.start_date is not None:
        recurring_task.start_date = update_data.start_date
    if update_data.end_date is not None:
        recurring_task.end_date = update_data.end_date
    if update_data.max_occurrences is not None:
        recurring_task.max_occurrences = update_data.max_occurrences
    if update_data.custom_config is not None:
        recurring_task.custom_config = update_data.custom_config
    if update_data.skip_weekends is not None:
        recurring_task.skip_weekends = update_data.skip_weekends
    if update_data.generate_ahead is not None:
        recurring_task.generate_ahead = update_data.generate_ahead
    if update_data.status is not None:
        if update_data.status == "paused":
            recurring_task.pause()
        elif update_data.status == "active":
            recurring_task.resume()
        elif update_data.status == "cancelled":
            recurring_task.cancel()

    db.commit()

    logger.info("Recurring task updated successfully", recurring_task_id=recurring_task_id)

    # Publish audit event
    async def publish_events():
        new_values = {
            "pattern": recurring_task.pattern,
            "interval": recurring_task.interval,
            "status": recurring_task.status
        }
        await event_publisher.publish_user_action(
            entity_type="recurring_task",
            entity_id=str(recurring_task.id),
            action="updated",
            user_id=user_id,
            changes=new_values
        )

    background_tasks.add_task(publish_events)

    return RecurringTaskResponse(
        id=str(recurring_task.id),
        user_id=str(recurring_task.user_id),
        template_task_id=str(recurring_task.template_task_id),
        pattern=recurring_task.pattern,
        interval=recurring_task.interval,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        next_due_date=recurring_task.next_due_date,
        occurrences_generated=recurring_task.occurrences_generated,
        last_generated_at=recurring_task.last_generated_at,
        status=recurring_task.status,
        custom_config=recurring_task.custom_config,
        skip_weekends=recurring_task.skip_weekends,
        generate_ahead=recurring_task.generate_ahead,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )


@router.delete("/{recurring_task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_recurring_task(
    recurring_task_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cancel a recurring task.

    This stops future task generation. Existing tasks are not affected.
    """
    logger.info("Cancelling recurring task", recurring_task_id=recurring_task_id, user_id=user_id)

    recurring_task = db.query(RecurringTask).filter(
        RecurringTask.id == UUID(recurring_task_id)
    ).first()

    if not recurring_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found"
        )

    if str(recurring_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own recurring tasks"
        )

    recurring_task.cancel()
    db.commit()

    logger.info("Recurring task cancelled successfully", recurring_task_id=recurring_task_id)

    # Publish audit event
    async def publish_events():
        await event_publisher.publish_user_action(
            entity_type="recurring_task",
            entity_id=str(recurring_task.id),
            action="cancelled",
            user_id=user_id,
            changes={"previous_status": "active"}
        )

    background_tasks.add_task(publish_events)

    return None


@router.post("/{recurring_task_id}/generate-next", response_model=RecurringTaskResponse)
async def generate_next_occurrence(
    recurring_task_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger generation of the next task occurrence.

    Useful for testing or when you want to generate ahead of schedule.
    """
    logger.info("Manual generation triggered", recurring_task_id=recurring_task_id, user_id=user_id)

    recurring_task = db.query(RecurringTask).filter(
        RecurringTask.id == UUID(recurring_task_id)
    ).first()

    if not recurring_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring task not found"
        )

    if str(recurring_task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only generate occurrences for your own recurring tasks"
        )

    if recurring_task.status != RecurringTaskStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot generate occurrence for {recurring_task.status} recurring task"
        )

    # Get the service to handle generation
    service = get_recurring_task_service()

    # Use the last generated task or template task
    template_task = db.query(Task).filter(Task.id == recurring_task.template_task_id).first()
    if not template_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template task not found"
        )

    # Generate next occurrence
    result = await service.handle_task_completed(
        task_id=str(template_task.id),
        user_id=user_id,
        db=db
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not generate next occurrence (recurring task may be completed)"
        )

    db.refresh(recurring_task)

    return RecurringTaskResponse(
        id=str(recurring_task.id),
        user_id=str(recurring_task.user_id),
        template_task_id=str(recurring_task.template_task_id),
        pattern=recurring_task.pattern,
        interval=recurring_task.interval,
        start_date=recurring_task.start_date,
        end_date=recurring_task.end_date,
        max_occurrences=recurring_task.max_occurrences,
        next_due_date=recurring_task.next_due_date,
        occurrences_generated=recurring_task.occurrences_generated,
        last_generated_at=recurring_task.last_generated_at,
        status=recurring_task.status,
        custom_config=recurring_task.custom_config,
        skip_weekends=recurring_task.skip_weekends,
        generate_ahead=recurring_task.generate_ahead,
        created_at=recurring_task.created_at,
        updated_at=recurring_task.updated_at
    )
