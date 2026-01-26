# Implements: T019-T022
# Phase III - AI-Powered Todo Chatbot
# MCP Tools - Task management operations exposed to Qwen AI

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from src.repositories.todo_repository import TodoRepository


class MCPTools:
    """
    Model Context Protocol (MCP) Tools for Todo Management.
    These tools are registered with the MCP server and exposed to Qwen AI.
    """

    def __init__(self, todo_repository: TodoRepository, user_id: UUID):
        self.repo = todo_repository
        self.user_id = user_id

    async def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> dict:
        """
        Create a new task.

        Args:
            title: Task title (required)
            description: Optional detailed description
            priority: Priority level - low, medium, or high (default: medium)
            due_date: Optional due date in ISO format (e.g., "2026-01-30")
            tags: Optional list of tags for categorization

        Returns:
            Dict with created task details or error message
        """
        try:
            # Parse due date if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    return {"success": False, "error": f"Invalid due date format: {due_date}. Use ISO format like '2026-01-30'"}

            todo = self.repo.create(
                user_id=self.user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                tags=tags
            )

            return {
                "success": True,
                "task": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status.value,
                    "priority": todo.priority.value,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "created_at": todo.created_at.isoformat()
                },
                "message": f"Task '{title}' created successfully!"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}"
            }

    async def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50
    ) -> dict:
        """
        List all tasks for the current user.

        Args:
            status: Optional filter by status - 'pending' or 'completed'
            priority: Optional filter by priority - 'low', 'medium', or 'high'
            limit: Maximum number of tasks to return (default: 50)

        Returns:
            Dict with list of tasks or error message
        """
        try:
            todos = self.repo.get_by_user(
                user_id=self.user_id,
                status=status,
                priority=priority,
                limit=limit
            )

            return {
                "success": True,
                "tasks": [
                    {
                        "id": str(todo.id),
                        "title": todo.title,
                        "description": todo.description,
                        "status": todo.status.value,
                        "priority": todo.priority.value,
                        "due_date": todo.due_date.isoformat() if todo.due_date else None,
                        "tags": todo.tags,
                        "created_at": todo.created_at.isoformat(),
                        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
                    }
                    for todo in todos
                ],
                "count": len(todos),
                "message": f"Found {len(todos)} task(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list tasks: {str(e)}"
            }

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> dict:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update (required)
            title: New title
            description: New description
            status: New status - 'pending' or 'completed'
            priority: New priority - 'low', 'medium', or 'high'
            due_date: New due date in ISO format
            tags: New list of tags

        Returns:
            Dict with updated task details or error message
        """
        try:
            # Parse due date if provided
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    return {"success": False, "error": f"Invalid due date format: {due_date}. Use ISO format like '2026-01-30'"}

            todo = self.repo.update(
                todo_id=UUID(task_id),
                user_id=self.user_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=parsed_due_date,
                tags=tags
            )

            if not todo:
                return {
                    "success": False,
                    "error": f"Task with ID '{task_id}' not found"
                }

            return {
                "success": True,
                "task": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status.value,
                    "priority": todo.priority.value,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "tags": todo.tags,
                    "updated_at": todo.updated_at.isoformat()
                },
                "message": f"Task '{todo.title}' updated successfully!"
            }

        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update task: {str(e)}"
            }

    async def delete_task(self, task_id: str) -> dict:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete (required)

        Returns:
            Dict with success status or error message
        """
        try:
            success = self.repo.delete(
                todo_id=UUID(task_id),
                user_id=self.user_id
            )

            if not success:
                return {
                    "success": False,
                    "error": f"Task with ID '{task_id}' not found"
                }

            return {
                "success": True,
                "message": f"Task '{task_id}' deleted successfully!"
            }

        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete task: {str(e)}"
            }

    async def complete_task(self, task_id: str) -> dict:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete (required)

        Returns:
            Dict with completed task details or error message
        """
        try:
            todo = self.repo.mark_completed(
                todo_id=UUID(task_id),
                user_id=self.user_id
            )

            if not todo:
                return {
                    "success": False,
                    "error": f"Task with ID '{task_id}' not found"
                }

            return {
                "success": True,
                "task": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "status": todo.status.value,
                    "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
                },
                "message": f"Task '{todo.title}' marked as completed!"
            }

        except ValueError:
            return {
                "success": False,
                "error": f"Invalid task ID format: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to complete task: {str(e)}"
            }


# Export for use in other modules
__all__ = ['MCPTools']
