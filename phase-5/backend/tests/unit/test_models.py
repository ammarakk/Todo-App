"""
Unit Tests for SQLAlchemy Models
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.models import User, Task, Reminder, Conversation, Message, Event, AuditLog


class TestUser:
    """Test User model"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            full_name="Test User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.created_at is not None
    
    def test_user_unique_email(self, db_session):
        """Test email uniqueness constraint"""
        user1 = User(email="test@example.com", full_name="User 1")
        user2 = User(email="test@example.com", full_name="User 2")
        
        db_session.add(user1)
        db_session.commit()
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.add(user2)
            db_session.commit()


class TestTask:
    """Test Task model"""
    
    def test_create_task(self, db_session, sample_user_data):
        """Test creating a task"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        task = Task(
            user_id=user.id,
            title="Test Task",
            priority="high",
            tags=["test", "sample"],
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.priority == "high"
        assert task.status == "active"
        assert task.tags == ["test", "sample"]
    
    def test_task_priority_constraint(self, db_session, sample_user_data):
        """Test priority constraint"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        with pytest.raises(Exception):
            task = Task(
                user_id=user.id,
                title="Test",
                priority="invalid",  # Invalid priority
            )
            db_session.add(task)
            db_session.commit()


class TestReminder:
    """Test Reminder model"""
    
    def test_create_reminder(self, db_session, sample_user_data):
        """Test creating a reminder"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        task = Task(
            user_id=user.id,
            title="Test Task",
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        reminder = Reminder(
            task_id=task.id,
            trigger_time=datetime.now(),
            delivery_method="email",
            destination="user@example.com",
        )
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)
        
        assert reminder.id is not None
        assert reminder.task_id == task.id
        assert reminder.status == "pending"
        assert reminder.retry_count == 0
