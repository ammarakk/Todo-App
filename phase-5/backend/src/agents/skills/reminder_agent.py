"""
Reminder Agent - Phase 5

AI skill agent for extracting reminder data from natural language.
Handles time/date extraction and delivery method preferences.
"""

import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta, timezone

try:
    from ollama import Client as OllamaClient
except ImportError:
    OllamaClient = None

from src.utils.logging import get_logger

logger = get_logger(__name__)


class ReminderAgent:
    """
    Extracts structured reminder data from natural language input.

    This agent handles time extraction, lead time calculation,
    and delivery method preferences.
    """

    def __init__(self, prompt_path: str, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Reminder Agent.

        Args:
            prompt_path: Path to reminder prompt file
            ollama_url: URL for Ollama service
        """
        self.prompt_path = Path(prompt_path)
        self.ollama_url = ollama_url

        # Load system prompt
        if self.prompt_path.exists():
            self.prompt = self.prompt_path.read_text()
        else:
            self.prompt = self._get_default_prompt()

        # Initialize Ollama client if available
        if OllamaClient:
            self.ollama = OllamaClient(host=ollama_url)
        else:
            self.ollama = None
            logger.warning("ollama_not_available", using_fallback=True)

    async def execute(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract reminder data from natural language input.

        Args:
            input_text: User's natural language input
            context: Additional context (user_id, task_id, etc.)

        Returns:
            Structured JSON with reminder data:
            {
                "trigger_time": "ISO 8601 datetime",
                "lead_time": "15m",
                "delivery_method": "email",
                "destination": "user@example.com",
                "confidence": 0.0-1.0
            }
        """
        logger.info(
            "reminder_agent_execute",
            input_length=len(input_text),
            context_keys=list(context.keys())
        )

        # Build full prompt
        full_prompt = f"""
{self.prompt}

User Input: {input_text}
Context: {json.dumps(context, indent=2)}
Current Time: {datetime.now(timezone.utc).isoformat()}

Extract reminder data and return ONLY JSON (no markdown, no explanation).
"""

        # Try Ollama first
        if self.ollama:
            try:
                response = self.ollama.generate(
                    model='llama2',
                    prompt=full_prompt,
                    stream=False
                )

                result_text = response.get('response', '')
                result = self._parse_json_result(result_text, input_text, context)

                logger.info(
                    "reminder_agent_success",
                    trigger_time=result.get("trigger_time"),
                    confidence=result.get("confidence")
                )

                return result

            except Exception as e:
                logger.error(
                    "reminder_agent_ollama_failed",
                    error=str(e),
                    falling_back=True
                )

        # Fallback: Rule-based extraction
        return self._fallback_extraction(input_text, context)

    def _parse_json_result(
        self,
        result_text: str,
        input_text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse JSON from LLM response with fallback."""
        try:
            result = json.loads(result_text.strip())

            # Validate required fields
            if "trigger_time" not in result:
                # Try to extract from input text
                result["trigger_time"] = self._extract_time_from_text(input_text)

            # Set defaults
            result.setdefault("lead_time", "15m")
            result.setdefault("delivery_method", "email")
            result.setdefault("destination", context.get("user_email", "user@example.com"))
            result.setdefault("confidence", 0.95)

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "reminder_agent_json_parse_failed",
                error=str(e),
                using_fallback=True
            )
            return self._fallback_extraction(input_text, context)

    def _fallback_extraction(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based extraction.

        Args:
            input_text: User's natural language input
            context: Additional context

        Returns:
            Structured reminder data
        """
        trigger_time = self._extract_time_from_text(input_text)

        # Extract lead time
        lead_time = "15m"  # Default
        lead_time_match = re.search(r'(\d+)\s*(m|min|minutes?)\s*(before|earlier)', input_text.lower())
        if lead_time_match:
            minutes = int(lead_time_match.group(1))
            lead_time = f"{minutes}m"

        # Extract delivery method
        delivery_method = "email"  # Default
        if "push" in input_text.lower() or "notification" in input_text.lower():
            delivery_method = "push"

        return {
            "trigger_time": trigger_time,
            "lead_time": lead_time,
            "delivery_method": delivery_method,
            "destination": context.get("user_email", "user@example.com"),
            "confidence": 0.7  # Lower confidence for fallback
        }

    def _extract_time_from_text(self, text: str) -> Optional[str]:
        """
        Extract time/date from text using regex patterns.

        Args:
            text: Input text

        Returns:
            ISO 8601 datetime string or None
        """
        text_lower = text.lower()
        now = datetime.now(timezone.utc)

        # Relative time patterns
        if "tomorrow" in text_lower:
            return (now + timedelta(days=1)).isoformat()
        elif "today" in text_lower:
            return now.isoformat()
        elif "next week" in text_lower:
            return (now + timedelta(weeks=1)).isoformat()

        # Time patterns: "at 5pm", "at 15:00", "5:00 PM"
        time_patterns = [
            r'at\s+(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'at\s+(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})\s*(am|pm)'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    if len(match.groups()) == 3:
                        hour, minute, period = match.groups()
                        hour = int(hour)
                        minute = int(minute)
                    else:
                        hour = int(match.group(1))
                        minute = 0
                        period = match.group(2) if len(match.groups()) > 1 else None

                    # Adjust for AM/PM
                    if period == "pm" and hour < 12:
                        hour += 12
                    elif period == "am" and hour == 12:
                        hour = 0

                    # Create datetime for today at that time
                    result = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    # If time has passed today, assume tomorrow
                    if result < now:
                        result += timedelta(days=1)

                    return result.isoformat()

                except (ValueError, IndexError):
                    continue

        # Default: tomorrow at 9 AM
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat()

    def _get_default_prompt(self) -> str:
        """Get default system prompt for reminder extraction."""
        return """You are a Reminder Extraction Agent. Extract reminder data from user input.

Return ONLY JSON in this format:
{
  "trigger_time": "ISO 8601 datetime",
  "lead_time": "15m",
  "delivery_method": "email",
  "destination": "user@example.com",
  "confidence": 0.0-1.0
}

Rules:
- trigger_time: When to send the reminder (ISO 8601 format)
- lead_time: How long before the task to remind (e.g., "15m", "1h", "1d")
- delivery_method: "email" or "push"
- destination: Email address or push token
- Extract relative times (e.g., "tomorrow at 5pm") to absolute ISO 8601

Examples:
User: "Remind me 15 minutes before my meeting tomorrow at 3pm"
Output: {"trigger_time": "2026-02-05T14:45:00Z", "lead_time": "15m", "delivery_method": "email", "destination": "user@example.com", "confidence": 0.95}

User: "Remind me at 5pm"
Output: {"trigger_time": "2026-02-04T17:00:00Z", "lead_time": "0m", "delivery_method": "email", "destination": "user@example.com", "confidence": 0.9}
"""
