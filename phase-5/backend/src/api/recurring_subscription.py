"""
Recurring Task Subscription Endpoint - Phase 5
Dapr subscription handler for task.completed events
"""

from typing import Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.recurring_task_service import get_recurring_task_service
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class TaskCompletedEvent(BaseModel):
    """Schema for task.completed event from Kafka"""
    event_id: str
    event_type: str
    correlation_id: str
    timestamp: str
    source_service: str
    payload: Dict[str, Any]


@router.post("/task-completed")
async def handle_task_completed_event(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Dapr subscription endpoint for task.completed events.

    When a task is marked complete, this endpoint is automatically invoked
    by Dapr to generate the next occurrence for recurring tasks.

    Flow:
    1. Dapr delivers task.completed event from Kafka
    2. Extract task_id and user_id from event payload
    3. Check if task is recurring (has recurrence_rule)
    4. Calculate next due date based on pattern
    5. Create new task instance
    6. Publish task.created event
    """
    try:
        # Parse event data
        event_data = await request.json()
        logger.info("Task completed event received", event_data=event_data)

        # Validate event structure
        if "payload" not in event_data or "task_id" not in event_data["payload"]:
            logger.error("Invalid event payload", event_data=event_data)
            raise HTTPException(status_code=400, detail="Invalid event payload")

        task_id = event_data["payload"]["task_id"]
        user_id = event_data["payload"].get("user_id")

        if not task_id or not user_id:
            logger.error("Missing task_id or user_id in event", event_data=event_data)
            raise HTTPException(status_code=400, detail="Missing task_id or user_id")

        logger.info(
            "Processing task completed for recurring generation",
            task_id=task_id,
            user_id=user_id
        )

        # Handle recurring task generation in background
        async def process_recurring_task():
            db: Session = next(get_db())
            try:
                service = get_recurring_task_service()
                result = await service.handle_task_completed(
                    task_id=task_id,
                    user_id=user_id,
                    db=db
                )

                if result:
                    logger.info(
                        "Recurring task generated successfully",
                        task_id=task_id,
                        result=result
                    )
                else:
                    logger.debug(
                        "Task is not recurring or no more occurrences to generate",
                        task_id=task_id
                    )

            except Exception as e:
                logger.error(
                    "Failed to process recurring task generation",
                    task_id=task_id,
                    error=str(e),
                    exc_info=True
                )
            finally:
                db.close()

        background_tasks.add_task(process_recurring_task)

        return {
            "status": "accepted",
            "message": "Task completed event received, processing in background"
        }

    except Exception as e:
        logger.error(
            "Failed to handle task completed event",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Failed to process event: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the recurring task subscription"""
    return {
        "status": "healthy",
        "service": "recurring-task-subscription",
        "subscription": "task-completed"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "service": "recurring-task-subscription"
    }
