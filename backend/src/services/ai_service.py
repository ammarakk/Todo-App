"""
AI Service for Hugging Face integration.

Provides todo generation, summarization, and prioritization features.
"""
import json
import os
from typing import List, Optional
from huggingface_hub import InferenceClient

from src.core.config import settings


class AIService:
    """Service for AI-powered todo features."""

    def __init__(self):
        """Initialize AI service with Hugging Face client."""
        self.client = None
        if settings.huggingface_api_key:
            self.client = InferenceClient(token=settings.huggingface_api_key)

    def _generate_todos_prompt(self, goal: str) -> str:
        """Generate prompt for todo creation."""
        return f"""You are a task planning assistant. Generate 5-7 actionable, specific todo items for this goal: "{goal}"

Requirements:
- Each todo must be specific and actionable
- Include realistic due dates (relative: "tomorrow", "next week", "next month")
- Assign priority (low/medium/high)
- Return as JSON array with exact format below

Output format (JSON array):
{{
  "todos": [
    {{"title": "Research competitors", "description": "Analyze top 3 competitor features", "priority": "high", "due_date": "2025-01-25"}},
    {{"title": "Create wireframes", "description": "Sketch main dashboard screens", "priority": "medium", "due_date": "2025-01-26"}}
  ]
}}

Only return JSON, no other text."""

    def _summarize_todos_prompt(self, todos: List) -> str:
        """Generate prompt for todo summarization."""
        todos_text = "\n".join([f"- {t['title']}: {t.get('description', '')}" for t in todos])
        return f"""Summarize these {len(todos)} todo items into a concise overview:

{todos_text}

Provide:
- Total count breakdown by priority (high/medium/low)
- Top 3 most urgent items
- One sentence overall status

Keep under 100 words. Be concise and actionable."""

    def _prioritize_todos_prompt(self, todos: List) -> str:
        """Generate prompt for todo prioritization."""
        todos_text = "\n".join([
            f"{i+1}. {t['title']} (Priority: {t.get('priority', 'medium')}, Due: {t.get('due_date', 'none')})"
            for i, t in enumerate(todos)
        ])
        return f"""You are a productivity expert. Reorder these todos by urgency and importance:

Current todos:
{todos_text}

Consider:
- Due dates (earlier = more urgent)
- Priority levels explicitly assigned
- Task dependencies

Return as ordered JSON array:
{{
  "todos": [
    {{"id": "1", "title": "...", "priority_score": 95, "reasoning": "Due tomorrow"}},
    {{"id": "2", "title": "...", "priority_score": 80, "reasoning": "High priority, due in 3 days"}}
  ]
}}

Only return JSON, no other text."""

    def generate_todos(self, goal: str) -> dict:
        """
        Generate todos from a goal using AI.

        Args:
            goal: User's goal to break down into todos

        Returns:
            Dict with generated todos

        Raises:
            ValueError: If AI service is not configured or response is invalid
        """
        if not self.client:
            raise ValueError("AI service not configured. Please set HUGGINGFACE_API_KEY.")

        try:
            prompt = self._generate_todos_prompt(goal)
            response = self.client.text_generation(
                prompt,
                model="mistralai/Mistral-7B-Instruct-v0.2",
                max_new_tokens=500,
                temperature=0.7,
            )

            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            return {
                "todos": result.get("todos", []),
                "message": f"Generated {len(result.get('todos', []))} todos for your goal"
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid AI response format. Please try again.") from e
        except Exception as e:
            raise ValueError(f"AI service error: {str(e)}") from e

    def summarize_todos(self, todos: List[dict]) -> dict:
        """
        Summarize todos using AI.

        Args:
            todos: List of todo dictionaries

        Returns:
            Dict with summary and breakdown
        """
        if not self.client:
            raise ValueError("AI service not configured. Please set HUGGINGFACE_API_KEY.")

        if not todos:
            return {
                "summary": "No todos to summarize.",
                "breakdown": {"high_priority": 0, "medium_priority": 0, "low_priority": 0},
                "urgent_todos": []
            }

        try:
            # Calculate breakdown
            breakdown = {
                "high_priority": sum(1 for t in todos if t.get("priority") == "high"),
                "medium_priority": sum(1 for t in todos if t.get("priority") == "medium"),
                "low_priority": sum(1 for t in todos if t.get("priority") == "low"),
            }

            # Get urgent todos (high priority or due soon)
            from datetime import datetime, timedelta
            urgent = []
            for t in todos:
                if t.get("priority") == "high":
                    urgent.append(t.get("title", ""))
                elif t.get("due_date"):
                    try:
                        due_date = datetime.fromisoformat(t["due_date"].replace("Z", "+00:00"))
                        if due_date <= datetime.now() + timedelta(days=2):
                            urgent.append(t.get("title", ""))
                    except:
                        pass

            # Generate summary
            prompt = self._summarize_todos_prompt(todos)
            summary = self.client.text_generation(
                prompt,
                model="facebook/bart-large-cnn",
                max_new_tokens=200,
                temperature=0.5,
            )

            return {
                "summary": summary.strip(),
                "breakdown": breakdown,
                "urgent_todos": urgent[:3]  # Top 3 urgent
            }

        except Exception as e:
            raise ValueError(f"AI service error: {str(e)}") from e

    def prioritize_todos(self, todos: List[dict]) -> dict:
        """
        Prioritize todos using AI.

        Args:
            todos: List of todo dictionaries

        Returns:
            Dict with prioritized todos
        """
        if not self.client:
            raise ValueError("AI service not configured. Please set HUGGINGFACE_API_KEY.")

        if not todos:
            return {
                "prioritized_todos": [],
                "message": "No todos to prioritize"
            }

        try:
            prompt = self._prioritize_todos_prompt(todos)
            response = self.client.text_generation(
                prompt,
                model="mistralai/Mistral-7B-Instruct-v0.2",
                max_new_tokens=500,
                temperature=0.7,
            )

            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            return {
                "prioritized_todos": result.get("todos", []),
                "message": f"Prioritized {len(result.get('todos', []))} todos"
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid AI response format. Please try again.") from e
        except Exception as e:
            raise ValueError(f"AI service error: {str(e)}") from e


# Global AI service instance
ai_service = AIService()


__all__ = ['ai_service', 'AIService']
