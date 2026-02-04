"""
Reminder Scheduler Service - Phase 5
Intelligent Reminders Feature

Background service that periodically checks for due reminders
and publishes them to Kafka for delivery by the notification service.

This runs as a background task alongside the FastAPI application.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from dapr.clients import DaprClient

from src.db.session import get_db
from src.models.reminder import Reminder
from src.models.task import Task
from src.utils.logger import get_logger


logger = get_logger(__name__)


class ReminderScheduler:
    """
    Background scheduler for task reminders.

    Checks every 60 seconds for reminders that are due to be sent.
    Publishes reminder events to Kafka for the notification service to process.
    """

    def __init__(self, check_interval_seconds: int = 60, max_retries: int = 3):
        """
        Initialize the reminder scheduler.

        Args:
            check_interval_seconds: How often to check for due reminders (default: 60s)
            max_retries: Maximum retry attempts for failed reminders
        """
        self.check_interval = check_interval_seconds
        self.max_retries = max_retries
        self.dapr = DaprClient()
        self.pubsub_name = "kafka-pubsub"
        self.topic_name = "reminders"
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the background scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        logger.info("Starting reminder scheduler", check_interval_seconds=self.check_interval)
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        """Stop the background scheduler."""
        if not self._running:
            return

        logger.info("Stopping reminder scheduler")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _scheduler_loop(self):
        """Main scheduler loop - runs until stopped."""
        while self._running:
            try:
                await self._check_and_process_reminders()
            except Exception as e:
                logger.error("Scheduler loop error", error=str(e), exc_info=True)

            # Wait for next check
            await asyncio.sleep(self.check_interval)

    async def _check_and_process_reminders(self):
        """
        Check for due reminders and publish them to Kafka.

        A reminder is "due" if:
        1. Status is "pending"
        2. trigger_at <= now
        3. delivery_attempts < max_retries
        """
        db: Session = next(get_db())

        try:
            # Find due reminders
            now = datetime.utcnow()
            due_reminders = db.query(Reminder).filter(
                Reminder.status == "pending",
                Reminder.trigger_at <= now,
                Reminder.retry_count < self.max_retries
            ).all()

            if not due_reminders:
                return

            logger.info("Found due reminders", count=len(due_reminders))

            # Process each reminder
            for reminder in due_reminders:
                await self._process_reminder(reminder, db)

            db.commit()

        except Exception as e:
            logger.error("Error processing reminders", error=str(e), exc_info=True)
            db.rollback()
        finally:
            db.close()

    async def _process_reminder(self, reminder: Reminder, db: Session):
        """
        Process a single due reminder.

        1. Fetch task details (for email content)
        2. Publish event to Kafka
        3. Update reminder status
        """
        try:
            # Fetch task details
            task = db.query(Task).filter(Task.id == reminder.task_id).first()

            if not task:
                logger.warning(
                    "Task not found for reminder",
                    reminder_id=str(reminder.id),
                    task_id=str(reminder.task_id)
                )
                # Mark as failed - task doesn't exist
                reminder.status = "failed"
                reminder.last_error = "Task not found"
                return

            # Check if task is already completed
            if task.status == "completed":
                logger.info(
                    "Task already completed, expiring reminder",
                    reminder_id=str(reminder.id),
                    task_id=str(reminder.id)
                )
                reminder.status = "expired"
                return

            # Build event payload with task context
            event_data = {
                "reminder_id": str(reminder.id),
                "task_id": str(reminder.task_id),
                "user_id": str(reminder.user_id),
                "trigger_at": reminder.trigger_time.isoformat(),
                "delivery_method": reminder.delivery_method,
                "destination": reminder.destination,
                "custom_message": reminder.custom_message,
                # Task context for email rendering
                "task_title": task.title,
                "task_description": task.description,
                "task_due_date": task.due_date.isoformat() if task.due_date else None,
                "task_priority": task.priority,
            }

            # Publish to Kafka via Dapr
            import json
            await self.dapr.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topic_name,
                data=json.dumps(event_data),
                data_content_type="application/json"
            )

            # Update reminder
            reminder.status = "sent"
            reminder.sent_at = datetime.utcnow()
            reminder.retry_count += 1

            logger.info(
                "Reminder sent successfully",
                reminder_id=str(reminder.id),
                task_id=str(reminder.task_id),
                delivery_method=reminder.delivery_method
            )

        except Exception as e:
            logger.error(
                "Failed to process reminder",
                reminder_id=str(reminder.id),
                error=str(e),
                exc_info=True
            )

            # Mark as failed
            reminder.status = "failed"
            reminder.retry_count += 1
            reminder.last_retry_at = datetime.utcnow()
            reminder.last_error = str(e)

    async def check_now(self):
        """
        Manually trigger a check for due reminders.

        Useful for testing or manual triggering.
        """
        logger.info("Manual reminder check triggered")
        await self._check_and_process_reminders()


# Global scheduler instance
_scheduler: Optional[ReminderScheduler] = None


def get_scheduler() -> ReminderScheduler:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = ReminderScheduler()
    return _scheduler


async def start_scheduler():
    """Start the global reminder scheduler."""
    scheduler = get_scheduler()
    await scheduler.start()
    logger.info("Reminder scheduler started")


async def stop_scheduler():
    """Stop the global reminder scheduler."""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        logger.info("Reminder scheduler stopped")


# Lifespan functions for FastAPI
async def on_startup():
    """Start scheduler on application startup."""
    await start_scheduler()


async def on_shutdown():
    """Stop scheduler on application shutdown."""
    await stop_scheduler()
