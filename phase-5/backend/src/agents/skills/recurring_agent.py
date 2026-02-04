"""
Recurring Agent - Phase 5

AI skill agent for calculating recurring task schedules.
Handles date arithmetic for daily, weekly, monthly patterns.
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


class RecurringAgent:
    """
    Calculates next occurrence for recurring tasks.

    Handles:
    - Daily recurrence (every N days)
    - Weekly recurrence (every N weeks, specific days)
    - Monthly recurrence (every N months, specific day)
    """

    def __init__(self, prompt_path: str, ollama_url: str = "http://localhost:11434"):
        """
        Initialize Recurring Agent.

        Args:
            prompt_path: Path to recurring prompt file
            ollama_url: URL for Ollama service
        """
        self.prompt_path = Path(prompt_path)
        self.ollama_url = ollama_url

        if self.prompt_path.exists():
            self.prompt = self.prompt_path.read_text()
        else:
            self.prompt = self._get_default_prompt()

        if OllamaClient:
            self.ollama = OllamaClient(host=ollama_url)
        else:
            self.ollama = None
            logger.warning("ollama_not_available", using_fallback=True)

    async def execute(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate next occurrence for recurring task.

        Args:
            input_text: User's natural language input
            context: Additional context (current_date, recurrence_rule, etc.)

        Returns:
            Structured JSON with recurrence data:
            {
                "pattern": "daily|weekly|monthly",
                "interval": 1,
                "next_date": "ISO 8601 datetime",
                "confidence": 0.0-1.0
            }
        """
        logger.info(
            "recurring_agent_execute",
            input_length=len(input_text),
            context_keys=list(context.keys())
        )

        # Try Ollama first
        if self.ollama:
            try:
                full_prompt = f"""
{self.prompt}

User Input: {input_text}
Context: {json.dumps(context, indent=2)}
Current Date: {datetime.now(timezone.utc).isoformat()}

Extract recurrence data and return ONLY JSON (no markdown, no explanation).
"""

                response = self.ollama.generate(
                    model='llama2',
                    prompt=full_prompt,
                    stream=False
                )

                result_text = response.get('response', '')
                result = self._parse_json_result(result_text, input_text, context)

                logger.info(
                    "recurring_agent_success",
                    pattern=result.get("pattern"),
                    next_date=result.get("next_date"),
                    confidence=result.get("confidence")
                )

                return result

            except Exception as e:
                logger.error(
                    "recurring_agent_ollama_failed",
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
            if "pattern" not in result:
                result["pattern"] = self._extract_pattern_from_text(input_text)

            if "next_date" not in result:
                result["next_date"] = self._calculate_next_date(
                    result.get("pattern", "daily"),
                    result.get("interval", 1),
                    context
                )

            result.setdefault("interval", 1)
            result.setdefault("confidence", 0.95)

            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "recurring_agent_json_parse_failed",
                error=str(e),
                using_fallback=True
            )
            return self._fallback_extraction(input_text, context)

    def _fallback_extraction(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based extraction."""
        pattern = self._extract_pattern_from_text(input_text)
        interval = self._extract_interval_from_text(input_text)
        next_date = self._calculate_next_date(pattern, interval, context)

        return {
            "pattern": pattern,
            "interval": interval,
            "next_date": next_date,
            "confidence": 0.7  # Lower confidence for fallback
        }

    def _extract_pattern_from_text(self, text: str) -> str:
        """Extract recurrence pattern from text."""
        text_lower = text.lower()

        if "daily" in text_lower or "every day" in text_lower:
            return "daily"
        elif "weekly" in text_lower or "every week" in text_lower:
            return "weekly"
        elif "monthly" in text_lower or "every month" in text_lower:
            return "monthly"
        else:
            return "daily"  # Default

    def _extract_interval_from_text(self, text: str) -> int:
        """Extract interval from text (e.g., "every 2 weeks" -> 2)."""
        match = re.search(r'every\s+(\d+)', text.lower())
        if match:
            return int(match.group(1))
        return 1  # Default

    def _calculate_next_date(
        self,
        pattern: str,
        interval: int,
        context: Dict[str, Any]
    ) -> str:
        """
        Calculate next occurrence date.

        Args:
            pattern: Recurrence pattern (daily, weekly, monthly)
            interval: Interval (every N days/weeks/months)
            context: Additional context

        Returns:
            ISO 8601 datetime string
        """
        now = datetime.now(timezone.utc)

        if pattern == "daily":
            next_date = now + timedelta(days=interval)

        elif pattern == "weekly":
            next_date = now + timedelta(weeks=interval)

        elif pattern == "monthly":
            # Add months (handle year rollover)
            new_month = now.month + interval
            year = now.year + (new_month - 1) // 12
            month = (new_month - 1) % 12 + 1

            # Keep same day of month
            try:
                next_date = now.replace(year=year, month=month)
            except ValueError:
                # Handle invalid dates (e.g., Jan 31 -> Feb)
                next_date = now.replace(year=year, month=month, day=28)

        else:
            next_date = now + timedelta(days=interval)

        return next_date.isoformat()

    def _get_default_prompt(self) -> str:
        """Get default system prompt for recurring task extraction."""
        return """You are a Recurring Task Agent. Calculate the next occurrence for recurring tasks.

Return ONLY JSON in this format:
{
  "pattern": "daily|weekly|monthly",
  "interval": 1,
  "next_date": "ISO 8601 datetime",
  "confidence": 0.0-1.0
}

Rules:
- pattern: Type of recurrence (daily, weekly, monthly)
- interval: How often (every N days/weeks/months)
- next_date: Next occurrence in ISO 8601 format
- Calculate next_date from current date + interval

Examples:
User: "Repeat daily"
Output: {"pattern": "daily", "interval": 1, "next_date": "2026-02-05T09:00:00Z", "confidence": 0.95}

User: "Repeat every 2 weeks"
Output: {"pattern": "weekly", "interval": 2, "next_date": "2026-02-18T09:00:00Z", "confidence": 0.95}
"""
