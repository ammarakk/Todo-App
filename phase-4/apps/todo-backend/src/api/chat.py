# Implements: Phase 3 AI Assistant Integration (T005-T018, T030-T034)
# Phase III - AI-Powered Todo Chatbot
# Chat API Endpoint - Full implementation with Qwen and MCP tools

import json
import re
import time
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session
from logging import getLogger

from src.middleware.auth import get_current_user_id
from src.api.deps import get_db
from src.ai.qwen_client import QwenClient
from src.ai.gemini_client import GeminiClient
from src.ai.prompt_builder import PromptBuilder
from src.mcp.server import MCPServer
from src.mcp.registry import initialize_mcp_tools, register_mcp_tools_with_server
from src.repositories.todo_repository import ConversationRepository
from src.core.config import settings


logger = getLogger(__name__)
router = APIRouter(prefix="/api/ai-chat", tags=["AI Chat"])  # Changed from /api/chat for dashboard integration


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User message to send to the AI (English or Urdu)"
    )
    conversation_id: Optional[str] = Field(None, description="Conversation UUID to continue")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    reply: str = Field(..., description="AI response in user's language")
    conversation_id: str = Field(..., description="Conversation UUID")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="MCP tools executed by AI")


def extract_tool_call(ai_response: str) -> Optional[Dict[str, Any]]:
    """
    Extract tool call from AI response.

    The AI may respond with a tool call in format:
    TOOL_CALL: {"tool": "create_task", "parameters": {"title": "..."}}

    Args:
        ai_response: AI response text

    Returns:
        Tool call dict or None
    """
    if "TOOL_CALL:" in ai_response:
        try:
            # Extract JSON after TOOL_CALL:
            tool_call_str = ai_response.split("TOOL_CALL:")[1].strip()
            return json.loads(tool_call_str)
        except (json.JSONDecodeError, IndexError):
            logger.warning("Failed to parse tool call from AI response")
    return None


