# Implements: T023-T029
# Phase III - AI-Powered Todo Chatbot
# Chat API Endpoint - Full implementation with Qwen and MCP tools

import json
import os
import asyncio
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, create_engine
from logging import getLogger

from src.middleware.auth import get_current_user_id
from src.ai.qwen_client import QwenClient
from src.ai.prompt_builder import PromptBuilder
from src.mcp.server import MCPServer
from src.mcp.registry import initialize_mcp_tools, register_mcp_tools_with_server
from src.repositories.todo_repository import ConversationRepository


logger = getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Database setup
DATABASE_URL = os.getenv("NEON_DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)


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


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session


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


async def execute_tool_calls(
    tool_calls: List[Dict[str, Any]],
    mcp_server: MCPServer
) -> List[Dict[str, Any]]:
    """
    Execute multiple tool calls.

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
            result = await mcp_server.call_tool(tool_name, parameters)
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
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
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
        session: Database session

    Returns:
        Chat response with AI reply
    """
    try:
        user_uuid = UUID(user_id)
        logger.info(f"Chat request from user {user_id}: {request.message[:50]}...")

        # Initialize repositories and MCP
        conv_repo = ConversationRepository(session)
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

        # Initialize Qwen client
        qwen_client = QwenClient()

        # Initialize MCP server and tools
        mcp_server = MCPServer()
        mcp_tools = initialize_mcp_tools(session, user_uuid)
        register_mcp_tools_with_server(mcp_server, mcp_tools)

        # Build system prompt with tool definitions
        tool_descriptions = mcp_server.list_tools()
        system_prompt = PromptBuilder.build_system_prompt(
            language=language,
            tools_available=tool_descriptions
        )

        # Prepare messages for Qwen
        qwen_messages = [
            {"role": "system", "content": system_prompt},
            *messages[-10:]  # Last 10 messages for context
        ]

        # Get AI response
        ai_response = await qwen_client.generate(qwen_messages)

        # Check if AI wants to call a tool
        tool_call = extract_tool_call(ai_response)

        tool_results = []
        final_response = ai_response

        if tool_call:
            # Execute the tool call
            logger.info(f"Executing tool call: {tool_call['tool']}")
            results = await execute_tool_calls([tool_call], mcp_server)
            tool_results = results

            # Format tool results for AI
            tool_result_text = json.dumps(results, indent=2)

            # Ask AI to format the tool result for user
            followup_messages = qwen_messages + [
                {"role": "assistant", "content": ai_response},
                {"role": "user", "content": f"Tool executed successfully. Here is the result:\n{tool_result_text}\n\nPlease format this for the user in {language}."}
            ]

            final_response = await qwen_client.generate(followup_messages)

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
async def health_check():
    """Health check endpoint for chat API"""
    return {"status": "healthy", "service": "chat-api"}
