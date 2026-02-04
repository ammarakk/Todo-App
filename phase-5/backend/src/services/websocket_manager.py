"""
WebSocket Connection Manager - Phase 5
Manages real-time WebSocket connections for multi-client sync
"""

import json
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from uuid import UUID

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Features:
    - Track active connections per user
    - Broadcast updates to specific user's connections
    - Handle connection/disconnection gracefully
    - Support multiple devices per user
    """

    def __init__(self):
        # user_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> user_id mapping (for reverse lookup)
        self.connection_to_user: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept a new WebSocket connection and track it.

        Args:
            websocket: The WebSocket connection
            user_id: ID of the user connecting
        """
        await websocket.accept()

        # Add to user's connection set
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        self.connection_to_user[websocket] = user_id

        logger.info(
            "websocket_connected",
            user_id=user_id,
            total_connections_for_user=len(self.active_connections[user_id]),
            total_users=len(self.active_connections)
        )

        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Real-time sync activated",
            "user_id": user_id
        })

    async def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
        """
        user_id = self.connection_to_user.get(websocket)

        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            del self.connection_to_user[websocket]

            logger.info(
                "websocket_disconnected",
                user_id=user_id,
                remaining_connections=len(self.active_connections.get(user_id, []))
            )

    async def send_personal_message(self, message: dict, user_id: str):
        """
        Send a message to all connections for a specific user.

        Args:
            message: The message to send (will be JSON serialized)
            user_id: ID of the user to send to
        """
        if user_id not in self.active_connections:
            logger.debug("No active connections for user", user_id=user_id)
            return

        # Send to all of user's connected devices
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(
                    "failed_to_send_to_connection",
                    user_id=user_id,
                    error=str(e)
                )
                disconnected.add(connection)

        # Clean up disconnected sockets
        for connection in disconnected:
            await self.disconnect(connection)

        logger.info(
            "message_broadcast_to_user",
            user_id=user_id,
            recipient_count=len(self.active_connections.get(user_id, [])),
            message_type=message.get("type")
        )

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all connected users.

        Args:
            message: The message to broadcast
        """
        all_users = list(self.active_connections.keys())

        for user_id in all_users:
            await self.send_personal_message(message, user_id)

        logger.info(
            "message_broadcast_to_all",
            total_users=len(all_users),
            message_type=message.get("type")
        )

    async def broadcast_task_update(
        self,
        user_id: str,
        update_type: str,
        task_data: dict
    ):
        """
        Broadcast a task update to all of a user's connected devices.

        Args:
            user_id: ID of the user who owns the task
            update_type: Type of update (created, updated, completed, deleted)
            task_data: The task data
        """
        message = {
            "type": "task_update",
            "update_type": update_type,
            "data": task_data,
            "timestamp": asyncio.get_event_loop().time()
        }

        await self.send_personal_message(message, user_id)

    async def broadcast_reminder_created(
        self,
        user_id: str,
        reminder_data: dict
    ):
        """
        Broadcast a new reminder to all of a user's connected devices.

        Args:
            user_id: ID of the user who owns the reminder
            reminder_data: The reminder data
        """
        message = {
            "type": "reminder_created",
            "data": reminder_data,
            "timestamp": asyncio.get_event_loop().time()
        }

        await self.send_personal_message(message, user_id)

    def get_connection_count(self, user_id: Optional[str] = None) -> int:
        """
        Get the number of active connections.

        Args:
            user_id: If provided, get count for specific user only

        Returns:
            Number of active connections
        """
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(conns) for conns in self.active_connections.values())

    def get_connected_users(self) -> list[str]:
        """
        Get list of all connected user IDs.

        Returns:
            List of user IDs with active connections
        """
        return list(self.active_connections.keys())


# Global connection manager instance
manager: Optional[ConnectionManager] = None


def get_websocket_manager() -> ConnectionManager:
    """Get the global WebSocket connection manager instance."""
    global manager
    if manager is None:
        manager = ConnectionManager()
    return manager
