"""
Contract Tests for AI Skill Agents
"""
import pytest
from typing import Dict, Any

from src.agents.task_agent import TaskAgent
from src.agents.reminder_agent import ReminderAgent


class TestTaskAgentContract:
    """Contract tests for Task Agent"""
    
    @pytest.fixture
    def task_agent(self):
        """Create task agent instance"""
        return TaskAgent()
    
    def test_extract_task_creation(self, task_agent):
        """Test extracting task creation from user input"""
        user_input = "Create a task to buy milk tomorrow at 5pm with high priority"
        
        result = task_agent.extract_task(user_input)
        
        assert isinstance(result, dict)
        assert "title" in result
        assert result["title"] == "buy milk"
        assert "priority" in result
        assert result["priority"] == "high"
    
    def test_extract_task_update(self, task_agent):
        """Test extracting task update from user input"""
        user_input = "Update task 123 to mark it as completed"
        
        result = task_agent.extract_task_update(user_input)
        
        assert isinstance(result, dict)
        assert "task_id" in result
        assert "status" in result
        assert result["status"] == "completed"
    
    def test_validate_task_data(self, task_agent):
        """Test task data validation"""
        valid_data = {
            "title": "Test Task",
            "priority": "high",
        }
        
        is_valid, errors = task_agent.validate(valid_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_invalid_task_data(self, task_agent):
        """Test invalid task data validation"""
        invalid_data = {
            "priority": "invalid_priority",
        }
        
        is_valid, errors = task_agent.validate(invalid_data)
        
        assert is_valid is False
        assert len(errors) > 0


class TestReminderAgentContract:
    """Contract tests for Reminder Agent"""
    
    @pytest.fixture
    def reminder_agent(self):
        """Create reminder agent instance"""
        return ReminderAgent()
    
    def test_extract_reminder_time(self, reminder_agent):
        """Test extracting reminder time from user input"""
        user_input = "Remind me to buy milk tomorrow at 5pm"
        
        result = reminder_agent.extract_reminder(user_input)
        
        assert isinstance(result, dict)
        assert "trigger_time" in result
        assert "destination" in result
    
    def test_validate_reminder_data(self, reminder_agent):
        """Test reminder data validation"""
        valid_data = {
            "task_id": "123",
            "trigger_time": "2026-02-05T17:00:00Z",
            "destination": "user@example.com",
        }
        
        is_valid, errors = reminder_agent.validate(valid_data)
        
        assert is_valid is True
        assert len(errors) == 0
