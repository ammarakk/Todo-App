"""
Reminder API Endpoints - Phase 5
Intelligent Reminders Feature

Provides CRUD operations for task reminders with automatic
Dapr event publishing to trigger notifications.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.reminder import Reminder
from src.models.task import Task
from src.orchestrator.event_publisher import EventPublisher
from src.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate
from src.utils.logger import get_logger

router = APIRouter(prefix="/api/reminders", tags=["reminders"])
logger = get_logger(__name__)


# Initialize event publisher
event_publisher = EventPublisher()


def calculate_trigger_time(task_due_date: datetime, trigger_type: str, custom_offset: Optional[int] = None) -> datetime:
    """
    Calculate the trigger time based on task due date and trigger type.

    Args:
        task_due_date: When the task is due
        trigger_type: Type of reminder trigger (before_15_min, before_1_hour, etc.)
        custom_offset: Custom offset in minutes (only for CUSTOM trigger type)

    Returns:
        datetime: When the reminder should trigger
    """
    offsets = {
        "at_due_time": timedelta(minutes=0),
        "before_15_min": timedelta(minutes=-15),
        "before_30_min": timedelta(minutes=-30),
        "before_1_hour": timedelta(hours=-1),
        "before_1_day": timedelta(days=-1),
    }

    if trigger_type == "custom" and custom_offset is not None:
        return task_due_date + timedelta(minutes=-custom_offset)

    offset = offsets.get(trigger_type, timedelta(minutes=-15))  # Default: 15 minutes before
    return task_due_date + offset


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new reminder for a task.

    Flow:
    1. Validate task exists and belongs to user
    2. Calculate trigger time based on task due date
    3. Create reminder in database
    4. Publish reminder.created event to Kafka (triggers scheduler)
    5. Publish audit event

    Example:
    ```json
    {
        "task_id": "123e4567-e89b-12d3-a456-426614174000",
        "trigger_type": "before_15_min",
        "delivery_method": "email",
        "destination": "user@example.com"
    }
    ```
    """
    logger.info("Creating reminder", user_id=user_id, task_id=str(reminder_data.task_id))

    # Step 1: Validate task exists and belongs to user
    task = db.query(Task).filter(Task.id == reminder_data.task_id).first()
    if not task:
        logger.warning("Task not found", task_id=str(reminder_data.task_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if str(task.user_id) != user_id:
        logger.warning("Unauthorized reminder creation", user_id=user_id, task_owner=str(task.user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create reminders for your own tasks"
        )

    if not task.due_date:
        logger.warning("Task has no due date", task_id=str(task.id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create reminder for task without due date"
        )

    # Step 2: Calculate trigger time
    trigger_at = calculate_trigger_time(
        task.due_date,
        reminder_data.trigger_type,
        reminder_data.custom_offset_minutes
    )

    # Check if trigger time is in the past
    if trigger_at < datetime.utcnow():
        logger.warning("Trigger time in the past", trigger_at=trigger_at.isoformat())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reminder trigger time cannot be in the past"
        )

    # Step 3: Create reminder
    reminder = Reminder(
        task_id=reminder_data.task_id,
        user_id=UUID(user_id),
        trigger_type=reminder_data.trigger_type,
        custom_offset_minutes=reminder_data.custom_offset_minutes,
        trigger_at=trigger_at,
        delivery_method=reminder_data.delivery_method,
        destination=reminder_data.destination,
        custom_message=reminder_data.custom_message,
        status="pending"
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    logger.info(
        "Reminder created successfully",
        reminder_id=str(reminder.id),
        trigger_at=trigger_at.isoformat()
    )

    # Step 4: Publish events in background
    async def publish_events():
        # Publish reminder.created event (triggers scheduler)
        await event_publisher.publish_reminder_created(
            reminder_id=str(reminder.id),
            task_id=str(reminder.task_id),
            user_id=user_id,
            trigger_at=trigger_at.isoformat(),
            delivery_method=reminder.delivery_method,
            destination=reminder.destination
        )

        # Publish audit event
        await event_publisher.publish_user_action(
            entity_type="reminder",
            entity_id=str(reminder.id),
            action="created",
            user_id=user_id,
            changes={"trigger_at": trigger_at.isoformat()}
        )

    background_tasks.add_task(publish_events)

    return ReminderResponse(
        id=str(reminder.id),
        task_id=str(reminder.task_id),
        trigger_type=reminder.trigger_type,
        custom_offset_minutes=reminder.custom_offset_minutes,
        trigger_at=reminder.trigger_at,
        status=reminder.status,
        delivery_method=reminder.delivery_method,
        destination=reminder.destination,
        custom_message=reminder.custom_message,
        delivery_attempts=reminder.retry_count,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.get("/", response_model=List[ReminderResponse])
async def list_reminders(
    user_id: str,
    task_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all reminders for the current user.

    Query Parameters:
    - task_id: Filter by specific task
    - status: Filter by status (pending, sent, failed, cancelled)
    """
    logger.info("Listing reminders", user_id=user_id, task_id=task_id, status=status_filter)

    query = db.query(Reminder).filter(Reminder.user_id == UUID(user_id))

    if task_id:
        query = query.filter(Reminder.task_id == UUID(task_id))

    if status_filter:
        query = query.filter(Reminder.status == status_filter)

    reminders = query.order_by(Reminder.trigger_at).all()

    logger.info("Reminders retrieved", count=len(reminders))

    return [
        ReminderResponse(
            id=str(r.id),
            task_id=str(r.task_id),
            trigger_type=r.trigger_type,
            custom_offset_minutes=r.custom_offset_minutes,
            trigger_at=r.trigger_at,
            status=r.status,
            delivery_method=r.delivery_method,
            destination=r.destination,
            custom_message=r.custom_message,
            delivery_attempts=r.retry_count,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in reminders
    ]


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str, user_id: str, db: Session = Depends(get_db)):
    """Get details of a specific reminder."""
    logger.info("Fetching reminder", reminder_id=reminder_id, user_id=user_id)

    reminder = db.query(Reminder).filter(Reminder.id == UUID(reminder_id)).first()

    if not reminder:
        logger.warning("Reminder not found", reminder_id=reminder_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    if str(reminder.user_id) != user_id:
        logger.warning("Unauthorized access", user_id=user_id, reminder_owner=str(reminder.user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own reminders"
        )

    return ReminderResponse(
        id=str(reminder.id),
        task_id=str(reminder.task_id),
        trigger_type=reminder.trigger_type,
        custom_offset_minutes=reminder.custom_offset_minutes,
        trigger_at=reminder.trigger_at,
        status=reminder.status,
        delivery_method=reminder.delivery_method,
        destination=reminder.destination,
        custom_message=reminder.custom_message,
        delivery_attempts=reminder.retry_count,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reminder(
    reminder_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cancel a reminder.

    This marks the reminder as cancelled and publishes a reminder.cancelled event.
    """
    logger.info("Cancelling reminder", reminder_id=reminder_id, user_id=user_id)

    reminder = db.query(Reminder).filter(Reminder.id == UUID(reminder_id)).first()

    if not reminder:
        logger.warning("Reminder not found", reminder_id=reminder_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    if str(reminder.user_id) != user_id:
        logger.warning("Unauthorized cancellation", user_id=user_id, reminder_owner=str(reminder.user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own reminders"
        )

    if reminder.status == "sent":
        logger.warning("Cannot cancel sent reminder", reminder_id=reminder_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a reminder that has already been sent"
        )

    # Update status
    reminder.status = "cancelled"
    db.commit()

    logger.info("Reminder cancelled successfully", reminder_id=reminder_id)

    # Publish cancellation event
    async def publish_events():
        await event_publisher.publish_reminder_cancelled(
            reminder_id=str(reminder.id),
            task_id=str(reminder.task_id),
            user_id=user_id
        )

        await event_publisher.publish_user_action(
            entity_type="reminder",
            entity_id=str(reminder.id),
            action="cancelled",
            user_id=user_id,
            changes={"previous_status": "pending"}
        )

    background_tasks.add_task(publish_events)

    return None


@router.post("/{reminder_id}/retry", response_model=ReminderResponse)
async def retry_failed_reminder(
    reminder_id: str,
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Retry a failed reminder.

    Resets the status to pending and republishes the reminder event.
    """
    logger.info("Retrying failed reminder", reminder_id=reminder_id, user_id=user_id)

    reminder = db.query(Reminder).filter(Reminder.id == UUID(reminder_id)).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    if str(reminder.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only retry your own reminders"
        )

    if reminder.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only failed reminders can be retried"
        )

    # Reset status
    reminder.status = "pending"
    reminder.retry_count = 0
    reminder.last_retry_at = None
    reminder.last_error = None
    db.commit()

    logger.info("Reminder reset for retry", reminder_id=reminder_id)

    # Republish reminder event
    async def publish_events():
        await event_publisher.publish_reminder_created(
            reminder_id=str(reminder.id),
            task_id=str(reminder.task_id),
            user_id=user_id,
            trigger_at=reminder.trigger_time.isoformat(),
            delivery_method=reminder.delivery_method,
            destination=reminder.destination
        )

    background_tasks.add_task(publish_events)

    return ReminderResponse(
        id=str(reminder.id),
        task_id=str(reminder.task_id),
        trigger_type=reminder.trigger_type,
        custom_offset_minutes=reminder.custom_offset_minutes,
        trigger_at=reminder.trigger_time,
        status=reminder.status,
        delivery_method=reminder.delivery_method,
        destination=reminder.destination,
        custom_message=reminder.custom_message,
        delivery_attempts=reminder.retry_count,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at
    )
