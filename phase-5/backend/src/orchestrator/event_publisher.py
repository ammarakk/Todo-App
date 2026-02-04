"""
Event Publisher Module - Phase 5

Publishes events to Kafka via Dapr Pub/Sub.
All state changes are published as events for microservices to consume.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dapr.clients import DaprClient
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EventPublisher:
    """
    Publishes domain events to Kafka via Dapr.

    All state changes in the system are published as events.
    Microservices subscribe to these events for async processing.
    """

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        """
        Initialize event publisher.

        Args:
            dapr_client: Optional Dapr client (defaults to new instance)
        """
        self.dapr = dapr_client or DaprClient()
        self.pubsub_name = "kafka-pubsub"

        # Topic names (must match Dapr component config)
        self.topics = {
            "task_events": "task-events",
            "reminders": "reminders",
            "task_updates": "task-updates",
            "audit_events": "audit-events"
        }

    async def publish_task_event(
        self,
        event_type: str,
        task_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a task lifecycle event.

        Event types:
        - task.created
        - task.updated
        - task.completed
        - task.deleted

        Args:
            event_type: Type of event (e.g., "task.created")
            task_id: ID of the task
            payload: Event data (task object, changes, etc.)
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if published successfully, False otherwise
        """
        try:
            correlation_id = correlation_id or str(uuid.uuid4())

            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "topic_name": self.topics["task_events"],
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_service": "backend",
                "payload": {
                    "task_id": task_id,
                    **payload
                }
            }

            # Publish to Dapr
            await self.dapr.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topics["task_events"],
                data=json.dumps(event),
                data_content_type="application/json"
            )

            logger.info(
                "task_event_published",
                event_type=event_type,
                task_id=task_id,
                correlation_id=correlation_id
            )

            return True

        except Exception as e:
            logger.error(
                "task_event_publish_failed",
                event_type=event_type,
                task_id=task_id,
                error=str(e)
            )
            return False

    async def publish_reminder_event(
        self,
        event_type: str,
        reminder_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a reminder event.

        Event types:
        - reminder.created
        - reminder.triggered
        - reminder.sent
        - reminder.failed

        Args:
            event_type: Type of event
            reminder_id: ID of the reminder
            payload: Event data
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        try:
            correlation_id = correlation_id or str(uuid.uuid4())

            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "topic_name": self.topics["reminders"],
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_service": "backend",
                "payload": {
                    "reminder_id": reminder_id,
                    **payload
                }
            }

            await self.dapr.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topics["reminders"],
                data=json.dumps(event),
                data_content_type="application/json"
            )

            logger.info(
                "reminder_event_published",
                event_type=event_type,
                reminder_id=reminder_id,
                correlation_id=correlation_id
            )

            return True

        except Exception as e:
            logger.error(
                "reminder_event_publish_failed",
                event_type=event_type,
                reminder_id=reminder_id,
                error=str(e)
            )
            return False

    async def publish_reminder_created(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        trigger_at: str,
        delivery_method: str,
        destination: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a reminder.created event.

        This event triggers the reminder scheduler to track this reminder.

        Args:
            reminder_id: ID of the reminder
            task_id: ID of the associated task
            user_id: ID of the user
            trigger_at: When to trigger the reminder (ISO 8601)
            delivery_method: How to deliver (email, push, sms)
            destination: Destination address
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        return await self.publish_reminder_event(
            event_type="reminder.created",
            reminder_id=reminder_id,
            payload={
                "task_id": task_id,
                "user_id": user_id,
                "trigger_at": trigger_at,
                "delivery_method": delivery_method,
                "destination": destination
            },
            correlation_id=correlation_id
        )

    async def publish_reminder_cancelled(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a reminder.cancelled event.

        This event signals the scheduler to stop tracking this reminder.

        Args:
            reminder_id: ID of the reminder
            task_id: ID of the associated task
            user_id: ID of the user
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        return await self.publish_reminder_event(
            event_type="reminder.cancelled",
            reminder_id=reminder_id,
            payload={
                "task_id": task_id,
                "user_id": user_id
            },
            correlation_id=correlation_id
        )

    async def publish_user_action(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: str,
        changes: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a user action audit event (convenience method).

        This is a simplified wrapper for user-initiated actions.

        Args:
            entity_type: Type of entity (task, reminder, etc.)
            entity_id: ID of the entity
            action: Action performed (created, updated, deleted, cancelled)
            user_id: ID of the user
            changes: What changed (for new values)
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        return await self.publish_audit_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action.upper(),
            actor_type="user",
            actor_id=user_id,
            old_values=None,
            new_values=changes,
            correlation_id=correlation_id
        )

    async def publish_task_update(
        self,
        task_id: str,
        update_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish a task update event for real-time sync.

        These events are consumed by frontend to update UI in real-time.

        Args:
            task_id: ID of the task
            update_type: Type of update (created, updated, completed, deleted)
            payload: Update data
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        try:
            correlation_id = correlation_id or str(uuid.uuid4())

            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": f"task.{update_type}",
                "topic_name": self.topics["task_updates"],
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_service": "backend",
                "payload": {
                    "task_id": task_id,
                    "update_type": update_type,
                    **payload
                }
            }

            await self.dapr.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topics["task_updates"],
                data=json.dumps(event),
                data_content_type="application/json"
            )

            logger.info(
                "task_update_published",
                task_id=task_id,
                update_type=update_type,
                correlation_id=correlation_id
            )

            return True

        except Exception as e:
            logger.error(
                "task_update_publish_failed",
                task_id=task_id,
                update_type=update_type,
                error=str(e)
            )
            return False

    async def publish_audit_event(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_type: str,
        actor_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish an audit event.

        Audit events track all state changes for compliance and debugging.

        Args:
            entity_type: Type of entity (Task, Reminder, etc.)
            entity_id: ID of the entity
            action: Action performed (CREATE, UPDATE, DELETE)
            actor_type: Type of actor (user, system, service)
            actor_id: ID of the actor
            old_values: Previous values (for UPDATE)
            new_values: New values
            correlation_id: Optional correlation ID

        Returns:
            True if published successfully, False otherwise
        """
        try:
            correlation_id = correlation_id or str(uuid.uuid4())

            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": "audit.logged",
                "topic_name": self.topics["audit_events"],
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_service": "backend",
                "payload": {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "action": action,
                    "actor_type": actor_type,
                    "actor_id": actor_id,
                    "old_values": old_values,
                    "new_values": new_values
                }
            }

            await self.dapr.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.topics["audit_events"],
                data=json.dumps(event),
                data_content_type="application/json"
            )

            logger.info(
                "audit_event_published",
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                actor_id=actor_id,
                correlation_id=correlation_id
            )

            return True

        except Exception as e:
            logger.error(
                "audit_event_publish_failed",
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                error=str(e)
            )
            return False
