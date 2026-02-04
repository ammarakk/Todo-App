"""
Performance Tests - Phase 5
Verifies SLA compliance for API, AI, and database operations
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from time import perf_counter
from uuid import uuid4
from fastapi.testclient import TestClient

from src.main import app
from src.orchestrator.intent_detector import IntentDetector
from src.orchestrator.skill_dispatcher import SkillDispatcher
from src.orchestrator.event_publisher import EventPublisher
from src.services.recurring_task_service import RecurringTaskService
from src.db.session import get_db
from src.models.task import Task
from src.models.user import User


class TestAPIPerformance:
    """Performance tests for API endpoints"""

    @pytest.fixture
    def db_session(self):
        return next(get_db())

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=uuid4(),
            email="perf@example.com",
            name="Performance User",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.mark.performance
    def test_create_task_response_time(self, test_user):
        """Test: POST /api/tasks completes in <200ms"""
        client = TestClient(app)

        start = perf_counter()
        response = client.post(
            f"/api/tasks?user_id={test_user.id}",
            json={
                "title": "Performance Test Task",
                "priority": "high",
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
        )
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response.status_code == 201
        assert duration_ms < 200, f"Response time {duration_ms}ms exceeds 200ms SLA"

    @pytest.mark.performance
    def test_get_task_response_time(self, test_user, db_session):
        """Test: GET /api/tasks/{id} completes in <100ms"""
        # Create a task first
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Get Test Task",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        client = TestClient(app)

        start = perf_counter()
        response = client.get(f"/api/tasks/{task.id}?user_id={test_user.id}")
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response.status_code == 200
        assert duration_ms < 100, f"Response time {duration_ms}ms exceeds 100ms SLA"

    @pytest.mark.performance
    def test_list_tasks_response_time(self, test_user):
        """Test: GET /api/tasks completes in <150ms"""
        client = TestClient(app)

        start = perf_counter()
        response = client.get(f"/api/tasks?user_id={test_user.id}")
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response.status_code == 200
        assert duration_ms < 150, f"Response time {duration_ms}ms exceeds 150ms SLA"

    @pytest.mark.performance
    def test_update_task_response_time(self, test_user, db_session):
        """Test: PATCH /api/tasks/{id} completes in <150ms"""
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Update Test Task",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        client = TestClient(app)

        start = perf_counter()
        response = client.patch(
            f"/api/tasks/{task.id}?user_id={test_user.id}",
            json={"title": "Updated Title"}
        )
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response.status_code == 200
        assert duration_ms < 150, f"Response time {duration_ms}ms exceeds 150ms SLA"

    @pytest.mark.performance
    def test_health_check_response_time(self):
        """Test: GET /health completes in <50ms"""
        client = TestClient(app)

        start = perf_counter()
        response = client.get("/health")
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response.status_code == 200
        assert duration_ms < 50, f"Response time {duration_ms}ms exceeds 50ms SLA"


class TestAIPerformance:
    """Performance tests for AI operations"""

    @pytest.mark.performance
    def test_intent_detection_latency(self):
        """Test: Intent detection completes in <500ms"""
        detector = IntentDetector()

        test_inputs = [
            "Create a task to buy milk tomorrow",
            "Remind me about my meeting at 3pm",
            "Show me my high priority tasks",
            "Complete the task about documentation",
            "Delete all completed tasks"
        ]

        latencies = []
        for user_input in test_inputs:
            start = perf_counter()
            intent, confidence = detector.detect(user_input)
            end = perf_counter()

            duration_ms = (end - start) * 1000
            latencies.append(duration_ms)

            assert intent is not None, f"Intent detection failed for: {user_input}"
            assert duration_ms < 500, f"Intent detection {duration_ms}ms exceeds 500ms SLA"

        # Verify average latency
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 300, f"Average latency {avg_latency}ms too high"

    @pytest.mark.performance
    def test_skill_dispatch_latency(self):
        """Test: Skill dispatch completes in <1000ms"""
        dispatcher = SkillDispatcher()
        detector = IntentDetector()

        user_input = "Create a high priority task to call mom tomorrow at 5pm"
        intent, confidence = detector.detect(user_input)

        start = perf_counter()
        result = asyncio.run(dispatcher.dispatch(
            intent=intent,
            user_input=user_input,
            context={"user_id": "test-user"}
        ))
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert result is not None
        assert "title" in result
        assert duration_ms < 1000, f"Skill dispatch {duration_ms}ms exceeds 1000ms SLA"

    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires Ollama service")
    def test_ollama_inference_latency(self):
        """Test: Ollama inference completes in <2s"""
        # This test requires actual Ollama service
        # Skip in CI/CD, run manually for performance verification
        import ollama

        start = perf_counter()
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': 'Extract task: Create a task to buy milk'}]
        )
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert response is not None
        assert duration_ms < 2000, f"Ollama inference {duration_ms}ms exceeds 2000ms SLA"


class TestDatabasePerformance:
    """Performance tests for database operations"""

    @pytest.fixture
    def db_session(self):
        return next(get_db())

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=uuid4(),
            email="db-perf@example.com",
            name="DB Performance User",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.mark.performance
    def test_create_task_query_time(self, test_user, db_session):
        """Test: Task creation query completes in <50ms"""
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="DB Performance Task",
            status="active"
        )

        start = perf_counter()
        db_session.add(task)
        db_session.commit()
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert duration_ms < 50, f"Create query {duration_ms}ms exceeds 50ms SLA"

    @pytest.mark.performance
    def test_query_task_by_id_time(self, test_user, db_session):
        """Test: Query task by ID completes in <30ms"""
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Query Test Task",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        start = perf_counter()
        result = db_session.query(Task).filter(Task.id == task.id).first()
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert result is not None
        assert duration_ms < 30, f"Query {duration_ms}ms exceeds 30ms SLA"

    @pytest.mark.performance
    def test_list_user_tasks_query_time(self, test_user, db_session):
        """Test: List user tasks query completes in <50ms"""
        # Create multiple tasks
        for i in range(10):
            task = Task(
                id=uuid4(),
                user_id=test_user.id,
                title=f"Task {i}",
                status="active"
            )
            db_session.add(task)
        db_session.commit()

        start = perf_counter()
        results = db_session.query(Task).filter(Task.user_id == test_user.id).all()
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert len(results) == 10
        assert duration_ms < 50, f"List query {duration_ms}ms exceeds 50ms SLA"

    @pytest.mark.performance
    def test_update_task_query_time(self, test_user, db_session):
        """Test: Update task query completes in <50ms"""
        task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Update Test",
            status="active"
        )
        db_session.add(task)
        db_session.commit()

        start = perf_counter()
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db_session.commit()
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert duration_ms < 50, f"Update query {duration_ms}ms exceeds 50ms SLA"


class TestEventPublishingPerformance:
    """Performance tests for event publishing"""

    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires Kafka service")
    def test_task_event_publishing_latency(self):
        """Test: Task event publishing completes in <100ms"""
        publisher = EventPublisher()

        start = perf_counter()
        success = asyncio.run(publisher.publish_task_event(
            event_type="task.created",
            task_id=str(uuid4()),
            payload={"title": "Performance Test", "status": "active"}
        ))
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert success is True
        assert duration_ms < 100, f"Event publishing {duration_ms}ms exceeds 100ms SLA"


class TestRecurringTaskPerformance:
    """Performance tests for recurring task generation"""

    @pytest.fixture
    def db_session(self):
        return next(get_db())

    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            id=uuid4(),
            email="recurring-perf@example.com",
            name="Recurring Performance User",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.mark.performance
    def test_recurring_task_generation_time(self, test_user, db_session):
        """Test: Recurring task generation completes in <500ms"""
        service = RecurringTaskService()

        # Create completed task
        completed_task = Task(
            id=uuid4(),
            user_id=test_user.id,
            title="Weekly Sync",
            due_date=datetime.utcnow(),
            status="completed",
            completed_at=datetime.utcnow()
        )
        db_session.add(completed_task)

        # Create recurring config
        from src.models.recurring_task import RecurringTask as RecurringTaskModel
        recurring_config = RecurringTaskModel(
            id=uuid4(),
            user_id=test_user.id,
            template_task_id=completed_task.id,
            pattern="weekly",
            interval=1,
            next_due_date=datetime.utcnow() + timedelta(weeks=1),
            occurrences_generated=1,
            status="active"
        )
        db_session.add(recurring_config)
        db_session.commit()

        start = perf_counter()
        result = asyncio.run(service.handle_task_completed(
            task_id=str(completed_task.id),
            user_id=str(test_user.id),
            db=db_session
        ))
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert result is not None
        assert result["occurrence_number"] == 2
        assert duration_ms < 500, f"Recurring task generation {duration_ms}ms exceeds 500ms SLA"


class TestConcurrentPerformance:
    """Performance tests for concurrent operations"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_intent_detection(self):
        """Test: 10 concurrent intent detections complete in <2s"""
        detector = IntentDetector()

        async def detect_intent():
            return detector.detect("Create a task to buy groceries")

        start = perf_counter()
        results = await asyncio.gather(*[detect_intent() for _ in range(10)])
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert len(results) == 10
        assert all(intent is not None for intent, _ in results)
        assert duration_ms < 2000, f"Concurrent detections {duration_ms}ms exceeds 2000ms SLA"

    @pytest.mark.performance
    def test_concurrent_api_requests(self):
        """Test: 10 concurrent API requests complete in <1s"""
        import threading

        client = TestClient(app)
        results = []
        errors = []

        def make_request():
            try:
                start = perf_counter()
                response = client.get("/health")
                end = perf_counter()
                results.append((end - start) * 1000)
                assert response.status_code == 200
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=make_request) for _ in range(10)]

        start = perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        end = perf_counter()

        duration_ms = (end - start) * 1000

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert duration_ms < 1000, f"Concurrent requests {duration_ms}ms exceeds 1000ms SLA"


class TestMemoryAndResourcePerformance:
    """Performance tests for memory and resource usage"""

    @pytest.mark.performance
    def test_memory_leak_detection(self):
        """Test: No significant memory leak after 100 operations"""
        import gc
        import sys

        detector = IntentDetector()

        # Force garbage collection
        gc.collect()

        # Get initial memory
        initial_objects = len(gc.get_objects())

        # Perform 100 operations
        for _ in range(100):
            intent, confidence = detector.detect("Create a test task")

        # Force garbage collection again
        gc.collect()

        # Get final memory
        final_objects = len(gc.get_objects())

        # Memory growth should be minimal (< 1000 objects)
        memory_growth = final_objects - initial_objects
        assert memory_growth < 1000, f"Potential memory leak: {memory_growth} objects grown"
