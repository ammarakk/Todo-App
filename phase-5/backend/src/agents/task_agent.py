"""
Task Agent - Handles task creation, updates, and queries
"""
from typing import Dict, Any, Tuple, List
import re
from datetime import datetime, timedelta

from .base import BaseSkillAgent, RegexExtractor


class TaskAgent(BaseSkillAgent):
    """AI agent for task management operations"""
    
    # Intent patterns
    INTENT_PATTERNS = {
        "create": [
            r"create\s+(?:a\s+)?task",
            r"add\s+(?:a\s+)?task",
            r"new\s+task",
            r"make\s+(?:a\s+)?task",
            r"remind\s+me\s+to",  # Overlaps with reminders
        ],
        "update": [
            r"update\s+(?:the\s+)?task",
            r"change\s+(?:the\s+)?task",
            r"modify\s+(?:the\s+)?task",
            r"edit\s+(?:the\s+)?task",
        ],
        "complete": [
            r"complete\s+(?:the\s+)?task",
            r"finish\s+(?:the\s+)?task",
            r"done\s+with\s+(?:the\s+)?task",
            r"mark\s+(?:the\s+)?task\s+(?:as\s+)?complete",
        ],
        "delete": [
            r"delete\s+(?:the\s+)?task",
            r"remove\s+(?:the\s+)?task",
        ],
        "list": [
            r"list\s+(?:all\s+)?task",
            r"show\s+(?:all\s+)?task",
            r"what\s+task",
            r"my\s+task",
        ],
    }
    
    def __init__(self):
        super().__init__("TaskAgent")
    
    def extract(self, user_input: str) -> Dict[str, Any]:
        """Extract task data from user input"""
        # Detect intent
        intent = self._detect_intent(user_input)
        
        # Extract based on intent
        if intent == "create":
            return self._extract_task_creation(user_input)
        elif intent == "update":
            return self._extract_task_update(user_input)
        elif intent == "complete":
            return self._extract_task_completion(user_input)
        elif intent == "delete":
            return self._extract_task_deletion(user_input)
        elif intent == "list":
            return self._extract_task_list(user_input)
        
        return {"intent": "unknown", "raw_input": user_input}
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate task data"""
        errors = []
        
        # Title is required for creation
        if data.get("intent") == "create":
            if not data.get("title"):
                errors.append("Title is required")
        
        # Task ID is required for update/delete/complete
        if data.get("intent") in ["update", "delete", "complete"]:
            if not data.get("task_id"):
                errors.append("Task ID is required")
        
        # Validate priority
        if "priority" in data:
            valid_priorities = ["low", "medium", "high", "urgent"]
            if data["priority"] not in valid_priorities:
                errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")
        
        # Validate status
        if "status" in data:
            valid_statuses = ["active", "completed", "deleted"]
            if data["status"] not in valid_statuses:
                errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task operation (called by orchestrator)"""
        # This is a placeholder - actual execution happens in orchestrator
        # via database operations and Dapr events
        return {
            "agent": self.name,
            "operation": data.get("intent"),
            "data": data,
        }
    
    def _detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    return intent
        return "unknown"
    
    def _extract_task_creation(self, user_input: str) -> Dict[str, Any]:
        """Extract task creation data"""
        # Remove common phrases to isolate task title
        title = user_input
        for pattern in [
            r"create\s+(?:a\s+)?task\s+(?:to\s+)?(?:called\s+)?",
            r"add\s+(?:a\s+)?task\s+(?:to\s+)?",
            r"new\s+task\s+(?:called\s+)?",
            r"remind\s+me\s+to\s+",
        ]:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)
        
        # Clean up title
        title = title.strip().capitalize()
        
        return {
            "intent": "create",
            "title": title,
            "priority": RegexExtractor.extract_priority(user_input),
            "tags": RegexExtractor.extract_tags(user_input),
            "raw_input": user_input,
        }
    
    def _extract_task_update(self, user_input: str) -> Dict[str, Any]:
        """Extract task update data"""
        task_id = RegexExtractor.extract_task_id(user_input)
        
        # Extract what to update
        new_title = None
        new_priority = None
        
        # Check for priority change
        if "priority" in user_input.lower():
            new_priority = RegexExtractor.extract_priority(user_input)
        
        return {
            "intent": "update",
            "task_id": task_id,
            "priority": new_priority,
            "raw_input": user_input,
        }
    
    def _extract_task_completion(self, user_input: str) -> Dict[str, Any]:
        """Extract task completion data"""
        task_id = RegexExtractor.extract_task_id(user_input)
        
        return {
            "intent": "complete",
            "task_id": task_id,
            "status": "completed",
            "raw_input": user_input,
        }
    
    def _extract_task_deletion(self, user_input: str) -> Dict[str, Any]:
        """Extract task deletion data"""
        task_id = RegexExtractor.extract_task_id(user_input)
        
        return {
            "intent": "delete",
            "task_id": task_id,
            "raw_input": user_input,
        }
    
    def _extract_task_list(self, user_input: str) -> Dict[str, Any]:
        """Extract task list query"""
        # Extract filters
        filters = {}
        
        if "active" in user_input.lower():
            filters["status"] = "active"
        elif "completed" in user_input.lower():
            filters["status"] = "completed"
        
        if "high" in user_input.lower() or "urgent" in user_input.lower():
            filters["priority"] = "high"
        
        return {
            "intent": "list",
            "filters": filters,
            "raw_input": user_input,
        }
