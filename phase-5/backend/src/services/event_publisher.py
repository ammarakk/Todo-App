"""
Event Publisher Service (Dapr)
"""
import json
from typing import Dict, Any, Optional
import httpx
from src.utils.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class EventPublisher:
    """Publish events to Kafka via Dapr"""
    
    def __init__(self):
        self.dapr_host = settings.dapr_host
        self.dapr_http_port = settings.dapr_http_port
        self.base_url = f"http://{self.dapr_host}:{self.dapr_http_port}/v1.0"
    
    async def publish(
        self,
        topic_name: str,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> bool:
        """
        Publish event to Kafka topic via Dapr
        
        Args:
            topic_name: Kafka topic name
            event_type: Type of event (e.g., "task.created")
            payload: Event data
            correlation_id: Correlation ID for tracing
        
        Returns:
            True if published successfully, False otherwise
        """
        import uuid
        
        # Build event envelope
        event_envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "topic_name": topic_name,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "timestamp": None,  # Will be set by JSON serializer
            "source_service": "todo-backend",
            "payload": payload,
        }
        
        logger.info(
            "publishing_event",
            topic=topic_name,
            event_type=event_type,
            event_id=event_envelope["event_id"],
            correlation_id=event_envelope["correlation_id"],
        )
        
        try:
            # Publish via Dapr
            url = f"{self.base_url}/publish/kafka-pubsub/{topic_name}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=event_envelope,
                    timeout=5.0,
                )
                
                if response.status_code == 200:
                    logger.info(
                        "event_published",
                        topic=topic_name,
                        event_id=event_envelope["event_id"],
                    )
                    return True
                else:
                    logger.error(
                        "event_publish_failed",
                        topic=topic_name,
                        status_code=response.status_code,
                        response=response.text,
                    )
                    return False
                    
        except Exception as e:
            logger.error(
                "event_publish_error",
                topic=topic_name,
                error=str(e),
            )
            return False
    
    async def publish_task_created(
        self,
        task_id: str,
        user_id: str,
        task_data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Publish task.created event"""
        return await self.publish(
            topic_name=settings.kafka_topic_task_events,
            event_type="task.created",
            payload={
                "task_id": task_id,
                "user_id": user_id,
                "task_data": task_data,
            },
            correlation_id=correlation_id,
        )
    
    async def publish_task_updated(
        self,
        task_id: str,
        user_id: str,
        updated_fields: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Publish task.updated event"""
        return await self.publish(
            topic_name=settings.kafka_topic_task_events,
            event_type="task.updated",
            payload={
                "task_id": task_id,
                "user_id": user_id,
                "updated_fields": updated_fields,
            },
            correlation_id=correlation_id,
        )
    
    async def publish_task_completed(
        self,
        task_id: str,
        user_id: str,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Publish task.completed event"""
        return await self.publish(
            topic_name=settings.kafka_topic_task_events,
            event_type="task.completed",
            payload={
                "task_id": task_id,
                "user_id": user_id,
            },
            correlation_id=correlation_id,
        )
    
    async def publish_task_deleted(
        self,
        task_id: str,
        user_id: str,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Publish task.deleted event"""
        return await self.publish(
            topic_name=settings.kafka_topic_task_events,
            event_type="task.deleted",
            payload={
                "task_id": task_id,
                "user_id": user_id,
            },
            correlation_id=correlation_id,
        )
    
    async def publish_reminder_created(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        trigger_time: str,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Publish reminder.created event"""
        return await self.publish(
            topic_name=settings.kafka_topic_reminders,
            event_type="reminder.created",
            payload={
                "reminder_id": reminder_id,
                "task_id": task_id,
                "user_id": user_id,
                "trigger_time": trigger_time,
            },
            correlation_id=correlation_id,
        )
