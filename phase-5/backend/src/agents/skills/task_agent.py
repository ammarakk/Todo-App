"""
Task Agent - Phase 5

AI skill agent for extracting task data from natural language.
Uses Ollama to run local LLM for structured extraction.
"""

import json
from typing import Dict, Any
from pathlib import Path

try:
    from ollama import Client as OllamaClient
except ImportError:
    OllamaClient = None

from src.utils.logging import get_logger

logger = get_logger(__name__)


class TaskAgent:
    """
    Extracts structured task data from natural language input.

    This agent is reusable across any todo application.
    It takes natural language input and returns structured JSON.
    """

    def __init__(self, prompt_path: str, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Task Agent.

        Args:
            prompt_path: Path to task prompt file
            ollama_url: URL for Ollama service
        """
        self.prompt_path = Path(prompt_path)
        self.ollama_url = ollama_url

        # Load system prompt
        if self.prompt_path.exists():
            self.prompt = self.prompt_path.read_text()
        else:
            # Fallback default prompt
            self.prompt = self._get_default_prompt()

        # Initialize Ollama client if available
        if OllamaClient:
            self.ollama = OllamaClient(host=ollama_url)
        else:
            self.ollama = None
            logger.warning("ollama_not_available", using_fallback=True)

    async def execute(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract task data from natural language input.

        Args:
            input_text: User's natural language input
            context: Additional context (user_id, conversation_id, etc.)

        Returns:
            Structured JSON with task data:
            {
                "title": "task title",
                "description": "description (optional)",
                "due_date": "ISO 8601 datetime (optional)",
                "priority": "low|medium|high",
                "tags": ["tag1", "tag2"],
                "confidence": 0.0-1.0
            }
        """
        logger.info(
            "task_agent_execute",
            input_length=len(input_text),
            context_keys=list(context.keys())
        )

        # Build full prompt
        full_prompt = f"""
{self.prompt}

User Input: {input_text}
Context: {json.dumps(context, indent=2)}

Extract task data and return ONLY JSON (no markdown, no explanation).
"""

        # Try Ollama first
        if self.ollama:
            try:
                response = self.ollama.generate(
                    model='llama2',  # Or 'qwen2' if available
                    prompt=full_prompt,
                    stream=False
                )

                result_text = response.get('response', '')

                # Parse JSON response
                result = self._parse_json_result(result_text, input_text)

                logger.info(
                    "task_agent_success",
                    title=result.get("title"),
                    confidence=result.get("confidence")
                )

                return result

            except Exception as e:
                logger.error(
                    "task_agent_ollama_failed",
                    error=str(e),
                    falling_back=True
                )

        # Fallback: Rule-based extraction
        return self._fallback_extraction(input_text)

    def _parse_json_result(self, result_text: str, input_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response with fallback.

        Args:
            result_text: Raw response from LLM
            input_text: Original user input for fallback

        Returns:
            Parsed and validated task data
        """
        try:
            # Try to parse JSON directly
            result = json.loads(result_text.strip())

            # Validate required fields
            if "title" not in result:
                raise ValueError("Missing required field: title")

            # Set defaults for optional fields
            result.setdefault("description", None)
            result.setdefault("due_date", None)
            result.setdefault("priority", "medium")
            result.setdefault("tags", [])
            result.setdefault("confidence", 0.95)

            # Validate priority
            if result["priority"] not in ["low", "medium", "high"]:
                result["priority"] = "medium"

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "task_agent_json_parse_failed",
                error=str(e),
                using_fallback=True
            )
            return self._fallback_extraction(input_text)

    def _fallback_extraction(self, input_text: str) -> Dict[str, Any]:
        """
        Fallback rule-based extraction when LLM is unavailable.

        Args:
            input_text: User's natural language input

        Returns:
            Structured task data with lower confidence
        """
        import re
        from datetime import datetime, timedelta

        # Extract title (first sentence or entire input)
        title = input_text.split('.')[0].split('!')[0].split('?')[0].strip()
        if len(title) > 100:
            title = title[:100] + "..."

        # Extract priority
        priority = "medium"
        if "high priority" in input_text.lower() or "urgent" in input_text.lower():
            priority = "high"
        elif "low priority" in input_text.lower():
            priority = "low"

        # Extract due date (simple patterns)
        due_date = None
        if "tomorrow" in input_text.lower():
            due_date = (datetime.now() + timedelta(days=1)).isoformat()
        elif "today" in input_text.lower():
            due_date = datetime.now().isoformat()

        # Extract tags (words starting with #)
        tags = re.findall(r'#(\w+)', input_text)

        return {
            "title": title,
            "description": input_text if len(input_text) > len(title) else None,
            "due_date": due_date,
            "priority": priority,
            "tags": tags,
            "confidence": 0.6  # Lower confidence for fallback
        }

    def _get_default_prompt(self) -> str:
        """
        Get default system prompt for task extraction.

        Returns:
            Default prompt text
        """
        return """You are a Task Extraction Agent. Extract task data from user input.

Return ONLY JSON in this format:
{
  "title": "task title",
  "description": "description (optional)",
  "due_date": "ISO 8601 datetime (optional)",
  "priority": "low|medium|high",
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0
}

Rules:
- If missing information, set field to null and confidence < 0.7
- Extract relative times (e.g., "tomorrow at 5pm") to ISO 8601
- Default priority to "medium" if not specified
- Tags are optional array
- Title is required

Examples:
User: "Create a task to call mom on Sunday at 3pm"
Output: {"title": "call mom", "due_date": "2026-02-09T15:00:00Z", "priority": "medium", "tags": [], "confidence": 0.95}

User: "Buy milk"
Output: {"title": "Buy milk", "due_date": null, "priority": "medium", "tags": [], "confidence": 0.7}
"""
