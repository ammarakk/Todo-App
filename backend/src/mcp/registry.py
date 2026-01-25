# Implements: T023
# Phase III - AI-Powered Todo Chatbot
# MCP Registry - Initialize and register all MCP tools

from uuid import UUID
from sqlmodel import Session
from backend.src.mcp.server import MCPServer
from backend.src.mcp.tools import MCPTools
from backend.src.repositories.todo_repository import TodoRepository


def initialize_mcp_tools(session: Session, user_id: UUID) -> MCPTools:
    """
    Initialize MCP tools and register them with the MCP server.

    Args:
        session: Database session
        user_id: Current user's ID

    Returns:
        MCPTools instance with all tools registered
    """
    # Create repository with user context
    todo_repo = TodoRepository(session=session, user_id=user_id)

    # Create MCP tools instance
    mcp_tools = MCPTools(todo_repository=todo_repo, user_id=user_id)

    return mcp_tools


def register_mcp_tools_with_server(mcp_server: MCPServer, mcp_tools: MCPTools):
    """
    Register all MCP tools with the MCP server.

    Args:
        mcp_server: MCP server instance
        mcp_tools: MCP tools instance
    """
    # Register create_task tool
    mcp_server.register_tool(
        name="create_task",
        func=mcp_tools.create_task,
        description="Create a new task with title, description, priority, due date, and tags"
    )

    # Register list_tasks tool
    mcp_server.register_tool(
        name="list_tasks",
        func=mcp_tools.list_tasks,
        description="List all tasks for the current user, optionally filtered by status or priority"
    )

    # Register update_task tool
    mcp_server.register_tool(
        name="update_task",
        func=mcp_tools.update_task,
        description="Update an existing task's title, description, status, priority, due date, or tags"
    )

    # Register delete_task tool
    mcp_server.register_tool(
        name="delete_task",
        func=mcp_tools.delete_task,
        description="Delete a task by its ID"
    )

    # Register complete_task tool
    mcp_server.register_tool(
        name="complete_task",
        func=mcp_tools.complete_task,
        description="Mark a task as completed"
    )


# Export for use in other modules
__all__ = ['initialize_mcp_tools', 'register_mcp_tools_with_server']
