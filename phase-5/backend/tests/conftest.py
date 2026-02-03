"""
Pytest Configuration and Fixtures
"""
import asyncio
import pytest
import os
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models import Base
from src.utils.config import settings


# Test database URL (use SQLite for tests or testcontainers)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
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


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high",
        "tags": ["test", "sample"],
        "due_date": "2026-02-05T17:00:00Z",
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
    }
