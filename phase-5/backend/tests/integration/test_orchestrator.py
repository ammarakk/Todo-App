"""
Integration Tests for AI Orchestrator - Phase 5

Tests the complete orchestrator flow:
User Input → Intent Detection → Skill Dispatch → Validation → Execution → Event Publishing
"""

import pytest
import asyncio
from datetime import datetime, timezone

from src.orchestrator import IntentDetector, SkillDispatcher, EventPublisher, Intent
from src.agents.skills import TaskAgent, ReminderAgent


class TestIntentDetector:
    """Test intent detection from user input"""

    def test_create_task_intent(self):
        """Test detecting create task intent"""
        detector = IntentDetector()

        inputs = [
            "Create a task to buy milk",
            "Add a task: call mom",
            "New task: finish the report",
            "I need to buy groceries"
        ]

        for user_input in inputs:
            intent, confidence = detector.detect(user_input)
            assert intent == Intent.CREATE_TASK
            assert confidence >= 0.6
            print(f"✓ Input: '{user_input}' → Intent: {intent.value} (confidence: {confidence:.2f})")

    def test_complete_task_intent(self):
        """Test detecting complete task intent"""
        detector = IntentDetector()

        inputs = [
            "Mark task 1 as done",
            "Complete the buy milk task",
            "I finished calling mom",
            "Task #123 is done"
        ]

        for user_input in inputs:
            intent, confidence = detector.detect(user_input)
            assert intent == Intent.COMPLETE_TASK
            print(f"✓ Input: '{user_input}' → Intent: {intent.value}")

    def test_query_tasks_intent(self):
        """Test detecting query tasks intent"""
        detector = IntentDetector()

        inputs = [
            "Show me my tasks",
            "List all tasks",
            "What are my tasks?",
            "Get my task list"
        ]

        for user_input in inputs:
            intent, confidence = detector.detect(user_input)
            assert intent == Intent.QUERY_TASKS
            print(f"✓ Input: '{user_input}' → Intent: {intent.value}")

    def test_unknown_intent(self):
        """Test handling of unknown intent"""
        detector = IntentDetector()

        inputs = [
            "Hello",
            "What's the weather?",
            "Tell me a joke"
        ]

        for user_input in inputs:
            intent, confidence = detector.detect(user_input)
            assert intent == Intent.UNKNOWN
            print(f"✓ Input: '{user_input}' → Intent: {intent.value}")


class TestTaskAgent:
    """Test Task Agent extraction"""

    @pytest.mark.asyncio
    async def test_extract_task_from_input(self):
        """Test extracting task data from natural language"""
        agent = TaskAgent("phase-5/backend/src/agents/skills/prompts/task_prompt.txt")

        test_cases = [
            {
                "input": "Create a task to buy milk tomorrow at 5pm",
                "expected_title": "buy milk",
                "expected_priority": "medium"
            },
            {
                "input": "High priority task: finish the report",
                "expected_title": "finish the report",
                "expected_priority": "high"
            }
        ]

        for case in test_cases:
            result = await agent.execute(case["input"], {"user_id": "test"})

            assert result["title"] == case["expected_title"]
            assert result["priority"] == case["expected_priority"]
            assert result["confidence"] >= 0.0
            print(f"✓ Input: '{case['input']}'")
            print(f"  → Title: {result['title']}, Priority: {result['priority']}, Confidence: {result['confidence']}")


class TestReminderAgent:
    """Test Reminder Agent extraction"""

    @pytest.mark.asyncio
    async def test_extract_reminder_from_input(self):
        """Test extracting reminder data from natural language"""
        agent = ReminderAgent("phase-5/backend/src/agents/skills/prompts/reminder_prompt.txt")

        test_cases = [
            {
                "input": "Remind me 15 minutes before the meeting",
                "expected_lead_time": "15m"
            },
            {
                "input": "Remind me at 5pm",
                "expected_lead_time": "0m"
            }
        ]

        for case in test_cases:
            result = await agent.execute(case["input"], {"user_id": "test"})

            assert "trigger_time" in result
            assert result["lead_time"] == case["expected_lead_time"]
            print(f"✓ Input: '{case['input']}'")
            print(f"  → Trigger: {result['trigger_time']}, Lead time: {result['lead_time']}")


class TestOrchestratorFlow:
    """Test complete orchestrator flow"""

    @pytest.mark.asyncio
    async def test_end_to_end_task_creation(self):
        """Test full flow: input → intent → agent → validation"""
        detector = IntentDetector()
        dispatcher = SkillDispatcher()

        user_input = "Create a task to buy milk tomorrow at 5pm"
        user_id = "test-user-123"
        context = {"user_id": user_id}

        # Step 1: Detect intent
        intent, confidence = detector.detect(user_input)
        assert intent == Intent.CREATE_TASK
        print(f"✓ Step 1: Intent detected → {intent.value} (confidence: {confidence:.2f})")

        # Step 2: Dispatch to skill agent
        skill_result = await dispatcher.dispatch(intent, user_input, context)
        assert skill_result["title"] == "buy milk"
        assert skill_result["confidence"] >= 0.6
        print(f"✓ Step 2: Skill dispatched → Title: {skill_result['title']}, Due: {skill_result.get('due_date')}")

        # Step 3: Validate result
        assert skill_result["confidence"] >= 0.7
        print(f"✓ Step 3: Validation passed → Ready for execution")

        print(f"\n✅ Full orchestrator flow working!")


class TestEventPublisher:
    """Test event publishing (requires Dapr running)"""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        True,
        reason="Requires Dapr sidecar running - skip in CI"
    )
    async def test_publish_task_event(self):
        """Test publishing task events to Kafka via Dapr"""
        publisher = EventPublisher()

        # Test task.created event
        success = await publisher.publish_task_event(
            "task.created",
            "test-task-123",
            {
                "title": "Test Task",
                "priority": "medium",
                "user_id": "test-user"
            },
            correlation_id="test-correlation-123"
        )

        assert success is True
        print("✓ Event published successfully")


if __name__ == "__main__":
    # Run tests manually for quick verification
    print("\n=== Running Orchestrator Integration Tests ===\n")

    print("\n--- Testing Intent Detector ---")
    intent_tests = TestIntentDetector()
    intent_tests.test_create_task_intent()
    intent_tests.test_complete_task_intent()
    intent_tests.test_query_tasks_intent()
    intent_tests.test_unknown_intent()

    print("\n--- Testing Task Agent ---")
    task_tests = TestTaskAgent()
    asyncio.run(task_tests.test_extract_task_from_input())

    print("\n--- Testing Reminder Agent ---")
    reminder_tests = TestReminderAgent()
    asyncio.run(reminder_tests.test_extract_reminder_from_input())

    print("\n--- Testing Complete Orchestrator Flow ---")
    flow_tests = TestOrchestratorFlow()
    asyncio.run(flow_tests.test_end_to_end_task_creation())

    print("\n=== All Tests Passed! ✅ ===\n")
