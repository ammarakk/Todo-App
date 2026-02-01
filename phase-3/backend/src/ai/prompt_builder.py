# Implements: T015
# Phase III - AI-Powered Todo Chatbot
# System Prompts - Bilingual (English and Urdu)

from typing import Dict, Any, Optional
import re


class PromptBuilder:
    """
    Builds prompts for Qwen with bilingual support and tool definitions.

    Handles language detection and ensures responses match user language.
    """

    # System prompts in English and Urdu
    SYSTEM_PROMPTS = {
        "english": """You are a helpful task management assistant. You help users create, list, update, and delete tasks through natural conversation.

Key capabilities:
- Create tasks when users ask to add something
- List all tasks when users ask to see their tasks
- Delete tasks when users ask to remove a task
- Mark tasks as completed when users ask

Response format:
- Always reply in the same language as the user's message
- After each action, confirm what you did (e.g., "✅ Task 'Buy milk' has been added.")
- If you need more information, ask politely
- Be concise and helpful

You have access to these tools:
- add_task(user_id, title, description): Create a new task
- list_tasks(user_id, status): List all tasks (optional status filter: pending/completed/all)
- delete_task(user_id, task_id): Delete a specific task
- update_task(user_id, task_id, status, title, description): Update task status or content

IMPORTANT: Only use tools when explicitly requested by the user. Never make assumptions.""",

        "urdu": """آپ ایک مددگار ٹاسک MANAGEMENT اسسٹنٹ ہیں۔ آپ صارفین کو قدرتی گفتگو کے ذریعے ٹاسک بنانے، فہرست دکھانے، اپ ڈیٹ کرنے اور حذف کرنے میں مدد کرتے ہیں۔

اہمیت:
- جب صارف کچھ شامل کرنے کو کہیں تو ٹاسک بنائیں
- جب صارف اپنے ٹاسک دیکھنے کو کہیں تو فہرست دکھائیں
- جب صارف کوئی ٹاسک ہٹانے کو کہیں تو اسے حذف کریں
- جب صارف کوئی ٹاسک مکمل کرنے کو کہیں تو اسے مکمل کر دیں

جواب کا انداز:
- ہمیشہ صارف کے پیغام کی نفس زبان میں جواب دیں
- ہر کارروائی کے بعد تصدیق کریں (مثال: "✅ 'دودھ لینا' ٹاسک شامل ہو گیا ہے۔")
- اگر آپ کو مزید معلومات چاہیے تو politely پوچھیں
- مختصر اور مددگ رہیں

آپ کے پاس یہ tools موجود ہیں:
- add_task(user_id, title, description): نیا ٹاسک بنائیں
- list_tasks(user_id, status): تمام ٹاسک دکھائیں (اختیاری فلٹر: pending/completed/all)
- delete_task(user_id, task_id): مخصوص ٹاسک حذف کریں
- update_task(user_id, task_id, status, title, description): ٹاسک اپ ڈیٹ کریں

اہم: صرف تب tool استعمال کریں جب صارف نے صراحت کی ہو۔ کبھی بھی اندازہ نہ کریں۔"""
    }

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text is in Urdu or English.

        Args:
            text: User message text

        Returns:
            "urdu" or "english"
        """
        # Urdu script detection (Unicode range for Urdu)
        urdu_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        has_urdu_script = urdu_pattern.search(text)

        if has_urdu_script:
            return "urdu"

        # Roman Urdu detection (common Urdu words written in Latin script)
        roman_urdu_keywords = [
            'task', 'karo', 'add', 'karo', 'dikhao', 'tasks', 'mera', 'meri',
            'kuch', 'hai', 'ho', 'ga', 'ge', 'se', 'ka', 'ki', 'ke', 'ko'
        ]

        text_lower = text.lower()
        if any(keyword in text_lower for keyword in roman_urdu_keywords):
            # Check if majority of text looks like Roman Urdu
            # This is a simple heuristic - can be improved with ML
            return "urdu"

        return "english"

    @staticmethod
    def build_system_prompt(language: str = "english") -> str:
        """
        Get system prompt for specified language.

        Args:
            language: "english" or "urdu"

        Returns:
            System prompt string
        """
        return PromptBuilder.SYSTEM_PROMPTS.get(
            language.lower(),
            PromptBuilder.SYSTEM_PROMPTS["english"]  # Fallback to English
        )

    @staticmethod
    def build_conversation_history(messages: list) -> list:
        """
        Convert database messages to Qwen format.

        Args:
            messages: List of Message entities from database

        Returns:
            Formatted message array for Qwen
        """
        formatted = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # Map MessageRole to Qwen format
            if role == "user":
                formatted.append({"role": "user", "content": content})
            elif role == "assistant":
                formatted.append({"role": "assistant", "content": content})
            elif role == "tool":
                # Tool messages can be included in assistant responses
                # but formatted differently
                if msg.get("tool_calls"):
                    formatted.append({
                        "role": "assistant",
                        "content": f"[Tool executed: {msg['tool_calls']}]"
                    })

        return formatted

    @staticmethod
    def build_tools_definition() -> str:
        """
        Build tool definitions for Qwen.

        Returns:
            String describing available tools
        """
        return """
Available Tools:
1. add_task(user_id, title, description) - Create a new task
2. list_tasks(user_id, status) - List all tasks (status: pending/completed/all)
3. delete_task(user_id, task_id) - Delete a specific task
4. update_task(user_id, task_id, status, title, description) - Update task

Tool Call Format:
When you need to use a tool, respond in this exact format:
TOOL: tool_name
PARAMETERS: {"param1": "value1", "param2": "value2"}
"""