def sanitize_input(message: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Removes HTML tags, SQL injection patterns, and suspicious characters.

    Args:
        message: Raw user message

    Returns:
        Sanitized message
    """
    # Remove HTML tags
    message = re.sub(r'<[^>]+>', '', message)

    # Remove common SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
        r"(\b(UNION|JOIN|WHERE)\b.*\b(OR|AND)\b)",
        r"(;|\-\-|#|\/\*|\*\/)",
        r"(\bEXEC\b|\bEXECUTE\b)",
    ]
    for pattern in sql_patterns:
        message = re.sub(pattern, '', message, flags=re.IGNORECASE)

    # Remove excessive whitespace
    message = ' '.join(message.split())

    return message.strip()


def get_ai_client():
    """
    Factory function to get the appropriate AI client based on settings.

    Returns:
        AI client instance (QwenClient or GeminiClient) or FallbackClient

    Raises:
        ValueError: If the AI provider is not supported
    """
    provider = settings.ai_provider.lower()

    if provider == 'gemini':
        try:
            logger.info("Using Gemini AI client")
            return GeminiClient()
        except ValueError as e:
            logger.warning(f"Gemini client initialization failed: {e}")
            return FallbackClient()
    elif provider == 'qwen':
        try:
            logger.info("Using Qwen AI client")
            return QwenClient()
        except ValueError as e:
            logger.warning(f"Qwen client initialization failed: {e}")
            return FallbackClient()
    else:
        logger.warning(f"Unknown AI provider '{provider}', using fallback")
        return FallbackClient()


class FallbackClient:
    """Fallback AI client that returns helpful messages when API is not configured"""

    def generate(self, messages: list, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate a fallback response"""
        return "I apologize, but the AI assistant is not configured yet. Please use the manual controls to create and manage your tasks. To enable AI features, the administrator needs to set up the GEMINI_API_KEY secret on HuggingFace."


# T005: AI Command Request Schema for Dashboard Integration
class AICommandRequest(BaseModel):
    """Request model for AI command endpoint (dashboard integration)"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language command from user"
    )
    conversationId: Optional[str] = Field("new", description="Conversation UUID or 'new' to start new")


class AICommandResponse(BaseModel):
    """Response model for AI command endpoint"""
    success: bool = Field(..., description="Whether command executed successfully")
    action: str = Field(..., description="Action executed: create_task, list_tasks, update_task, delete_task, complete_task, clarify")
    message: str = Field(..., description="Human-readable response from AI")
    data: Optional[Dict[str, Any]] = Field(None, description="Action-specific data (e.g., created task, task list)")


@router.post("/command", response_model=AICommandResponse)
def ai_command(
    request: AICommandRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    AI Command Endpoint for Dashboard Integration.

    This endpoint processes natural language commands from the floating AI chat panel,
    executes them via MCP tools, and returns structured responses.

    Flow:
    1. Sanitize input
    2. Verify JWT and extract user_id
    3. Load or create conversation
    4. Build message array with conversation history
    5. Send to Qwen AI model
    6. Parse AI response (action + parameters)
    7. Execute action via MCP tools
    8. Save messages to database
    9. Return structured response

    Args:
        request: AI command request with message
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        AI command response with action, message, and data
    """
    start_time = time.time()
    try:
        # T008: Input sanitization
        sanitized_message = sanitize_input(request.message)
        logger.info(f"AI command from user {user_id}: {sanitized_message[:50]}...")

        user_uuid = UUID(user_id)

        # Initialize repositories and MCP
        conv_repo = ConversationRepository(db)

        # Handle conversation ID
        if request.conversationId == "new":
            # Always create a FRESH conversation for "new" requests
            conversation = conv_repo.create_fresh_conversation(user_uuid)
        else:
            try:
                conversation_uuid = UUID(request.conversationId)
                conversation = conv_repo.get_conversation(conversation_uuid)
                if not conversation or conversation.user_id != user_uuid:
                    # Create new conversation if invalid or belongs to another user
                    conversation = conv_repo.get_or_create_conversation(user_uuid, None)
            except ValueError:
                conversation = conv_repo.get_or_create_conversation(user_uuid, None)

        # Save user message
        conv_repo.add_message(
            conversation_id=conversation.id,
            role="user",
            content=sanitized_message
        )

        # Detect language
        language = PromptBuilder.detect_language(sanitized_message)

        # Load conversation history (last 50 messages for performance)
        history = conv_repo.get_conversation_history(conversation.id, limit=50)
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Initialize AI client (Qwen or Gemini based on settings)
        ai_client = get_ai_client()

        # Initialize MCP server and tools
        mcp_server = MCPServer()
        mcp_tools = initialize_mcp_tools(db, user_uuid)
        register_mcp_tools_with_server(mcp_server, mcp_tools)

        # Build system prompt with tool definitions
        system_prompt = PromptBuilder.build_system_prompt(language=language)

        # Prepare messages for Qwen
        qwen_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Get AI response
        ai_response = ai_client.generate(qwen_messages)

        # Check if AI wants to call a tool
        tool_call = extract_tool_call(ai_response)

        action = "clarify"
        result_data = None
        tool_results = []

        if tool_call:
            # Execute the tool call
            tool_name = tool_call.get("tool")
            logger.info(f"Executing tool: {tool_name}")

            results = execute_tool_calls([tool_call], mcp_server)
            tool_results = results

            # Map tool name to action
            tool_to_action = {
                "create_todo": "create_task",
                "list_todos": "list_tasks",
                "update_todo": "update_task",
                "delete_todo": "delete_task",
                "complete_todo": "complete_task",
                "search_tasks": "search_by_keyword",
                "bulk_complete": "bulk_complete"
            }
            action = tool_to_action.get(tool_name, "clarify")

            # Extract result data
            if results and results[0].get("success"):
                result_data = results[0].get("result")

            # Format tool results for AI
            tool_result_text = json.dumps(results, indent=2)

            # Ask AI to format the tool result for user
            followup_messages = qwen_messages + [
                {"role": "assistant", "content": ai_response},
                {"role": "user", "content": f"Tool executed successfully. Here is the result:\n{tool_result_text}\n\nPlease format this for the user in {language}."}
            ]

            final_response = ai_client.generate(followup_messages)
        else:
            # No tool call, just conversation
            final_response = ai_response
            action = "clarify"

        # Save assistant response
        conv_repo.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=final_response,
            tool_calls={"calls": tool_results} if tool_results else None
        )

        # Log performance
        response_time = time.time() - start_time
        logger.info(f"AI command completed in {response_time:.2f}s: action={action}")

        return AICommandResponse(
            success=True,
            action=action,
            message=final_response,
            data=result_data
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"AI command endpoint error: {str(e)}", exc_info=True)
        # T017: Error handling for AI service failures
        return AICommandResponse(
            success=False,
            action="error",
            message="AI assistant is temporarily unavailable. Please try again or use the manual controls.",
            data=None
        )


