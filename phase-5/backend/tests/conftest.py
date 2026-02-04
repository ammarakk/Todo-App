"""
Pytest Configuration and Fixtures - Phase 5
Comprehensive test fixtures for unit, integration, and contract tests
"""
import asyncio
import pytest
import os
from typing import AsyncGenerator, Generator
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models import Base
from src.models.task import Task
from src.models.user import User
from src.models.reminder import Reminder
from src.models.recurring_task import RecurringTask
from src.db.session import get_db
from src.main import app


# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture(scope="function")
def db_session_sync() -> Generator[Session, None]:
    """Create synchronous test database session (for integration tests)"""
    engine = create_engine(
        TEST_SYNC_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session_sync: Session) -> User:
    """Create test user for integration tests"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password"
    )
    db_session_sync.add(user)
    db_session_sync.commit()
    return user


@pytest.fixture
def test_task(db_session_sync: Session, test_user: User) -> Task:
    """Create test task for integration tests"""
    task = Task(
        id=uuid4(),
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        due_date=datetime.utcnow() + timedelta(days=1),
        priority="high",
        status="active",
        tags=["test"]
    )
    db_session_sync.add(task)
    db_session_sync.commit()
    return task


@pytest.fixture
def test_reminder(db_session_sync: Session, test_task: Task, test_user: User) -> Reminder:
    """Create test reminder for integration tests"""
    reminder = Reminder(
        id=uuid4(),
        task_id=test_task.id,
        user_id=test_user.id,
        trigger_time=test_task.due_date - timedelta(minutes=15),
        status="pending",
        delivery_method="email",
        destination="user@example.com"
    )
    db_session_sync.add(reminder)
    db_session_sync.commit()
    return reminder


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "tags": ["test", "sample"],
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "name": "Test User",
    }


@pytest.fixture
def sample_reminder_data(test_task):
    """Sample reminder data for testing"""
    return {
        "task_id": str(test_task.id),
        "trigger_type": "before_15_min",
        "delivery_method": "email",
        "destination": "user@example.com"
    }


# Mock fixtures for external services

@pytest.fixture
def mock_kafka_publisher(monkeypatch):
    """Mock Kafka publisher for testing"""
    async def mock_publish(*args, **kwargs):
        return True

    from src.orchestrator import event_publisher
    monkeypatch.setattr(event_publisher.EventPublisher, "publish_task_event", mock_publish)
    monkeypatch.setattr(event_publisher.EventPublisher, "publish_task_update", mock_publish)
    monkeypatch.setattr(event_publisher.EventPublisher, "publish_user_action", mock_publish)

    return mock_publish


@pytest.fixture
def mock_ollama_client(monkeypatch):
    """Mock Ollama client for testing"""
    async def mock_chat(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.message = {
                    "content": '{"title": "Test Task", "priority": "high", "confidence": 0.9}'
                }
        return MockResponse()

    from src.agents.skills import task_agent
    monkeypatch.setattr(task_agent.TaskAgent, "extract_task_data", mock_chat)

    return mock_chat


@pytest.fixture
def mock_dapr_client(monkeypatch):
    """Mock Dapr client for testing"""
    class MockDaprClient:
        async def publish_event(self, *args, **kwargs):
            return True

        async def get_state(self, *args, **kwargs):
            return None

        async def save_state(self, *args, **kwargs):
            return True

    from src.services import reminder_scheduler
    monkeypatch.setattr(reminder_scheduler.ReminderScheduler, "_publish_to_kafka", lambda *args: asyncio.sleep(0))

    return MockDaprClient()


# Override database dependency for testing

@pytest.fixture
def client_override(db_session_sync: Session):
    """Override get_db dependency for testing"""
    def override_get_db():
        try:
            yield db_session_sync
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# Performance test fixtures

@pytest.fixture
def performance_thresholds():
    """Performance thresholds for SLA verification"""
    return {
        "intent_detection_ms": 500,
        "skill_dispatch_ms": 1000,
        "api_response_ms": 200,
        "db_query_ms": 50,
    }
