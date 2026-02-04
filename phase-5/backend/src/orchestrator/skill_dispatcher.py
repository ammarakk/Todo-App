"""
Skill Dispatcher Module - Phase 5

Dispatches user requests to appropriate AI skill agents.
Coordinates between multiple agents (Task, Reminder, Recurring, etc.)
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from .intent_detector import Intent
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SkillDispatcher:
    """
    Dispatches to appropriate skill agent based on intent.

    Each skill agent is a reusable AI module that extracts
    structured data from natural language input.
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize skill dispatcher.

        Args:
            prompts_dir: Directory containing agent prompt files
        """
        self.prompts_dir = prompts_dir or Path(__file__).parent.parent.parent / "agents" / "skills" / "prompts"

        # Lazy load agents (only when needed)
        self._task_agent = None
        self._reminder_agent = None
        self._recurring_agent = None

    async def dispatch(
        self,
        intent: Intent,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispatch to appropriate skill agent based on intent.

        Args:
            intent: Detected user intent
            user_input: Raw user input
            context: Additional context (user_id, conversation_id, etc.)

        Returns:
            Structured data from skill agent

        Raises:
            ValueError: If intent is unknown or agent fails
        """
        logger.info(
            "skill_dispatch",
            intent=intent.value,
            user_input_length=len(user_input)
        )

        if intent == Intent.CREATE_TASK:
            return await self._handle_create_task(user_input, context)

        elif intent == Intent.UPDATE_TASK:
            return await self._handle_update_task(user_input, context)

        elif intent == Intent.COMPLETE_TASK:
            return await self._handle_complete_task(user_input, context)

        elif intent == Intent.DELETE_TASK:
            return await self._handle_delete_task(user_input, context)

        elif intent == Intent.QUERY_TASKS:
            return await self._handle_query_tasks(user_input, context)

        elif intent == Intent.SET_REMINDER:
            return await self._handle_set_reminder(user_input, context)

        else:
            logger.warning("unknown_intent", intent=intent.value)
            return {
                "error": "Unknown intent",
                "intent": intent.value,
                "suggestion": "Could you please clarify what you'd like to do?"
            }

    async def _handle_create_task(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle task creation with Task Agent and optional Reminder Agent.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Structured task data with optional reminder
        """
        # Import TaskAgent here to avoid circular imports
        from src.agents.skills.task_agent import TaskAgent

        if self._task_agent is None:
            self._task_agent = TaskAgent(str(self.prompts_dir / "task_prompt.txt"))

        # Extract task data using Task Agent
        task_data = await self._task_agent.execute(user_input, context)

        # Check if user wants a reminder
        if "remind" in user_input.lower() or "reminder" in user_input.lower():
            from src.agents.skills.reminder_agent import ReminderAgent

            if self._reminder_agent is None:
                self._reminder_agent = ReminderAgent(str(self.prompts_dir / "reminder_prompt.txt"))

            reminder_data = await self._reminder_agent.execute(user_input, context)

            # Merge reminder data into task
            if reminder_data.get("confidence", 0) > 0.7:
                task_data["reminder_config"] = {
                    "lead_time": reminder_data.get("lead_time", "15m"),
                    "delivery_method": reminder_data.get("delivery_method", "email")
                }

        return task_data

    async def _handle_update_task(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle task update.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Structured update data
        """
        # Import TaskAgent for extracting update information
        from src.agents.skills.task_agent import TaskAgent

        if self._task_agent is None:
            self._task_agent = TaskAgent(str(self.prompts_dir / "task_prompt.txt"))

        # Extract update data
        update_data = await self._task_agent.execute(user_input, context)

        # Add metadata for update operation
        update_data["operation"] = "update"

        return update_data

    async def _handle_complete_task(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle task completion.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Task completion data
        """
        return {
            "operation": "complete",
            "confidence": 0.9,
            "user_input": user_input
        }

    async def _handle_delete_task(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle task deletion.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Task deletion data
        """
        return {
            "operation": "delete",
            "confidence": 0.9,
            "user_input": user_input
        }

    async def _handle_query_tasks(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle task query/list.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Query filters
        """
        # Extract filters from user input
        filters = {
            "operation": "query",
            "confidence": 0.8
        }

        user_input_lower = user_input.lower()

        # Filter by status
        if "completed" in user_input_lower or "done" in user_input_lower:
            filters["status"] = "completed"
        elif "active" in user_input_lower or "pending" in user_input_lower:
            filters["status"] = "active"

        # Filter by priority
        if "high priority" in user_input_lower:
            filters["priority"] = "high"
        elif "low priority" in user_input_lower:
            filters["priority"] = "low"

        # Filter by due date
        if "today" in user_input_lower:
            filters["due_today"] = True
        elif "overdue" in user_input_lower:
            filters["overdue"] = True

        return filters

    async def _handle_set_reminder(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle reminder creation.

        Args:
            user_input: User's natural language input
            context: Conversation context

        Returns:
            Reminder data
        """
        from src.agents.skills.reminder_agent import ReminderAgent

        if self._reminder_agent is None:
            self._reminder_agent = ReminderAgent(str(self.prompts_dir / "reminder_prompt.txt"))

        reminder_data = await self._reminder_agent.execute(user_input, context)

        return reminder_data
