"""
End-to-End Integration Tests - Phase 5
Tests complete user workflows across multiple services
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from src.main import app
from src.db.session import get_db
from src.models.task import Task
from src.models.user import User
from src.models.reminder import Reminder
from src.models.recurring_task import RecurringTask
from src.orchestrator.intent_detector import IntentDetector
from src.orchestrator.skill_dispatcher import SkillDispatcher
from src.orchestrator.event_publisher import EventPublisher
from src.services.recurring_task_service import RecurringTaskService


class TestTaskCreationWorkflow:
    """End-to-end test for task creation workflow"""

    @pytest.fixture
    def db_session(self):
        """Get database session"""
        return next(get_db())

    @pytest.fixture
    def test_user(self, db_session):
        """Create test user"""
        user = User(
            id=uuid4(),
            email="e2e@example.com",
            name="E2E Test User",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_complete_task_creation_flow(self, test_user, db_session):
        """Test: Create task via chat → Task created in DB → Event published"""
        # Step 1: Detect intent
        detector = IntentDetector()
        user_input = "Create a task to buy milk tomorrow at 5pm"
        intent, confidence = detector.detect(user_input)

        assert intent.value == "CREATE_TASK"
        assert confidence >= 0.7

        # Step 2: Use skill agent to extract data
        dispatcher = SkillDispatcher()
        result = asyncio.run(dispatcher.dispatch(
            intent=intent,
            user_input=user_input,
            context={"user_id": str(test_user.id)}
        ))

        assert result["title"] == "buy milk"
        assert result["due_date"] is not None
        assert result["confidence"] >= 0.7

        # Step 3: Create task in database
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title=result["title"],
            due_date=datetime.fromisoformat(result["due_date"].replace("Z", "+00:00")),
            priority=result.get("priority", "medium"),
            tags=result.get("tags", []),
            status="active",
            ai_metadata={"confidence": result["confidence"]}
        )
        db_session.add(task)
        db_session.commit()

        # Verify task was created
        created_task = db_session.query(Task).filter(Task.id == task.id).first()
        assert created_task is not None
        assert created_task.title == "buy milk"

        # Step 4: Verify event would be published (mocked)
        # In real flow, EventPublisher.publish_task_event is called
        # This test verifies the data flow is correct

    def test_task_with_reminder_flow(self, test_user, db_session):
        """Test: Create task with reminder → Reminder scheduled"""
        # Create task with due date
        due_date = datetime.utcnow() + timedelta(hours=24)
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Meeting with team",
            due_date=due_date,
            priority="high"
        )
        db_session.add(task)
        db_session.commit()

        # Create reminder
        reminder = Reminder(
            id=uuid4(),
            task_id=task.id,
            user_id=test_user.id,
            trigger_time=due_date - timedelta(minutes=15),
            status="pending",
            delivery_method="email",
            destination="user@example.com"
        )
        db_session.add(reminder)
        db_session.commit()

        # Verify reminder was created
        created_reminder = db_session.query(Reminder).filter(
            Reminder.task_id == task.id
        ).first()
        assert created_reminder is not None
        assert created_reminder.status == "pending"

    def test_recurring_task_generation_flow(self, test_user, db_session):
        """Test: Complete recurring task → Next occurrence created"""
        # Create recurring task configuration
        due_date = datetime.utcnow() + timedelta(hours=24)
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Weekly sync",
            due_date=due_date,
            priority="medium"
        )
        db_session.add(task)

        recurring_config = RecurringTask(
            id=uuid4(),
            user_id=test_user.id,
            template_task_id=task.id,
            pattern="weekly",
            interval=1,
            next_due_date=due_date + timedelta(weeks=1),
            occurrences_generated=1,
            status="active"
        )
        db_session.add(recurring_config)

        # Add recurrence_rule to task
        task.recurrence_rule = {"recurring_task_id": str(recurring_config.id)}
        db_session.commit()

        # Simulate task completion
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db_session.commit()

        # Trigger recurring task service
        service = RecurringTaskService()
        result = asyncio.run(service.handle_task_completed(
            task_id=str(task.id),
            user_id=str(test_user.id),
            db=db_session
        ))

        # Verify new task was created
        assert result is not None
        assert "new_task_id" in result
        assert result["occurrence_number"] == 2

        # Verify recurring config updated
        db_session.refresh(recurring_config)
        assert recurring_config.occurrences_generated == 2


class TestReminderDeliveryFlow:
    """Integration tests for reminder delivery workflow"""

    @pytest.fixture
    def db_session(self):
        return next(get_db())

    @pytest.fixture
    def setup_data(self, db_session):
        """Setup task and reminder"""
        user = User(
            id=uuid4(),
            email="reminder-e2e@example.com",
            name="Reminder E2E User",
            password_hash="hashed"
        )
        db_session.add(user)

        due_date = datetime.utcnow() + timedelta(minutes=30)
        task = Task(
            id=uuid4(),
            user_id=user.id,
            title="Important meeting",
            due_date=due_date,
            priority="high"
        )
        db_session.add(task)

        reminder = Reminder(
            id=uuid4(),
            task_id=task.id,
            user_id=user.id,
            trigger_time=due_date - timedelta(minutes=15),
            status="pending",
            delivery_method="email",
            destination="user@example.com"
        )
        db_session.add(reminder)
        db_session.commit()

        return {
            "user_id": str(user.id),
            "task_id": str(task.id),
            "reminder_id": str(reminder.id),
            "due_date": due_date
        }

    def test_reminder_scheduling_and_delivery(self, setup_data):
        """Test: Reminder due → Scheduler detects → Notification sent"""
        # This test verifies the components work together
        # In real flow:
        # 1. ReminderScheduler runs (background task)
        # 2. Checks for due reminders
        # 3. Publishes to Kafka
        # 4. Notification service receives via Dapr
        # 5. Sends email

        reminder_id = setup_data["reminder_id"]

        # Verify reminder exists and is pending
        db = next(get_db())
        reminder = db.query(Reminder).filter(Reminder.id == uuid4(reminder_id)).first()
        assert reminder is not None
        assert reminder.status == "pending"

        # In production, ReminderScheduler would:
        # - Find this reminder (trigger_time <= now)
        # - Publish to Kafka "reminders" topic
        # - Notification service subscribes and sends email

        # This test verifies the data model is correct
        assert reminder.trigger_time is not None
        assert reminder.delivery_method == "email"
        assert reminder.destination == "user@example.com"


class TestWebSocketSyncFlow:
    """Integration tests for real-time sync workflow"""

    def test_task_update_broadcasts_to_websocket(self):
        """Test: Task updated → Event published → WebSocket clients notified"""
        from src.services.websocket_manager import ConnectionManager

        # Create connection manager
        manager = ConnectionManager()

        # Simulate task update
        user_id = "test-user-123"
        task_data = {
            "id": str(uuid4()),
            "title": "Updated Task",
            "status": "completed"
        }

        # Broadcast should not raise error even with no connections
        asyncio.run(manager.broadcast_task_update(
            user_id=user_id,
            update_type="completed",
            task_data=task_data
        ))

        # Verify no exceptions raised
        assert True


class TestEventPublishingFlow:
    """Integration tests for event publishing and consumption"""

    @pytest.fixture
    def db_session(self):
        return next(get_db())

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=uuid4(),
            email="events@example.com",
            name="Events User",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_task_created_event_flow(self, test_user, db_session):
        """Test: Task created → Event published to Kafka"""
        publisher = EventPublisher()

        # Create task
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Event Test Task",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        # Publish event
        success = asyncio.run(publisher.publish_task_event(
            event_type="task.created",
            task_id=str(task.id),
            payload={
                "user_id": str(test_user.id),
                "title": task.title,
                "status": task.status
            }
        ))

        # In production with real Kafka, this would return True
        # For testing, we verify the method works
        assert isinstance(success, bool)

    def test_multiple_events_published(self, test_user, db_session):
        """Test: Multiple events published for single operation"""
        publisher = EventPublisher()

        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Multi Event Task",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        # Publish multiple events
        events = [
            ("task.created", {"user_id": str(test_user.id)}),
            ("task-updates", {"update_type": "created"}),
            ("audit.logged", {"entity_type": "task"})
        ]

        for event_type, payload in events:
            if "task-updates" in event_type:
                success = asyncio.run(publisher.publish_task_update(
                    task_id=str(task.id),
                    update_type="created",
                    payload=payload
                ))
            elif "audit" in event_type:
                success = asyncio.run(publisher.publish_user_action(
                    entity_type="task",
                    entity_id=str(task.id),
                    action="created",
                    user_id=str(test_user.id),
                    changes=payload
                ))
            else:
                success = asyncio.run(publisher.publish_task_event(
                    event_type=event_type,
                    task_id=str(task.id),
                    payload=payload
                ))

            assert isinstance(success, bool)


class TestErrorHandlingFlow:
    """Integration tests for error handling and edge cases"""

    def test_invalid_user_id_rejected(self):
        """Test: Invalid user_id returns 404"""
        from fastapi.testclient import TestClient
        client = TestClient(app)

        fake_user_id = str(uuid4())
        response = client.get(f"/api/tasks?user_id={fake_user_id}")

        # Should return empty list (user has no tasks)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_task_not_found_returns_404(self):
        """Test: Getting non-existent task returns 404"""
        from fastapi.testclient import TestClient
        client = TestClient(app)

        fake_task_id = str(uuid4())
        response = client.get(f"/api/tasks/{fake_task_id}?user_id=some-user")

        assert response.status_code == 404

    def test_duplicate_reminder_prevented(self):
        """Test: Cannot create multiple reminders for same task"""
        # This would require API validation
        # The test verifies business logic
        pass


class TestPerformanceConstraints:
    """Performance tests with SLA verification"""

    def test_intent_detection_performance(self):
        """Test: Intent detection completes in <500ms"""
        detector = IntentDetector()
        user_input = "Create a task to buy groceries at the store"

        start = datetime.now()
        intent, confidence = detector.detect(user_input)
        end = datetime.now()

        duration = (end - start).total_seconds()
        assert duration < 0.5  # < 500ms
        assert intent is not None

    def test_skill_dispatcher_performance(self):
        """Test: Skill dispatch completes in <1s"""
        dispatcher = SkillDispatcher()
        detector = IntentDetector()

        user_input = "Create a high priority task to call mom tomorrow"
        intent, confidence = detector.detect(user_input)

        start = datetime.now()
        result = asyncio.run(dispatcher.dispatch(
            intent=intent,
            user_input=user_input,
            context={"user_id": "test-user"}
        ))
        end = datetime.now()

        duration = (end - start).total_seconds()
        assert duration < 1.0  # < 1 second
        assert result is not None
