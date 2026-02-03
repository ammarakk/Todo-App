"""
Reminder Agent - Handles reminder scheduling
"""
from typing import Dict, Any, Tuple, List
import re
from datetime import datetime, timedelta

from .base import BaseSkillAgent, RegexExtractor


class ReminderAgent(BaseSkillAgent):
    """AI agent for reminder management"""
    
    def __init__(self):
        super().__init__("ReminderAgent")
    
    def extract(self, user_input: str) -> Dict[str, Any]:
        """Extract reminder data from user input"""
        return {
            "intent": "create_reminder",
            "task_title": self._extract_task_title(user_input),
            "trigger_time": self._extract_time(user_input),
            "destination": self._extract_destination(user_input),
            "delivery_method": "email",
            "raw_input": user_input,
        }
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate reminder data"""
        errors = []
        
        if not data.get("task_title"):
            errors.append("Task title is required")
        
        if not data.get("trigger_time"):
            errors.append("Trigger time is required")
        
        if not data.get("destination"):
            errors.append("Destination (email/phone) is required")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reminder creation"""
        return {
            "agent": self.name,
            "operation": "create_reminder",
            "data": data,
        }
    
    def _extract_task_title(self, user_input: str) -> str:
        """Extract task title from reminder request"""
        # Remove reminder-related phrases
        title = user_input
        for pattern in [
            r"remind\s+me\s+to\s+",
            r"remind\s+me\s+(?:about\s+)?",
            r"set\s+(?:a\s+)?reminder\s+(?:to\s+)?",
            r"reminder\s+(?:to\s+)?",
        ]:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)
        
        # Remove time-related phrases
        title = re.sub(r"\s+(?:tomorrow|today|tonight|at\s+\d+|in\s+\d+\s+(?:minutes?|hours?|days?)).*$", "", title, flags=re.IGNORECASE)
        
        return title.strip().capitalize()
    
    def _extract_time(self, user_input: str) -> str:
        """Extract trigger time from user input"""
        now = datetime.now()
        
        # Tomorrow
        if "tomorrow" in user_input.lower():
            tomorrow = now + timedelta(days=1)
            # Look for specific time
            time_match = re.search(r"at\s+(\d+)(?::(\d+))?\s*(am|pm)?", user_input, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                if time_match.group(3) and time_match.group(3).lower() == "pm" and hour < 12:
                    hour += 12
                return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
        
        # Today/tonight
        if "today" in user_input.lower() or "tonight" in user_input.lower():
            time_match = re.search(r"at\s+(\d+)(?::(\d+))?\s*(am|pm)?", user_input, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                if time_match.group(3) and time_match.group(3).lower() == "pm" and hour < 12:
                    hour += 12
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()
        
        # In X minutes/hours/days
        match = re.search(r"in\s+(\d+)\s+(minutes?|hours?|days?)", user_input, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower()
            
            if unit.startswith("minute"):
                return (now + timedelta(minutes=value)).isoformat()
            elif unit.startswith("hour"):
                return (now + timedelta(hours=value)).isoformat()
            elif unit.startswith("day"):
                return (now + timedelta(days=value)).isoformat()
        
        # Default: tomorrow at 9 AM
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat()
    
    def _extract_destination(self, user_input: str) -> str:
        """Extract email/phone from user input or use default"""
        # Look for email pattern
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", user_input)
        if email_match:
            return email_match.group(0)
        
        # Look for phone number
        phone_match = re.search(r"\+?(\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", user_input)
        if phone_match:
            return phone_match.group(0)
        
        # Default (should be replaced with user's actual email from context)
        return "user@example.com"
