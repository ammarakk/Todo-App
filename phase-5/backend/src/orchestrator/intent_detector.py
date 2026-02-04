"""
Intent Detection Module - Phase 5

Detects user intent from natural language input using keyword matching
and confidence scoring. This is the first step in the orchestrator flow.
"""

from enum import Enum
from typing import Optional, Dict, Any
import re


class Intent(Enum):
    """User intent types for task management"""
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    QUERY_TASKS = "query_tasks"
    SET_REMINDER = "set_reminder"
    UNKNOWN = "unknown"


class IntentDetector:
    """
    Detects user intent from natural language input.

    Uses keyword matching with confidence scoring.
    In production, this could be enhanced with ML models.
    """

    def __init__(self):
        # Keywords for each intent with weights
        self.keywords = {
            Intent.CREATE_TASK: {
                "create": 1.0,
                "add": 0.9,
                "new task": 1.0,
                "make a task": 0.9,
                "add a task": 0.9,
                "task to": 0.7,
                "need to": 0.5
            },
            Intent.UPDATE_TASK: {
                "update": 1.0,
                "change": 0.9,
                "modify": 1.0,
                "edit": 0.8,
                "set": 0.6
            },
            Intent.COMPLETE_TASK: {
                "complete": 1.0,
                "done": 0.9,
                "finish": 0.9,
                "mark as done": 1.0,
                "mark as complete": 1.0,
                "finished": 0.8
            },
            Intent.DELETE_TASK: {
                "delete": 1.0,
                "remove": 0.9,
                "get rid of": 0.8,
                "cancel": 0.7
            },
            Intent.QUERY_TASKS: {
                "list": 1.0,
                "show": 0.9,
                "what are my": 1.0,
                "get my tasks": 1.0,
                "display": 0.8,
                "all tasks": 0.9
            },
            Intent.SET_REMINDER: {
                "remind": 1.0,
                "reminder": 1.0,
                "remind me": 1.0,
                "notify": 0.8,
                "alert": 0.7
            }
        }

    def detect(self, user_input: str) -> tuple[Intent, float]:
        """
        Detect intent from user input.

        Args:
            user_input: Natural language input from user

        Returns:
            Tuple of (Intent, confidence_score)
        """
        if not user_input:
            return Intent.UNKNOWN, 0.0

        user_input_lower = user_input.lower().strip()

        # Calculate scores for each intent
        scores = {}
        for intent, keywords in self.keywords.items():
            score = 0.0
            matches = 0

            for keyword, weight in keywords.items():
                if keyword in user_input_lower:
                    score += weight
                    matches += 1

            if matches > 0:
                # Normalize score by number of matches
                scores[intent] = score / matches

        if not scores:
            return Intent.UNKNOWN, 0.0

        # Get intent with highest score
        best_intent = max(scores.items(), key=lambda x: x[1])
        intent, score = best_intent

        # Apply confidence threshold
        # Single keyword match: confidence 0.6-0.8
        # Multiple matches: confidence 0.8-1.0
        confidence = min(score, 1.0)

        # If confidence is too low, mark as unknown
        if confidence < 0.5:
            return Intent.UNKNOWN, confidence

        return intent, confidence

    def detect_with_context(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[Intent, float, Dict[str, Any]]:
        """
        Detect intent with additional context.

        Args:
            user_input: Natural language input
            context: Additional context (conversation history, user state, etc.)

        Returns:
            Tuple of (Intent, confidence, metadata)
        """
        intent, confidence = self.detect(user_input)

        metadata = {
            "raw_input": user_input,
            "input_length": len(user_input),
            "context_provided": context is not None
        }

        # Extract potential task ID from input (for update/delete/complete)
        if intent in [Intent.UPDATE_TASK, Intent.DELETE_TASK, Intent.COMPLETE_TASK]:
            task_id = self._extract_task_id(user_input)
            if task_id:
                metadata["task_id"] = task_id

        return intent, confidence, metadata

    def _extract_task_id(self, user_input: str) -> Optional[str]:
        """
        Extract task ID from user input.

        Looks for patterns like "task #123" or "task 123"
        """
        # Pattern: "task #123" or "task 123"
        match = re.search(r'task\s*#?(\w+)', user_input.lower())
        if match:
            return match.group(1)

        # Pattern: "123" at start of input
        match = re.search(r'^(\w+)', user_input.strip())
        if match and len(match.group(1)) < 10:
            return match.group(1)

        return None
