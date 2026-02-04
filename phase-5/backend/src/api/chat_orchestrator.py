"""
Chat Orchestrator API - Phase 5

Main chat endpoint that orchestrates AI agents, MCP tools, and event publishing.
This is the heart of the AI-native todo application.
"""

import json
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from src.orchestrator import IntentDetector, SkillDispatcher, EventPublisher, Intent
from src.models.base import get_db
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.utils.logging import get_logger
from src.utils.errors import ValidationError

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize orchestrator components
intent_detector = IntentDetector()
skill_dispatcher = SkillDispatcher()
event_publisher = EventPublisher()


@router.post("/command")
async def chat_command(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process chat command through AI orchestrator flow.

    Orchestrator Flow:
    1. Load conversation context (if exists)
    2. Detect user intent
    3. Dispatch to appropriate skill agent
    4. Validate skill output
    5. Execute business logic (via MCP tools)
    6. Publish Kafka events
    7. Save conversation to database
    8. Return response to user

    Args:
        request: Chat request with user_input, conversation_id, user_id
        db: Database session

    Returns:
        Chat response with intent, confidence, and result
    """
    user_input = request.get("user_input", "").strip()
    conversation_id = request.get("conversation_id")
    user_id = request.get("user_id")  # From Phase III auth

    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_input is required"
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id is required"
        )

    correlation_id = str(uuid.uuid4())

    logger.info(
        "chat_command_start",
        user_id=user_id,
        conversation_id=conversation_id,
        input_length=len(user_input),
        correlation_id=correlation_id
    )

    try:
        # Step 1: Load or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                dapr_state_key=f"conversation:{uuid.uuid4()}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = str(conversation.id)

        # Step 2: Save user message to database
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=user_input
        )
        db.add(user_message)
        db.commit()

        # Step 3: Detect intent
        intent, confidence, metadata = intent_detector.detect_with_context(
            user_input,
            context={"user_id": user_id, "conversation_id": conversation_id}
        )

        logger.info(
            "intent_detected",
            intent=intent.value,
            confidence=confidence,
            correlation_id=correlation_id
        )

        # Step 4: Dispatch to skill agent
        context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "correlation_id": correlation_id
        }

        skill_result = await skill_dispatcher.dispatch(intent, user_input, context)

        # Step 5: Validate skill output
        if skill_result.get("confidence", 0) < 0.7:
            # Low confidence - ask for clarification
            clarification_response = await _handle_low_confidence(
                user_input,
                intent,
                confidence,
                skill_result
            )

            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=clarification_response["response"],
                intent_detected=intent.value,
                confidence_score=confidence
            )
            db.add(assistant_message)
            db.commit()

            return clarification_response

        # Step 6: Execute business logic based on intent
        result = await _execute_intent(
            intent,
            skill_result,
            user_id,
            db,
            correlation_id
        )

        # Step 7: Generate response message
        response_text = result.get("message", _generate_default_response(intent, result))

        # Step 8: Save assistant message with AI metadata
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            intent_detected=intent.value,
            skill_agent_used=skill_result.get("agent", "TaskAgent"),
            confidence_score=confidence
        )
        db.add(assistant_message)

        # Update conversation last_message_at
        conversation.last_message_at = assistant_message.created_at
        db.commit()

        logger.info(
            "chat_command_success",
            intent=intent.value,
            result_keys=list(result.keys()),
            correlation_id=correlation_id
        )

        return {
            "response": response_text,
            "conversation_id": str(conversation_id),
            "intent_detected": intent.value,
            "skill_agent_used": skill_result.get("agent", "TaskAgent"),
            "confidence_score": confidence,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_command_error",
            error=str(e),
            correlation_id=correlation_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request"
        )


async def _handle_low_confidence(
    user_input: str,
    intent: Intent,
    confidence: float,
    skill_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle low confidence detections with clarification."""
    clarification_messages = {
        Intent.CREATE_TASK: (
            f"I think you want to create a task, but I'm not sure about the details. "
            f"You said: '{user_input}'. Could you provide the task title?"
        ),
        Intent.UPDATE_TASK: (
            f"I'd like to help update your task, but I'm not sure which task or what changes. "
            f"Could you clarify?"
        ),
        Intent.UNKNOWN: (
            f"I'm not sure what you'd like to do. You said: '{user_input}'. "
            f"Could you rephrase that? I can help you create, update, complete, or list tasks."
        )
    }

    message = clarification_messages.get(
        intent,
        f"I'm not sure I understood correctly. You said: '{user_input}'. Could you clarify?"
    )

    return {
        "response": message,
        "intent_detected": intent.value,
        "confidence_score": confidence,
        "clarification_needed": True
    }


async def _execute_intent(
    intent: Intent,
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Execute business logic based on intent."""
    if intent == Intent.CREATE_TASK:
        return await _create_task(skill_result, user_id, db, correlation_id)

    elif intent == Intent.UPDATE_TASK:
        return await _update_task(skill_result, user_id, db, correlation_id)

    elif intent == Intent.COMPLETE_TASK:
        return await _complete_task(skill_result, user_id, db, correlation_id)

    elif intent == Intent.DELETE_TASK:
        return await _delete_task(skill_result, user_id, db, correlation_id)

    elif intent == Intent.QUERY_TASKS:
        return await _query_tasks(skill_result, user_id, db)

    elif intent == Intent.SET_REMINDER:
        return await _set_reminder(skill_result, user_id, db, correlation_id)

    else:
        return {
            "message": "I'm not sure how to help with that. Could you try rephrasing?",
            "suggestion": "Try: 'Create a task to buy milk tomorrow'"
        }


async def _create_task(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Create task from skill result."""
    try:
        # Create task
        task = Task(
            title=skill_result["title"],
            description=skill_result.get("description"),
            due_date=skill_result.get("due_date"),
            priority=skill_result.get("priority", "medium"),
            tags=skill_result.get("tags", []),
            reminder_config=skill_result.get("reminder_config"),
            recurrence_rule=skill_result.get("recurrence_rule"),
            user_id=user_id
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        # Publish events
        await event_publisher.publish_task_event(
            "task.created",
            str(task.id),
            task.to_dict(),
            correlation_id
        )

        await event_publisher.publish_task_update(
            str(task.id),
            "created",
            task.to_dict(),
            correlation_id
        )

        await event_publisher.publish_audit_event(
            "Task",
            str(task.id),
            "CREATE",
            "user",
            user_id,
            new_values=task.to_dict(),
            correlation_id=correlation_id
        )

        return {
            "message": f"I've created a task '{task.title}' for you.",
            "task_created": {
                "task_id": str(task.id),
                "title": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value if task.priority else None
            }
        }

    except Exception as e:
        logger.error("create_task_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


async def _update_task(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Update task."""
    # TODO: Implement task update logic
    return {
        "message": "Task updates are coming soon!",
        "skill_result": skill_result
    }


async def _complete_task(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Complete task."""
    # TODO: Implement task completion logic
    return {
        "message": "Task completion is coming soon!",
        "skill_result": skill_result
    }


async def _delete_task(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Delete task."""
    # TODO: Implement task deletion logic
    return {
        "message": "Task deletion is coming soon!",
        "skill_result": skill_result
    }


async def _query_tasks(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session
) -> Dict[str, Any]:
    """Query tasks."""
    try:
        # Build query filters
        query = db.query(Task).filter(Task.user_id == user_id)

        # Apply status filter
        if skill_result.get("status"):
            query = query.filter(Task.status == skill_result["status"])

        # Apply priority filter
        if skill_result.get("priority"):
            query = query.filter(Task.priority == skill_result["priority"])

        # Execute query
        tasks = query.limit(20).all()

        return {
            "message": f"Found {len(tasks)} task(s)",
            "tasks": [task.to_dict() for task in tasks]
        }

    except Exception as e:
        logger.error("query_tasks_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query tasks"
        )


async def _set_reminder(
    skill_result: Dict[str, Any],
    user_id: str,
    db: Session,
    correlation_id: str
) -> Dict[str, Any]:
    """Set reminder."""
    # TODO: Implement reminder creation logic
    return {
        "message": "Reminder creation is coming soon!",
        "skill_result": skill_result
    }


def _generate_default_response(intent: Intent, result: Dict[str, Any]) -> str:
    """Generate default response for intent."""
    responses = {
        Intent.CREATE_TASK: "Task created successfully!",
        Intent.UPDATE_TASK: "Task updated successfully!",
        Intent.COMPLETE_TASK: "Great job! Task completed.",
        Intent.DELETE_TASK: "Task deleted.",
        Intent.QUERY_TASKS: f"Found {result.get('task_count', 0)} tasks.",
        Intent.SET_REMINDER: "Reminder set!"
    }

    return responses.get(intent, "Done!")
