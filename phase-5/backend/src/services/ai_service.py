"""
AI Service for Qwen API integration.

Provides todo generation, summarization, and prioritization features.
"""
import json
import os
from typing import List, Optional
from openai import OpenAI

from src.core.config import settings

# Qwen API Configuration (same as chatbot)
USE_QWEN_API = os.getenv("USE_QWEN_API", "true").lower() == "true"
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "0XA2TcDarwQtRtWP-uwkwY2L3PCkWHFuzQkxWyW1r2Xm58q5dR81tBuQSTAvW7AKppM8D0GRseYZb8AZ-cMtiQ")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")


class AIService:
    """Service for AI-powered todo features using Qwen API."""

    def __init__(self):
        """Initialize AI service with Qwen client."""
        self.client = None
        self.model = None

        # Try Qwen API first (same as chatbot)
        if USE_QWEN_API and QWEN_API_KEY:
            try:
                self.client = OpenAI(
                    api_key=QWEN_API_KEY,
                    base_url=QWEN_BASE_URL
                )
                self.model = "qwen-turbo"
            except Exception as e:
                print(f"Failed to initialize Qwen client: {e}")
        elif settings.huggingface_api_key:
            # Fallback to HuggingFace (original implementation)
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(
                model="Qwen/Qwen2.5-0.5B-Instruct",
                token=settings.huggingface_api_key
            )
            self.model = "huggingface"

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

    def _call_qwen_api(self, prompt: str) -> str:
        """Call Qwen API for text generation."""
        response = self.client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful task management assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _call_huggingface_api(self, prompt: str) -> str:
        """Call HuggingFace Inference API (fallback)."""
        response = self.client.text_generation(
            prompt,
            max_new_tokens=500,
            temperature=0.7,
        )
        return response.strip()

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
            raise ValueError("AI service not configured. Please set QWEN_API_KEY or HUGGINGFACE_API_KEY.")

        try:
            prompt = self._generate_todos_prompt(goal)

            # Call appropriate API
            if self.model == "huggingface":
                response_text = self._call_huggingface_api(prompt)
            else:
                response_text = self._call_qwen_api(prompt)

            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Try to find JSON array in the response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                todos_list = json.loads(json_str)
                return {
                    "todos": todos_list,
                    "message": f"Generated {len(todos_list)} todos for your goal"
                }
            else:
                # Fallback: return the raw text
                return {
                    "todos": [],
                    "message": "AI generated a response but couldn't parse todos. Please try again.",
                    "raw_response": response_text[:500]  # First 500 chars
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
            raise ValueError("AI service not configured. Please set QWEN_API_KEY or HUGGINGFACE_API_KEY.")

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

            # Generate simple summary (without AI for now)
            summary = f"You have {len(todos)} total todos. Breakdown: {breakdown['high_priority']} high, {breakdown['medium_priority']} medium, {breakdown['low_priority']} low priority."

            return {
                "summary": summary,
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
            raise ValueError("AI service not configured. Please set QWEN_API_KEY or HUGGINGFACE_API_KEY.")

        if not todos:
            return {
                "prioritized_todos": [],
                "message": "No todos to prioritize"
            }

        try:
            # Simple prioritization without AI for now
            prioritized = sorted(
                todos,
                key=lambda t: (
                    0 if t.get("priority") == "high" else 1 if t.get("priority") == "medium" else 2,
                    t.get("due_date") or "9999-12-31"
                )
            )

            return {
                "prioritized_todos": prioritized,
                "message": f"Prioritized {len(prioritized)} todos by priority and due date"
            }

        except Exception as e:
            raise ValueError(f"AI service error: {str(e)}") from e


# Global AI service instance
ai_service = AIService()


__all__ = ['ai_service', 'AIService']
