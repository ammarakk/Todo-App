"""
WebSocket Broadcaster Service - Phase 5
Subscribes to Kafka task-updates topic and broadcasts to WebSocket clients
"""

import json
import asyncio
from typing import Optional
from dapr.clients import DaprClient
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.task import Task
from src.services.websocket_manager import get_websocket_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketBroadcaster:
    """
    Background service that subscribes to Kafka task-updates topic
    and broadcasts updates to connected WebSocket clients.

    This enables real-time multi-client synchronization.
    """

    def __init__(self, check_interval_seconds: int = 1):
        """
        Initialize the WebSocket broadcaster.

        Args:
            check_interval_seconds: How often to poll for new messages (default: 1s)
        """
        self.dapr = DaprClient()
        self.pubsub_name = "kafka-pubsub"
        self.topic_name = "task-updates"
        self.check_interval = check_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.websocket_manager = get_websocket_manager()

    async def start(self):
        """Start the background broadcaster."""
        if self._running:
            logger.warning("WebSocket broadcaster already running")
            return

        logger.info("Starting WebSocket broadcaster", topic=self.topic_name)
        self._running = True
        self._task = asyncio.create_task(self._poll_messages())

    async def stop(self):
        """Stop the background broadcaster."""
        if not self._running:
            return

        logger.info("Stopping WebSocket broadcaster")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _poll_messages(self):
        """
        Main polling loop - continuously checks for new Kafka messages.

        Dapr doesn't support async subscribe, so we poll in a loop.
        """
        while self._running:
            try:
                # Use Dapr's subscribe method in a thread pool
                # to avoid blocking the event loop
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._subscribe_sync)

            except Exception as e:
                logger.error(
                    "Error in broadcaster loop",
                    error=str(e),
                    exc_info=True
                )

            # Small delay between polls
            await asyncio.sleep(self.check_interval)

    def _subscribe_sync(self):
        """
        Synchronous Dapr subscription.

        This runs in a thread pool to avoid blocking the async event loop.
        Dapr client doesn't support async, so we use this approach.
        """
        try:
            # Subscribe to Kafka topic via Dapr
            with self.dapr.subscribe(
                pubsub_name=self.pubsub_name,
                topic=self.topic_name,
                disable_beta_message_headers=True
            ) as subscription:
                for msg in subscription:
                    try:
                        # Parse message data
                        data = json.loads(msg.data())

                        # Handle the update
                        asyncio.create_task(self._handle_task_update(data))

                    except Exception as e:
                        logger.error(
                            "Error processing Kafka message",
                            error=str(e),
                            exc_info=True
                        )

        except Exception as e:
            logger.error("Dapr subscribe error", error=str(e), exc_info=True)

    async def _handle_task_update(self, event_data: dict):
        """
        Handle a task update event from Kafka.

        Args:
            event_data: The event payload from Kafka
        """
        try:
            event_type = event_data.get("event_type", "")
            payload = event_data.get("payload", {})
            user_id = payload.get("user_id")
            task_id = payload.get("task_id")

            if not user_id or not task_id:
                logger.warning("Missing user_id or task_id in event", event_data=event_data)
                return

            # Determine update type
            update_type = event_type.replace("task.", "")

            # Fetch full task data from database
            db: Session = next(get_db())
            try:
                task = db.query(Task).filter(Task.id == task_id).first()

                if not task:
                    logger.debug("Task not found, may have been deleted", task_id=task_id)
                    task_data = payload  # Use event data if task not found
                else:
                    task_data = task.to_dict()

                # Broadcast to user's WebSocket connections
                await self.websocket_manager.broadcast_task_update(
                    user_id=user_id,
                    update_type=update_type,
                    task_data=task_data
                )

                logger.info(
                    "Task update broadcast to WebSocket",
                    user_id=user_id,
                    task_id=task_id,
                    update_type=update_type
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(
                "Failed to handle task update",
                error=str(e),
                exc_info=True
            )

    async def broadcast_direct(
        self,
        user_id: str,
        update_type: str,
        task_data: dict
    ):
        """
        Direct broadcast method (for testing or manual triggering).

        Args:
            user_id: ID of the user
            update_type: Type of update (created, updated, completed, deleted)
            task_data: Task data to broadcast
        """
        await self.websocket_manager.broadcast_task_update(
            user_id=user_id,
            update_type=update_type,
            task_data=task_data
        )


# Global broadcaster instance
_broadcaster: Optional[WebSocketBroadcaster] = None


def get_websocket_broadcaster() -> WebSocketBroadcaster:
    """Get the global WebSocket broadcaster instance."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = WebSocketBroadcaster()
    return _broadcaster


async def start_broadcaster():
    """Start the global WebSocket broadcaster."""
    broadcaster = get_websocket_broadcaster()
    await broadcaster.start()
    logger.info("WebSocket broadcaster started")


async def stop_broadcaster():
    """Stop the global WebSocket broadcaster."""
    global _broadcaster
    if _broadcaster:
        await _broadcaster.stop()
        logger.info("WebSocket broadcaster stopped")
