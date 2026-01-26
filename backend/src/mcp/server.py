# Implements: T012
# Phase III - AI-Powered Todo Chatbot
# MCP Server - Model Context Protocol server initialization

from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Model Context Protocol Server for Phase III.

    This server exposes task operations as tools that the AI agent can call.
    All tools enforce user_id isolation to prevent cross-user data access.
    """

    def __init__(self, name: str = "todo-mcp-server"):
        """
        Initialize MCP server.

        Args:
            name: Server name for identification
        """
        self.name = name
        self.tools: Dict[str, Callable] = {}
        logger.info(f"MCP Server '{self.name}' initialized")

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: Optional[str] = None
    ):
        """
        Register an MCP tool with the server.

        Args:
            name: Tool name (e.g., "add_task", "list_tasks")
            func: Synchronous function implementing the tool
            description: Human-readable tool description
        """
        self.tools[name] = func
        logger.info(f"Registered MCP tool: {name} - {description or 'No description'}")

    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool by name (synchronous).

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters (must include user_id)

        Returns:
            Tool execution result as JSON

        Raises:
            ValueError: If tool not found or parameters invalid
            Exception: If tool execution fails
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in MCP server")

        tool_func = self.tools[tool_name]

        logger.info(f"Executing MCP tool: {tool_name} with parameters: {list(parameters.keys())}")

        try:
            result = tool_func(**parameters)
            logger.info(f"Tool '{tool_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {str(e)}")
            raise

    def list_tools(self) -> Dict[str, str]:
        """
        Get list of all registered tools.

        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {name: func.__doc__ or "No description" for name, func in self.tools.items()}


# Global MCP server instance
mcp_server = MCPServer()
