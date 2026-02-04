"""
Recurring Task Service - Phase 5
Automatically generates next task occurrence when recurring task is completed
"""

import json
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from dapr.clients import DaprClient

from src.models.task import Task
from src.models.recurring_task import RecurringTask, RecurringTaskStatus
from src.orchestrator.event_publisher import EventPublisher
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RecurringTaskService:
    """
    Service for managing recurring tasks.

    Listens for task.completed events and automatically generates
    the next occurrence for recurring tasks.
    """

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        """
        Initialize recurring task service.

        Args:
            dapr_client: Optional Dapr client (defaults to new instance)
        """
        self.dapr = dapr_client or DaprClient()
        self.event_publisher = EventPublisher()
        self.pubsub_name = "kafka-pubsub"
        self.task_events_topic = "task-events"

    async def handle_task_completed(
        self,
        task_id: str,
        user_id: str,
        db: Session
    ) -> Optional[dict]:
        """
        Handle task completion by generating next occurrence if it's recurring.

        This is called when a task.completed event is received.

        Args:
            task_id: ID of the completed task
            user_id: ID of the user who owns the task
            db: Database session

        Returns:
            Dict with details of newly created task, or None if not recurring
        """
        try:
            # Step 1: Fetch the completed task
            completed_task = db.query(Task).filter(Task.id == UUID(task_id)).first()
            if not completed_task:
                logger.warning("Task not found for recurring generation", task_id=task_id)
                return None

            # Step 2: Check if task has a recurring configuration
            if not completed_task.recurrence_rule:
                logger.debug("Task is not recurring", task_id=task_id)
                return None

            recurring_rule = completed_task.recurrence_rule
            recurring_task_id = recurring_rule.get("recurring_task_id")

            if not recurring_task_id:
                logger.warning("Task has recurrence_rule but no recurring_task_id", task_id=task_id)
                return None

            # Step 3: Fetch recurring task configuration
            recurring_task = db.query(RecurringTask).filter(
                RecurringTask.id == UUID(recurring_task_id)
            ).first()

            if not recurring_task:
                logger.warning("Recurring task not found", recurring_task_id=recurring_task_id)
                return None

            # Step 4: Check if should continue generating
            if recurring_task.status != RecurringTaskStatus.ACTIVE:
                logger.info(
                    "Recurring task not active, skipping generation",
                    recurring_task_id=recurring_task_id,
                    status=recurring_task.status
                )
                return None

            if recurring_task.should_stop_generating():
                logger.info(
                    "Recurring task reached end criteria",
                    recurring_task_id=recurring_task_id,
                    occurrences_generated=recurring_task.occurrences_generated
                )
                recurring_task.mark_as_completed()
                db.commit()
                return None

            # Step 5: Calculate next due date
            if not completed_task.due_date:
                logger.warning("Task has no due_date, cannot calculate next occurrence", task_id=task_id)
                return None

            next_due_date = recurring_task.calculate_next_due_date(completed_task.due_date)

            if not next_due_date:
                logger.info("No more occurrences to generate", recurring_task_id=recurring_task_id)
                recurring_task.mark_as_completed()
                db.commit()
                return None

            # Step 6: Create new task instance
            new_task = Task(
                user_id=recurring_task.user_id,
                title=completed_task.title,
                description=completed_task.description,
                due_date=next_due_date,
                priority=completed_task.priority,
                tags=completed_task.tags.copy(),
                status="active",
                recurrence_rule={"recurring_task_id": str(recurring_task.id)},
                ai_metadata=completed_task.ai_metadata.copy() if completed_task.ai_metadata else None
            )

            db.add(new_task)
            db.flush()  # Get the ID without committing

            # Step 7: Update recurring task tracking
            recurring_task.next_due_date = next_due_date
            recurring_task.occurrences_generated += 1
            recurring_task.last_generated_at = datetime.utcnow()

            db.commit()
            db.refresh(new_task)
            db.refresh(recurring_task)

            logger.info(
                "Recurring task generated successfully",
                recurring_task_id=str(recurring_task.id),
                new_task_id=str(new_task.id),
                occurrence_number=recurring_task.occurrences_generated,
                next_due_date=next_due_date.isoformat()
            )

            # Step 8: Publish events
            await self._publish_task_generated_events(
                recurring_task=recurring_task,
                new_task=new_task,
                db=db
            )

            return {
                "recurring_task_id": str(recurring_task.id),
                "new_task_id": str(new_task.id),
                "occurrence_number": recurring_task.occurrences_generated,
                "next_due_date": next_due_date.isoformat()
            }

        except Exception as e:
            logger.error(
                "Failed to generate recurring task",
                task_id=task_id,
                error=str(e),
                exc_info=True
            )
            db.rollback()
            return None

    async def _publish_task_generated_events(
        self,
        recurring_task: RecurringTask,
        new_task: Task,
        db: Session
    ):
        """
        Publish events when a recurring task is generated.

        Args:
            recurring_task: The recurring task configuration
            new_task: The newly generated task
            db: Database session
        """
        # Publish task.created event
        await self.event_publisher.publish_task_event(
            event_type="task.created",
            task_id=str(new_task.id),
            payload={
                "user_id": str(new_task.user_id),
                "title": new_task.title,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "recurrence_rule": new_task.recurrence_rule,
                "auto_generated": True,
                "recurring_task_id": str(recurring_task.id),
                "occurrence_number": recurring_task.occurrences_generated
            }
        )

        # Publish task-updates for real-time sync
        await self.event_publisher.publish_task_update(
            task_id=str(new_task.id),
            update_type="created",
            payload={
                "user_id": str(new_task.user_id),
                "title": new_task.title,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "auto_generated": True
            }
        )

        # Publish audit event
        await self.event_publisher.publish_user_action(
            entity_type="task",
            entity_id=str(new_task.id),
            action="auto_generated",
            user_id=str(new_task.user_id),
            changes={
                "recurring_task_id": str(recurring_task.id),
                "occurrence_number": recurring_task.occurrences_generated,
                "pattern": recurring_task.pattern
            }
        )

    async def generate_ahead_tasks(self, db: Session, max_to_generate: int = 100):
        """
        Generate tasks ahead of time for recurring tasks with generate_ahead > 0.

        This is called periodically by a background scheduler.

        Args:
            db: Database session
            max_to_generate: Maximum number of tasks to generate in one batch
        """
        try:
            # Find recurring tasks that need ahead generation
            recurring_tasks = db.query(RecurringTask).filter(
                RecurringTask.status == RecurringTaskStatus.ACTIVE,
                RecurringTask.generate_ahead > 0,
                RecurringTask.next_due_date.isnot(None)
            ).limit(max_to_generate).all()

            logger.info("Found recurring tasks for ahead generation", count=len(recurring_tasks))

            for recurring_task in recurring_tasks:
                # Count existing pending tasks for this recurring task
                pending_count = db.query(Task).filter(
                    Task.recurrence_rule["recurring_task_id"].astext == str(recurring_task.id),
                    Task.status == "active"
                ).count()

                tasks_needed = recurring_task.generate_ahead - pending_count

                if tasks_needed <= 0:
                    continue

                # Generate tasks ahead
                await self._generate_tasks_ahead(
                    recurring_task=recurring_task,
                    tasks_to_generate=tasks_needed,
                    db=db
                )

            db.commit()

        except Exception as e:
            logger.error("Failed to generate ahead tasks", error=str(e), exc_info=True)
            db.rollback()

    async def _generate_tasks_ahead(
        self,
        recurring_task: RecurringTask,
        tasks_to_generate: int,
        db: Session
    ):
        """
        Generate multiple tasks ahead of time for a recurring task.

        Args:
            recurring_task: The recurring task configuration
            tasks_to_generate: Number of tasks to generate
            db: Database session
        """
        # Get the template task
        template_task = db.query(Task).filter(
            Task.id == recurring_task.template_task_id
        ).first()

        if not template_task:
            logger.warning(
                "Template task not found for ahead generation",
                template_task_id=str(recurring_task.template_task_id)
            )
            return

        # Start from next_due_date or template task due date
        current_due_date = recurring_task.next_due_date or template_task.due_date

        if not current_due_date:
            logger.warning("No due date to base ahead generation on", recurring_task_id=str(recurring_task.id))
            return

        for i in range(tasks_to_generate):
            # Check if should stop
            if recurring_task.should_stop_generating():
                break

            # Calculate next due date
            current_due_date = recurring_task.calculate_next_due_date(current_due_date)

            if not current_due_date:
                recurring_task.mark_as_completed()
                break

            # Create task
            new_task = Task(
                user_id=recurring_task.user_id,
                title=template_task.title,
                description=template_task.description,
                due_date=current_due_date,
                priority=template_task.priority,
                tags=template_task.tags.copy() if template_task.tags else [],
                status="active",
                recurrence_rule={"recurring_task_id": str(recurring_task.id)},
                ai_metadata=template_task.ai_metadata.copy() if template_task.ai_metadata else None
            )

            db.add(new_task)
            db.flush()

            # Update tracking
            recurring_task.occurrences_generated += 1
            recurring_task.next_due_date = current_due_date

            logger.info(
                "Ahead task generated",
                recurring_task_id=str(recurring_task.id),
                task_id=str(new_task.id),
                due_date=current_due_date.isoformat()
            )


# Global service instance
_service: Optional[RecurringTaskService] = None


def get_recurring_task_service() -> RecurringTaskService:
    """Get the global recurring task service instance."""
    global _service
    if _service is None:
        _service = RecurringTaskService()
    return _service
