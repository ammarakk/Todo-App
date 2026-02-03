"""
Chat API Endpoint - AI Orchestrator
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4

from src.api.models import ChatCommandRequest, ChatCommandResponse
from src.models import Task
from src.services import IntentDetector, SkillDispatcher, EventPublisher
from src.utils.database import get_db_session
from src.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

intent_detector = IntentDetector()
skill_dispatcher = SkillDispatcher()
event_publisher = EventPublisher()


@router.post("/command", response_model=ChatCommandResponse)
async def chat_command(
    request: ChatCommandRequest,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Process chat command via AI orchestrator"""
    correlation_id = str(uuid4())

    # Detect intent
    intent_result = intent_detector.detect(request.user_input)

    if intent_result["requires_clarification"]:
        return ChatCommandResponse(
            response=f"I need more info: {', '.join(intent_result['missing_fields'])}",
            intent_detected=intent_result["intent"],
            skill_agent_used=intent_result["agent"] or "none",
            confidence_score=intent_result["confidence"],
            requires_clarification=True,
        )

    # Build context
    context = {
        "user_id": "default-user-id",
        "db_session": db_session,
        "correlation_id": correlation_id,
    }

    # Dispatch to skill agent
    await skill_dispatcher.dispatch(
        agent_name=intent_result["agent"],
        intent_data=intent_result["data"],
        context=context,
    )

    # Execute operation
    try:
        if intent_result["intent"] == "create":
            result = await _create_task(intent_result["data"], context, correlation_id)
        elif intent_result["intent"] == "complete":
            result = await _complete_task(intent_result["data"], context, correlation_id)
        elif intent_result["intent"] == "list":
            result = await _list_tasks(intent_result["data"], context)
        else:
            result = {"response": "Could you please rephrase that?"}

        return ChatCommandResponse(
            response=result["response"],
            intent_detected=intent_result["intent"],
            skill_agent_used=intent_result["agent"],
            confidence_score=intent_result["confidence"],
            requires_clarification=False,
            data=result.get("data"),
        )
    except Exception as e:
        logger.error("chat_command_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def _create_task(data: dict, context: dict, correlation_id: str) -> dict:
    """Create a new task"""
    db_session = context["db_session"]

    task = Task(
        user_id=UUID(context["user_id"]),
        title=data["title"],
        priority=data.get("priority", "medium"),
        tags=data.get("tags", []),
        status="active",
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Publish event
    await event_publisher.publish_task_created(
        task_id=str(task.id),
        user_id=context["user_id"],
        task_data=task.to_dict(),
        correlation_id=correlation_id,
    )

    return {
        "response": f"I've created '{task.title}' with {task.priority} priority.",
        "data": {"task_id": str(task.id)},
    }


async def _complete_task(data: dict, context: dict, correlation_id: str) -> dict:
    """Mark a task as complete"""
    db_session = context["db_session"]

    result = await db_session.execute(select(Task).where(Task.id == UUID(data["task_id"])))
    task = result.scalar_one_or_none()

    if not task:
        return {"response": "Task not found."}

    task.status = "completed"
    await db_session.commit()

    await event_publisher.publish_task_completed(
        task_id=str(task.id),
        user_id=context["user_id"],
        correlation_id=correlation_id,
    )

    return {"response": f"Marked '{task.title}' as complete!", "data": {"task_id": str(task.id)}}


async def _list_tasks(data: dict, context: dict) -> dict:
    """List user's tasks"""
    db_session = context["db_session"]

    query = select(Task).where(Task.user_id == UUID(context["user_id"]))
    filters = data.get("filters", {})
    if "status" in filters:
        query = query.where(Task.status == filters["status"])

    result = await db_session.execute(query)
    tasks = result.scalars().all()

    if not tasks:
        return {"response": "No tasks found.", "data": {"tasks": []}}

    task_list = "\n".join([f"- {t.title} ({t.status})" for t in tasks[:10]])
    return {"response": f"Your tasks:\n{task_list}", "data": {"tasks": [t.to_dict() for t in tasks]}}
