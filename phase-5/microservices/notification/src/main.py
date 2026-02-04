"""
Notification Microservice - Phase 5

Consumes reminder events from Kafka and sends email/push notifications.
Subscribes to "reminders" topic via Dapr Pub/Sub.
"""

import os
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

from src.utils.logging import get_logger

logger = get_logger(__name__)

# Configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_HOST = os.getenv("DAPR_HOST", "localhost")
BASE_URL = f"http://{DAPR_HOST}:{DAPR_HTTP_PORT}"
SUBSCRIPTION_PATH = "/reminders"  # Dapr will invoke this endpoint

app = FastAPI(
    title="Notification Service",
    description="Microservice for sending reminder notifications",
    version="1.0.0"
)

# Email service configuration
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@todo-app.local")


class ReminderEvent(BaseModel):
    """Reminder event from Kafka"""
    event_id: str
    event_type: str
    topic_name: str
    correlation_id: str
    timestamp: str
    source_service: str
    payload: Dict[str, Any]


class NotificationDelivery(BaseModel):
    """Notification delivery result"""
    reminder_id: str
    task_id: str
    status: str  # sent, failed, pending
    delivery_method: str  # email, push
    destination: str
    error_message: str = ""


async def send_email_notification(
    to: str,
    subject: str,
    body: str,
    task_data: Dict[str, Any]
) -> bool:
    """
    Send email notification using SendGrid (or mock).

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body (HTML)
        task_data: Task details for templating

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # For demo/development, we'll log the email
        logger.info(
            "sending_email",
            to=to,
            subject=subject,
            task_id=task_data.get("task_id"),
            task_title=task_data.get("title")
        )

        # If EMAIL_API_KEY is configured, use actual SendGrid
        if EMAIL_API_KEY and EMAIL_API_KEY != "SG.mock":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {EMAIL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [
                            {
                                "to": [{"email": to}],
                                "subject": subject
                            }
                        ],
                        "from": {"email": FROM_EMAIL},
                        "content": [
                            {
                                "type": "text/html",
                                "value": body
                            }
                        ]
                    },
                    timeout=10.0
                )

                if response.status_code in [200, 202]:
                    logger.info("email_sent_success", to=to, task_id=task_data.get("task_id"))
                    return True
                else:
                    logger.error(
                        "email_send_failed",
                        status=response.status_code,
                        response=response.text
                    )
                    return False
        else:
            # Mock mode - just log and return success
            logger.info("email_mock_mode", to=to, subject=subject)
            return True

    except Exception as e:
        logger.error("email_exception", error=str(e))
        return False


def format_reminder_email(task_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Format reminder email subject and body.

    Args:
        task_data: Task details

    Returns:
        Tuple of (subject, html_body)
    """
    title = task_data.get("title", "Task")
    due_date = task_data.get("due_date")
    description = task_data.get("description", "")

    subject = f"🔔 Reminder: {title}"

    html_body = f"""
    <html>
    <body>
        <h2>Task Reminder</h2>
        <p>You have a task due soon:</p>

        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
            <h3>{title}</h3>
            {f'<p><strong>Due:</strong> {due_date}</p>' if due_date else ''}
            {f'<p><strong>Description:</strong> {description}</p>' if description else ''}
        </div>

        <p>This is an automated reminder from your Todo App.</p>

        <hr>
        <p style="color: #666; font-size: 12px;">
            Reminder ID: {task_data.get('reminder_id')}<br>
            Task ID: {task_data.get('task_id')}
        </p>
    </body>
    </html>
    """

    return subject, html_body


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "notification-service",
        "status": "running",
        "version": "1.0.0",
        "dapr_port": DAPR_HTTP_PORT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check if email service is configured
    ready = bool(EMAIL_API_KEY) or EMAIL_API_KEY == "SG.mock"

    return {
        "status": "ready" if ready else "not_ready",
        "email_configured": ready,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post(SUBSCRIPTION_PATH)
async def handle_reminder_event(
    event_data: ReminderEvent,
    background_tasks: BackgroundTasks
):
    """
    Dapr Pub/Sub subscription endpoint for reminders topic.

    Automatically called by Dapr when a message is published to the "reminders" topic.

    Args:
        event_data: Reminder event from Kafka
        background_tasks: FastAPI background tasks

    Returns:
        Delivery confirmation
    """
    try:
        logger.info(
            "reminder_event_received",
            event_id=event_data.event_id,
            event_type=event_data.event_type,
            correlation_id=event_data.correlation_id
        )

        # Extract reminder details
        payload = event_data.payload
        reminder_id = payload.get("reminder_id")
        task_id = payload.get("task_id")
        trigger_time = payload.get("trigger_time")
        delivery_method = payload.get("delivery_method", "email")
        destination = payload.get("destination")

        if not all([reminder_id, task_id, destination]):
            logger.error(
                "invalid_reminder_event",
                payload_keys=list(payload.keys()),
                reminder_id=reminder_id,
                task_id=task_id
            )
            raise HTTPException(status_code=400, detail="Invalid reminder event")

        # Get task details for email formatting
        task_data = payload.get("task", {})
        task_data["reminder_id"] = reminder_id
        task_data["task_id"] = task_id

        # Send notification based on delivery method
        if delivery_method == "email":
            subject, body = format_reminder_email(task_data)

            # Send in background task
            background_tasks.add_task(
                send_email_and_log(
                    reminder_id=reminder_id,
                    task_id=task_id,
                    destination=destination,
                    subject=subject,
                    body=body,
                    task_data=task_data,
                    correlation_id=event_data.correlation_id
                )
            )
        else:
            logger.warning(
                "unsupported_delivery_method",
                method=delivery_method
            )

        return {
            "status": "processing",
            "reminder_id": reminder_id,
            "message": "Notification queued for delivery"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "handle_reminder_event_failed",
            error=str(e),
            event_id=event_data.event_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process reminder event: {str(e)}"
        )


async def send_email_and_log(
    reminder_id: str,
    task_id: str,
    destination: str,
    subject: str,
    body: str,
    task_data: Dict[str, Any],
    correlation_id: str
):
    """
    Send email and log delivery result.

    Args:
        reminder_id: Reminder ID
        task_id: Task ID
        destination: Email address
        subject: Email subject
        body: Email body
        task_data: Task details
        correlation_id: Correlation ID for tracing
    """
    # Send email
    success = await send_email_notification(destination, subject, body, task_data)

    # Log delivery result
    logger.info(
        "notification_delivery_complete",
        reminder_id=reminder_id,
        task_id=task_id,
        destination=destination,
        status="sent" if success else "failed",
        correlation_id=correlation_id
    )

    # TODO: Publish audit event to Kafka
    # await publish_audit_event(...)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "4000"))
    logger.info("starting_notification_service", port=port)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
