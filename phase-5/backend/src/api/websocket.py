"""
WebSocket API Endpoint - Phase 5
Real-time sync for multi-client updates
"""

import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.exceptions import HTTPException

from src.services.websocket_manager import get_websocket_manager
from src.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
manager = get_websocket_manager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(..., description="User ID for the connection")
):
    """
    WebSocket endpoint for real-time task updates.

    Connect to this endpoint to receive live updates when:
    - Tasks are created, updated, completed, or deleted
    - Reminders are created or triggered
    - Recurring tasks generate new occurrences

    Connection URL: ws://localhost:8000/ws?user_id=USER_ID

    Message Types Received by Client:
    - connected: Connection established
    - task_update: Task changed (created, updated, completed, deleted)
    - reminder_created: New reminder created
    - recurring_task_generated: New recurring task occurrence created

    Example client code:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws?user_id=USER_ID');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('Received:', message);

      if (message.type === 'task_update') {
        // Update UI with new task data
        if (message.update_type === 'created') {
          addTaskToUI(message.data);
        } else if (message.update_type === 'completed') {
          markTaskCompleted(message.data);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('Disconnected from real-time sync');
    };
    ```
    """
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("WebSocket connection rejected: missing user_id")
        return

    try:
        # Accept and track connection
        await manager.connect(websocket, user_id)

        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client (for keepalive/ping)
            try:
                data = await websocket.receive_text()

                # Parse client message
                try:
                    message = json.loads(data)

                    # Handle ping/pong for keepalive
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": message.get("timestamp")
                        })

                    # Handle client requests
                    elif message.get("type") == "subscribe":
                        # Client can filter what updates they want
                        # For now, we send everything
                        await websocket.send_json({
                            "type": "subscribed",
                            "message": "Subscribed to all updates"
                        })

                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received from WebSocket client", user_id=user_id)

            except WebSocketDisconnect:
                # Client disconnected normally
                logger.info("WebSocket disconnected by client", user_id=user_id)
                break

            except Exception as e:
                logger.error(
                    "WebSocket error",
                    user_id=user_id,
                    error=str(e),
                    exc_info=True
                )
                break

    except Exception as e:
        logger.error(
            "WebSocket connection error",
            user_id=user_id,
            error=str(e),
            exc_info=True
        )

    finally:
        # Clean up connection
        await manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics.

    Returns information about active WebSocket connections.
    """
    connected_users = manager.get_connected_users()

    return {
        "total_users_connected": len(connected_users),
        "total_connections": manager.get_connection_count(),
        "connected_users": connected_users,
        "status": "running"
    }


@router.post("/ws/broadcast")
async def test_broadcast(
    user_id: str,
    message: str,
    update_type: str = "test"
):
    """
    Test endpoint to broadcast a message to a user's connections.

    This is primarily for testing and demonstration purposes.
    In production, broadcasts are triggered by Kafka events.
    """
    await manager.send_personal_message({
        "type": "test",
        "update_type": update_type,
        "message": message,
        "timestamp": asyncio.get_event_loop().time()
    }, user_id)

    return {
        "status": "sent",
        "user_id": user_id,
        "message": message
    }


# Note: Need to import asyncio at the top
import asyncio
