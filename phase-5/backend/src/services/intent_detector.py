"""
Intent Detection Service
"""
from typing import Dict, Any, Optional
from src.agents import TaskAgent, ReminderAgent
from src.utils.logging import get_logger

logger = get_logger(__name__)


class IntentDetector:
    """Detect user intent and route to appropriate skill agent"""
    
    def __init__(self):
        self.task_agent = TaskAgent()
        self.reminder_agent = ReminderAgent()
        
        self.agent_registry = {
            "task": self.task_agent,
            "reminder": self.reminder_agent,
        }
    
    def detect(self, user_input: str) -> Dict[str, Any]:
        """
        Detect user intent and extract structured data
        
        Returns:
            {
                "intent": str,
                "agent": str,
                "confidence": float,
                "data": dict,
                "requires_clarification": bool,
                "missing_fields": list,
            }
        """
        logger.info("detecting_intent", user_input=user_input[:100])
        
        # First, determine which agent to use
        agent_name = self._determine_agent(user_input)
        agent = self.agent_registry.get(agent_name)
        
        if not agent:
            return self._unknown_intent_response(user_input)
        
        # Extract data using the agent
        extracted_data = agent.extract(user_input)
        
        # Validate extracted data
        is_valid, errors = agent.validate(extracted_data)
        
        # Build response
        response = {
            "intent": extracted_data.get("intent", "unknown"),
            "agent": agent_name,
            "confidence": self._calculate_confidence(user_input, extracted_data),
            "data": extracted_data,
            "requires_clarification": not is_valid,
            "missing_fields": errors if not is_valid else [],
        }
        
        logger.info(
            "intent_detected",
            intent=response["intent"],
            agent=response["agent"],
            confidence=response["confidence"],
            requires_clarification=response["requires_clarification"],
        )
        
        return response
    
    def _determine_agent(self, user_input: str) -> Optional[str]:
        """Determine which agent should handle the request"""
        import re
        
        # Reminder-specific patterns
        reminder_patterns = [
            r"\bremind\b",
            r"\breminder\b",
            r"\bnotify\b",
            r"\balert\b",
        ]
        
        # Task-specific patterns
        task_patterns = [
            r"\btask\b",
            r"\btodo\b",
            r"\bcreate\b",
            r"\badd\b",
            r"\bcomplete\b",
            r"\bfinish\b",
            r"\bdelete\b",
            r"\bremove\b",
            r"\bupdate\b",
            r"\bchange\b",
            r"\bedit\b",
            r"\blist\b",
            r"\bshow\b",
        ]
        
        # Check reminder patterns first (more specific)
        for pattern in reminder_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return "reminder"
        
        # Check task patterns
        for pattern in task_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return "task"
        
        # Default to task agent (most common)
        return "task"
    
    def _calculate_confidence(self, user_input: str, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for intent detection"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if intent is clear
        if extracted_data.get("intent") != "unknown":
            confidence += 0.2
        
        # Increase confidence if we extracted useful data
        if extracted_data.get("title"):
            confidence += 0.15
        
        if extracted_data.get("task_id"):
            confidence += 0.15
        
        # Check for key phrases
        key_phrases = ["create", "update", "delete", "complete", "remind", "notify"]
        for phrase in key_phrases:
            if phrase in user_input.lower():
                confidence += 0.05
                break
        
        return min(confidence, 1.0)
    
    def _unknown_intent_response(self, user_input: str) -> Dict[str, Any]:
        """Return response for unknown intents"""
        return {
            "intent": "unknown",
            "agent": None,
            "confidence": 0.0,
            "data": {"raw_input": user_input},
            "requires_clarification": True,
            "missing_fields": ["Could not understand your request"],
        }
