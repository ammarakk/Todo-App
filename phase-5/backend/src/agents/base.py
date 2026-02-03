"""
Base Skill Agent Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
import re
from datetime import datetime


class BaseSkillAgent(ABC):
    """Base class for all skill agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def extract(self, user_input: str) -> Dict[str, Any]:
        """Extract structured data from user input"""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate extracted data"""
        pass
    
    @abstractmethod
    def execute(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill with given data and context"""
        pass
    
    def format_response(self, success: bool, message: str, data: Any = None) -> Dict[str, Any]:
        """Format standardized response"""
        response = {
            "success": success,
            "message": message,
            "agent_used": self.name,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if data:
            response["data"] = data
        return response


class RegexExtractor:
    """Helper for regex-based extraction"""
    
    @staticmethod
    def extract_priority(text: str) -> str:
        """Extract priority from text"""
        priorities = {
            r"\b(urgent|asap|emergency)\b": "urgent",
            r"\b(high|important)\b": "high",
            r"\b(medium|normal)\b": "medium",
            r"\b(low|optional)\b": "low",
        }
        
        for pattern, priority in priorities.items():
            if re.search(pattern, text, re.IGNORECASE):
                return priority
        return "medium"
    
    @staticmethod
    def extract_tags(text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    @staticmethod
    def extract_task_id(text: str) -> str:
        """Extract task ID from text"""
        match = re.search(r'(?:task\s+)?[0-9a-f-]{36}', text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = re.search(r'task\s+(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""
