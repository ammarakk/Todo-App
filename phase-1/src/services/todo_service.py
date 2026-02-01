"""Todo business logic service and exceptions."""

from datetime import datetime
from typing import Optional

from ..models.todo import Todo, TodoStatus


# =============================================================================
# Custom Exceptions
# =============================================================================


class TodoError(Exception):
    """Base exception for todo operations."""


class InvalidTitleError(TodoError):
    """Raised when title validation fails."""


class InvalidDescriptionError(TodoError):
    """Raised when description validation fails."""


class TodoNotFoundError(TodoError):
    """Raised when todo ID not found."""


class AlreadyCompletedError(TodoError):
    """Raised when attempting to complete an already completed todo."""


# =============================================================================
# Validation Helpers
# =============================================================================


def validate_title(title: str) -> str:
    """Validate and clean todo title.

    Args:
        title: Raw title input

    Returns:
        Cleaned title (stripped whitespace)

    Raises:
        InvalidTitleError: If title is empty or exceeds 200 characters
    """
    stripped = title.strip()
    if not stripped:
        raise InvalidTitleError("Title cannot be empty")
    if len(stripped) > 200:
        raise InvalidTitleError("Title cannot exceed 200 characters")
    return stripped


def validate_description(description: Optional[str]) -> Optional[str]:
    """Validate todo description.

    Args:
        description: Description input (None or string)

    Returns:
        Validated description

    Raises:
        InvalidDescriptionError: If description exceeds 1000 characters
    """
    if description is None:
        return None
    stripped = description.strip()
    if len(stripped) > 1000:
        raise InvalidDescriptionError("Description cannot exceed 1000 characters")
    return stripped if stripped else None


# =============================================================================
# TodoService Class
# =============================================================================


class TodoService:
    """Business logic for Todo CRUD operations.

    This service is framework-agnostic and will be reused in:
    - Phase I: Invoked by CLI layer
    - Phase II: Invoked by FastAPI endpoints
    - Phase III: Invoked by MCP tools for AI agents
    """

    def __init__(self) -> None:
        """Initialize in-memory storage."""
        self._todos: list[Todo] = []
        self._next_id: int = 1

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    def create_todo(self, title: str, description: Optional[str] = None) -> Todo:
        """Create a new todo with auto-incremented ID.

        Args:
            title: Non-empty string (1-200 characters)
            description: Optional string (max 1000 characters if provided)

        Returns:
            Todo: Newly created todo with PENDING status

        Raises:
            InvalidTitleError: If title is empty or exceeds 200 chars
            InvalidDescriptionError: If description exceeds 1000 chars
        """
        validated_title = validate_title(title)
        validated_description = validate_description(description)

        todo = Todo(
            id=self._next_id,
            title=validated_title,
            description=validated_description,
            status=TodoStatus.PENDING,
            created_at=datetime.now(),
        )

        self._todos.append(todo)
        self._next_id += 1
        return todo

    def list_todos(self) -> list[Todo]:
        """List all todos in insertion order.

        Returns:
            list[Todo]: All todos, ordered by creation time (insertion order)
                        Returns empty list if no todos exist
        """
        return list(self._todos)  # Return a copy to prevent external mutation

    def get_todo_by_id(self, todo_id: int) -> Todo:
        """Get a specific todo by ID.

        Args:
            todo_id: Integer ID of todo to retrieve

        Returns:
            Todo: The todo with matching ID

        Raises:
            TodoNotFoundError: If no todo exists with given ID
        """
        for todo in self._todos:
            if todo.id == todo_id:
                return todo
        raise TodoNotFoundError(f"Todo with ID {todo_id} not found")

    def update_todo(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Todo:
        """Update an existing todo's title and/or description.

        Args:
            todo_id: Integer ID of todo to update
            title: New title (optional, but must be non-empty if provided)
            description: New description (optional, None means "no change")

        Returns:
            Todo: Updated todo object

        Raises:
            TodoNotFoundError: If no todo exists with given ID
            InvalidTitleError: If title is empty or exceeds 200 chars
            InvalidDescriptionError: If description exceeds 1000 chars
        """
        todo = self.get_todo_by_id(todo_id)

        if title is not None:
            validated_title = validate_title(title)
            todo.title = validated_title

        if description is not None:
            validated_description = validate_description(description)
            todo.description = validated_description

        return todo

    def complete_todo(self, todo_id: int) -> Todo:
        """Mark a todo as completed.

        Args:
            todo_id: Integer ID of todo to mark complete

        Returns:
            Todo: Updated todo with COMPLETED status

        Raises:
            TodoNotFoundError: If no todo exists with given ID
            AlreadyCompletedError: If todo is already in COMPLETED status
        """
        todo = self.get_todo_by_id(todo_id)

        if todo.status == TodoStatus.COMPLETED:
            raise AlreadyCompletedError(f"Todo {todo_id} is already completed")

        todo.status = TodoStatus.COMPLETED
        return todo

    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo by ID.

        Args:
            todo_id: Integer ID of todo to delete

        Returns:
            None

        Raises:
            TodoNotFoundError: If no todo exists with given ID
        """
        todo = self.get_todo_by_id(todo_id)
        self._todos.remove(todo)