# Keep existing standalone chat endpoint for backward compatibility during migration


def execute_tool_calls(
    tool_calls: List[Dict[str, Any]],
    mcp_server: MCPServer
) -> List[Dict[str, Any]]:
    """
    Execute multiple tool calls (synchronous).

    Args:
        tool_calls: List of tool call dicts with 'tool' and 'parameters'
        mcp_server: MCP server instance

    Returns:
        List of tool execution results
    """
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.get("tool")
        parameters = tool_call.get("parameters", {})

        try:
            result = mcp_server.call_tool(tool_name, parameters)
            results.append({
                "tool": tool_name,
                "success": True,
                "result": result
            })
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            results.append({
                "tool": tool_name,
                "success": False,
                "error": str(e)
            })

    return results


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Send message to AI chatbot and receive response.

    Flow:
    1. Verify JWT and extract user_id
    2. Load or create conversation for user
    3. Save user message to database
    4. Build system prompt with tool definitions
    5. Send conversation history to Qwen
    6. Execute MCP tools if requested
    7. Save assistant response to database
    8. Return AI response

    Args:
        request: Chat request with user message
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        Chat response with AI reply
    """
    try:
        user_uuid = UUID(user_id)
        logger.info(f"Chat request from user {user_id}: {request.message[:50]}...")

        # Initialize repositories and MCP
        conv_repo = ConversationRepository(db)
        conversation = conv_repo.get_or_create_conversation(
            user_uuid,
            UUID(request.conversation_id) if request.conversation_id else None
        )

        # Save user message
        conv_repo.add_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )

        # Detect language
        language = PromptBuilder.detect_language(request.message)

        # Load conversation history
        history = conv_repo.get_conversation_history(conversation.id)
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Initialize AI client (Qwen or Gemini based on settings)
        ai_client = get_ai_client()

        # Initialize MCP server and tools
        mcp_server = MCPServer()
        mcp_tools = initialize_mcp_tools(db, user_uuid)
        register_mcp_tools_with_server(mcp_server, mcp_tools)

        # Build system prompt with tool definitions
        system_prompt = PromptBuilder.build_system_prompt(language=language)

        # Prepare messages for Qwen
        qwen_messages = [
            {"role": "system", "content": system_prompt},
            *messages[-10:]  # Last 10 messages for context
        ]

        # Get AI response
        ai_response = ai_client.generate(qwen_messages)

        # Check if AI wants to call a tool
        tool_call = extract_tool_call(ai_response)

        tool_results = []
        final_response = ai_response

        if tool_call:
            # Execute the tool call
            logger.info(f"Executing tool call: {tool_call['tool']}")
            results = execute_tool_calls([tool_call], mcp_server)
            tool_results = results

            # Format tool results for AI
            tool_result_text = json.dumps(results, indent=2)

            # Ask AI to format the tool result for user
            followup_messages = qwen_messages + [
                {"role": "assistant", "content": ai_response},
                {"role": "user", "content": f"Tool executed successfully. Here is the result:\n{tool_result_text}\n\nPlease format this for the user in {language}."}
            ]

            final_response = ai_client.generate(followup_messages)

        # Save assistant response
        conv_repo.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=final_response,
            tool_calls={"calls": tool_results} if tool_results else None
        )

        return ChatResponse(
            reply=final_response,
            conversation_id=str(conversation.id),
            tool_calls=tool_results if tool_results else None
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Health check endpoint for chat API"""
    return {"status": "healthy", "service": "chat-api"}
