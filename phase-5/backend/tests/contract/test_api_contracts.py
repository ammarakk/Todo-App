"""
Contract Tests for Task API Endpoints - Phase 5
Verifies API contracts and response schemas
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from uuid import uuid4
import json

from src.main import app
from src.db.session import get_db
from src.models.task import Task
from src.models.user import User

client = TestClient(app)


class TestTaskAPIContracts:
    """Contract tests for Task API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session):
        """Setup test user and tasks"""
        # Create test user
        user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        self.user_id = str(user.id)

    def test_create_task_contract(self):
        """Test POST /api/tasks contract"""
        response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "priority": "high",
                "tags": ["test", "contract"]
            }
        )

        # Verify status code
        assert response.status_code == 201

        # Verify response structure
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "active"
        assert "tags" in data
        assert isinstance(data["tags"], list)
        assert "created_at" in data
        assert "updated_at" in data

        # Verify data types
        assert isinstance(data["id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["priority"], str)
        assert isinstance(data["tags"], list)

    def test_create_task_validation_contract(self):
        """Test POST /api/tasks input validation"""
        # Missing required field
        response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={
                # title missing
                "priority": "high"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_get_task_contract(self):
        """Test GET /api/tasks/{id} contract"""
        # First create a task
        create_response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={"title": "Get Test Task"}
        )
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/api/tasks/{task_id}?user_id={self.user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Get Test Task"

    def test_get_task_not_found_contract(self):
        """Test GET /api/tasks/{id} with invalid ID"""
        fake_id = str(uuid4())
        response = client.get(f"/api/tasks/{fake_id}?user_id={self.user_id}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_list_tasks_contract(self):
        """Test GET /api/tasks contract"""
        response = client.get(f"/api/tasks?user_id={self.user_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Could be empty list or list of tasks

    def test_list_tasks_with_filters_contract(self):
        """Test GET /api/tasks with query parameters"""
        response = client.get(
            f"/api/tasks?user_id={self.user_id}&status=active&priority=high"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_task_contract(self):
        """Test PATCH /api/tasks/{id} contract"""
        # Create a task first
        create_response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={"title": "Update Test", "priority": "low"}
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = client.patch(
            f"/api/tasks/{task_id}?user_id={self.user_id}",
            json={
                "title": "Updated Title",
                "priority": "high"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "high"
        assert "updated_at" in data

    def test_complete_task_contract(self):
        """Test POST /api/tasks/{id}/complete contract"""
        # Create a task
        create_response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={"title": "Complete Test"}
        )
        task_id = create_response.json()["id"]

        # Complete the task
        response = client.post(f"/api/tasks/{task_id}/complete?user_id={self.user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "completed_at" in data

    def test_delete_task_contract(self):
        """Test DELETE /api/tasks/{id} contract"""
        # Create a task
        create_response = client.post(
            f"/api/tasks?user_id={self.user_id}",
            json={"title": "Delete Test"}
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}?user_id={self.user_id}")

        assert response.status_code == 204  # No content

        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}?user_id={self.user_id}")
        assert get_response.status_code == 404


class TestReminderAPIContracts:
    """Contract tests for Reminder API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session):
        """Setup test user and task"""
        user = User(
            id=uuid4(),
            email="reminder-test@example.com",
            name="Reminder Test User",
            password_hash="hashed_password"
        )
        db_session.add(user)

        task = Task(
            id=uuid4(),
            user_id=user.id,
            title="Task with Reminder",
            due_date=datetime.utcnow() + timedelta(hours=24),
            priority="medium"
        )
        db_session.add(task)
        db_session.commit()

        self.user_id = str(user.id)
        self.task_id = str(task.id)

    def test_create_reminder_contract(self):
        """Test POST /api/reminders contract"""
        response = client.post(
            f"/api/reminders?user_id={self.user_id}",
            json={
                "task_id": self.task_id,
                "trigger_type": "before_15_min",
                "delivery_method": "email",
                "destination": "user@example.com"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["task_id"] == self.task_id
        assert data["trigger_type"] == "before_15_min"
        assert data["status"] == "pending"
        assert "trigger_at" in data

    def test_create_reminder_validation_contract(self):
        """Test POST /api/reminders validation"""
        # Invalid trigger_type
        response = client.post(
            f"/api/reminders?user_id={self.user_id}",
            json={
                "task_id": self.task_id,
                "trigger_type": "invalid_type",
                "delivery_method": "email",
                "destination": "user@example.com"
            }
        )
        assert response.status_code == 422

    def test_list_reminders_contract(self):
        """Test GET /api/reminders contract"""
        response = client.get(f"/api/reminders?user_id={self.user_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_cancel_reminder_contract(self):
        """Test DELETE /api/reminders/{id} contract"""
        # Create a reminder first
        create_response = client.post(
            f"/api/reminders?user_id={self.user_id}",
            json={
                "task_id": self.task_id,
                "trigger_type": "before_15_min",
                "delivery_method": "email",
                "destination": "user@example.com"
            }
        )
        reminder_id = create_response.json()["id"]

        # Cancel the reminder
        response = client.delete(f"/api/reminders/{reminder_id}?user_id={self.user_id}")

        assert response.status_code == 204


class TestRecurringTaskAPIContracts:
    """Contract tests for Recurring Task API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session):
        """Setup test user and task"""
        user = User(
            id=uuid4(),
            email="recurring-test@example.com",
            name="Recurring Test User",
            password_hash="hashed_password"
        )
        db_session.add(user)

        task = Task(
            id=uuid4(),
            user_id=user.id,
            title="Weekly Meeting",
            due_date=datetime.utcnow() + timedelta(hours=24),
            priority="high"
        )
        db_session.add(task)
        db_session.commit()

        self.user_id = str(user.id)
        self.task_id = str(task.id)

    def test_create_recurring_task_contract(self):
        """Test POST /api/recurring-tasks contract"""
        response = client.post(
            f"/api/recurring-tasks?user_id={self.user_id}",
            json={
                "template_task_id": self.task_id,
                "pattern": "weekly",
                "interval": 1,
                "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["pattern"] == "weekly"
        assert data["interval"] == 1
        assert data["status"] == "active"
        assert "occurrences_generated" in data

    def test_list_recurring_tasks_contract(self):
        """Test GET /api/recurring-tasks contract"""
        response = client.get(f"/api/recurring-tasks?user_id={self.user_id}")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_update_recurring_task_contract(self):
        """Test PATCH /api/recurring-tasks/{id} contract"""
        # Create recurring task
        create_response = client.post(
            f"/api/recurring-tasks?user_id={self.user_id}",
            json={
                "template_task_id": self.task_id,
                "pattern": "weekly",
                "interval": 1
            }
        )
        recurring_id = create_response.json()["id"]

        # Pause the recurring task
        response = client.patch(
            f"/api/recurring-tasks/{recurring_id}?user_id={self.user_id}",
            json={"status": "paused"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"

    def test_cancel_recurring_task_contract(self):
        """Test DELETE /api/recurring-tasks/{id} contract"""
        # Create recurring task
        create_response = client.post(
            f"/api/recurring-tasks?user_id={self.user_id}",
            json={
                "template_task_id": self.task_id,
                "pattern": "daily",
                "interval": 1
            }
        )
        recurring_id = create_response.json()["id"]

        # Cancel it
        response = client.delete(f"/api/recurring-tasks/{recurring_id}?user_id={self.user_id}")

        assert response.status_code == 204


class TestHealthAPIContracts:
    """Contract tests for Health endpoints"""

    def test_health_check_contract(self):
        """Test GET /health contract"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data

    def test_readiness_check_contract(self):
        """Test GET /ready contract"""
        response = client.get("/ready")

        assert response.status_code in [200, 503]  # Ready or not ready
        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_metrics_endpoint_contract(self):
        """Test GET /metrics contract"""
        response = client.get("/metrics")

        # Prometheus metrics endpoint
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestChatOrchestratorContracts:
    """Contract tests for Chat Orchestrator endpoints"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db_session):
        """Setup test user"""
        user = User(
            id=uuid4(),
            email="chat-test@example.com",
            name="Chat Test User",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        self.user_id = str(user.id)

    def test_chat_command_contract(self):
        """Test POST /chat/command contract"""
        response = client.post(
            "/chat/command",
            json={
                "user_input": "Create a task to buy groceries",
                "user_id": self.user_id
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "intent_detected" in data
        assert "confidence_score" in data
        assert isinstance(data["confidence_score"], (int, float))

    def test_chat_command_with_context_contract(self):
        """Test POST /chat/command with conversation context"""
        response = client.post(
            "/chat/command",
            json={
                "user_input": "Set it to high priority",
                "user_id": self.user_id,
                "conversation_id": str(uuid4())
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
