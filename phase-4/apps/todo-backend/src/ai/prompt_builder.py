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
        "english": """You are a task management assistant. CRITICAL: You MUST use tools for ALL task operations.

MANDATORY TOOL USAGE:
1. When user wants to create a task: You MUST respond with TOOL_CALL: {"tool": "create_task", "parameters": {"title": "task title", "priority": "medium"}}
2. When user wants to see tasks: You MUST respond with TOOL_CALL: {"tool": "list_tasks", "parameters": {}}
3. When user wants to complete/delete/update: You MUST respond with the appropriate TOOL_CALL

TOOL CALL FORMAT (STRICT - NO EXCEPTIONS):
TOOL_CALL: {"tool": "tool_name", "parameters": {"key": "value"}}

Available tools:
- create_task (params: title, description, priority, due_date, tags)
- list_tasks (params: {})
- update_task (params: task_id, title, description, priority, status)
- delete_task (params: task_id)
- complete_task (params: task_id)

CRITICAL: NEVER explain what you would do. ALWAYS use the exact TOOL_CALL format.
DO NOT include markdown, code blocks, or explanations. Just the TOOL_CALL line.

Examples:
User: "Create a todo to buy groceries"
Assistant: TOOL_CALL: {"tool": "create_task", "parameters": {"title": "Buy groceries", "priority": "medium"}}

User: "Show me my tasks"
Assistant: TOOL_CALL: {"tool": "list_tasks", "parameters": {}}
""",

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

اہم: صرف تب tool استعمال کریں جب صارف نے صراحت کی ہو۔ کبھی بھی اندازہ نہ کریں۔""",

        "roman_urdu": """You are a task management assistant. CRITICAL: You MUST use tools for ALL task operations.

MANDATORY TOOL USAGE:
1. Jab user task banana chahe: TOOL_CALL: {"tool": "create_task", "parameters": {"title": "task title", "priority": "medium"}}
2. Jab user tasks dekhna chahe: TOOL_CALL: {"tool": "list_tasks", "parameters": {}}
3. Jab user task complete/delete/update karna chahe: Appropriate TOOL_CALL use karo

TOOL CALL FORMAT (STRICT - KOI EXCEPTION NAHI):
TOOL_CALL: {"tool": "tool_name", "parameters": {"key": "value"}}

Available tools:
- create_task (params: title, description, priority, due_date, tags)
- list_tasks (params: {})
- update_task (params: task_id, title, description, priority, status)
- delete_task (params: task_id)
- complete_task (params: task_id)

CRITICAL: Kabhi explain mat karo kya karoge. HAMESHA exact TOOL_CALL format use karo.
Markdown, code blocks ya explanations mat use karo. Sirf TOOL_CALL line likho.

Examples:
User: "Mujhe ek todo banana hai groceries buy karne ke liye"
Assistant: TOOL_CALL: {"tool": "create_task", "parameters": {"title": "Buy groceries", "priority": "medium"}}

User: "Meri tasks dikhao"
Assistant: TOOL_CALL: {"tool": "list_tasks", "parameters": {}}

User: "Ye complete kar do groceries wala task"
Assistant: TOOL_CALL: {"tool": "complete_task", "parameters": {"task_id": "TASK_ID"}}
"""
    }

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text is in English, Urdu script, or Roman Urdu.

        Args:
            text: User message text

        Returns:
            "english", "urdu", or "roman_urdu"
        """
        # Urdu script detection (Unicode range for Urdu)
        urdu_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        has_urdu_script = urdu_pattern.search(text)

        if has_urdu_script:
            return "urdu"

        # Roman Urdu detection (common Urdu words written in Latin script)
        roman_urdu_keywords = [
            'karo', 'krna', 'daina', 'bana', 'dikhana', 'dikhao',
            'mera', 'meri', 'mere', 'kuch', 'hai', 'ho', 'hoga', 'hogi',
            'se', 'ka', 'ki', 'ke', 'ko', 'mein', 'main', 'ap', 'aap',
            'kya', 'kis', 'kon', 'sa', 'hi', 'bhi', 'liye', 'waje',
            'jald', 'turant', 'plz', 'please', 'shukriya', 'thanks'
        ]

        text_lower = text.lower()
        # Check if multiple Roman Urdu words are present
        roman_urdu_count = sum(1 for word in roman_urdu_keywords if word in text_lower)

        if roman_urdu_count >= 2:
            return "roman_urdu"

        return "english"

    @staticmethod
    def build_system_prompt(language: str = "english") -> str:
        """
        Get system prompt for specified language.

        Args:
            language: "english", "urdu", or "roman_urdu"

        Returns:
            System prompt string
        """
        language = language.lower()
        if language not in ["english", "urdu", "roman_urdu"]:
            language = "english"  # Fallback to English
        return PromptBuilder.SYSTEM_PROMPTS.get(language)

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
        Build tool definitions for AI.

        Returns:
            String describing available tools
        """
        return """
Available MCP Tools:
1. create_task(title, description, priority, due_date, tags) - Create a new task
2. list_tasks(status, priority) - List all tasks
3. update_task(task_id, title, description, priority, status, due_date, tags) - Update a task
4. delete_task(task_id) - Delete a task
5. complete_task(task_id) - Mark a task as completed

Tool Call Format:
When you need to use a tool, respond with this exact format:
TOOL_CALL: {"tool": "tool_name", "parameters": {"param1": "value1"}}
"""
