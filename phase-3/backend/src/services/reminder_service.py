"""
Background service to check and send task reminders.
"""
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.todo import Todo, Status
from src.models.user import User
from src.services.email_service import email_service


def check_and_send_reminders(session: Session) -> dict:
    """
    Check for tasks due in ~24 hours and send reminders.

    This function should be called hourly by the scheduler.
    It finds tasks that are:
    - Not completed
    - Have a due_date set
    - Due within the next 25 hours
    - Haven't had a reminder sent yet

    Args:
        session: Database session

    Returns:
        dict with count of reminders sent and errors
    """
    # Calculate time window: now to now+25 hours
    # This ensures we catch tasks due "tomorrow" when checking hourly
    now = datetime.utcnow()
    reminder_window_start = now
    reminder_window_end = now + timedelta(hours=25)

    print(f"🔍 Checking for tasks due between {reminder_window_start} and {reminder_window_end}")

    # Build query to find eligible tasks
    query = session.query(Todo, User).join(
        User, Todo.user_id == User.id
    ).filter(
        and_(
            Todo.status != Status.COMPLETED,        # Not completed
            Todo.due_date.isnot(None),              # Has due date
            Todo.due_date >= reminder_window_start, # Due in future
            Todo.due_date <= reminder_window_end,   # Due within 25 hours
            Todo.reminder_sent == False             # Reminder not sent yet
        )
    )

    results = query.all()
    sent_count = 0
    error_count = 0
    skipped_count = 0

    print(f"📋 Found {len(results)} tasks eligible for reminders")

    for todo, user in results:
        try:
            # Send reminder email with full task details
            success = email_service.send_reminder(
                to_email=user.email,
                task_title=todo.title,
                task_description=todo.description,
                due_date=todo.due_date,
                priority=todo.priority.value if todo.priority else None,
                tags=todo.tags,
                task_id=str(todo.id)
            )

            if success:
                # Mark reminder as sent
                todo.reminder_sent = True
                session.commit()
                sent_count += 1
                print(f"✅ Reminder sent for task '{todo.title}' to {user.email}")
            else:
                error_count += 1
                print(f"❌ Failed to send reminder for task '{todo.title}'")

        except Exception as e:
            print(f"❌ Error sending reminder for task {todo.id}: {e}")
            error_count += 1
            session.rollback()

    summary = {
        "checked": len(results),
        "sent": sent_count,
        "errors": error_count,
        "skipped": skipped_count
    }

    print(f"📊 Reminder check complete: {summary}")
    return summary


def send_test_reminder(session: Session, user_id: UUID) -> bool:
    """
    Send a test reminder to verify email configuration.

    Args:
        session: Database session
        user_id: User ID to send test email to

    Returns:
        bool: True if test email sent successfully
    """
    from src.models.user import User

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"User not found: {user_id}")
        return False

    test_due_date = datetime.utcnow() + timedelta(hours=24)

    return email_service.send_reminder(
        to_email=user.email,
        task_title="🧪 Test Task - Todo App Reminder",
        task_description="This is a test reminder email to verify your email configuration is working correctly!",
        due_date=test_due_date,
        priority="medium",
        tags=["test"],
        task_id="test-task-id"
    )
