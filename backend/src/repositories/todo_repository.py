# Implements: T018
# Phase III - AI-Powered Todo Chatbot
# Todo Repository - Handles all database operations for Todo model

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select, col
from backend.src.models.todo import Todo, Status, Priority
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message


class TodoRepository:
    """
    Repository for Todo CRUD operations.
    Provides data access methods for MCP tools.
    """

    def __init__(self, session: Session, user_id: Optional[UUID] = None):
        self.session = session
        self.user_id = user_id

    def create(
        self,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Todo:
        """
        Create a new todo for the user.

        Args:
            user_id: User who owns this todo
            title: Todo title
            description: Optional detailed description
            priority: Priority level (low, medium, high)
            due_date: Optional due date
            tags: Optional list of tags

        Returns:
            Created Todo object
        """
        todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            priority=Priority(priority),
            due_date=due_date,
            tags=tags or [],
            status=Status.PENDING
        )
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50
    ) -> List[Todo]:
        """
        Get all todos for a user, optionally filtered.

        Args:
            user_id: User ID to fetch todos for
            status: Optional status filter (pending, completed)
            priority: Optional priority filter (low, medium, high)
            limit: Maximum number of todos to return

        Returns:
            List of Todo objects
        """
        query = select(Todo).where(Todo.user_id == user_id)

        if status:
            query = query.where(Todo.status == Status(status))
        if priority:
            query = query.where(Todo.priority == Priority(priority))

        query = query.order_by(col(Todo.created_at).desc()).limit(limit)
        return list(self.session.exec(query).all())

    def get_by_id(self, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Get a specific todo by ID for a user.

        Args:
            todo_id: Todo ID to fetch
            user_id: User ID (for authorization)

        Returns:
            Todo object or None if not found
        """
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.exec(query).first()

    def update(
        self,
        todo_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Todo]:
        """
        Update an existing todo.

        Args:
            todo_id: Todo ID to update
            user_id: User ID (for authorization)
            title: New title
            description: New description
            status: New status
            priority: New priority
            due_date: New due date
            tags: New tags list

        Returns:
            Updated Todo object or None if not found
        """
        todo = self.get_by_id(todo_id, user_id)
        if not todo:
            return None

        if title is not None:
            todo.title = title
        if description is not None:
            todo.description = description
        if status is not None:
            todo.status = Status(status)
            if status == "completed":
                todo.completed_at = datetime.utcnow()
        if priority is not None:
            todo.priority = Priority(priority)
        if due_date is not None:
            todo.due_date = due_date
        if tags is not None:
            todo.tags = tags

        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete(self, todo_id: UUID, user_id: UUID) -> bool:
        """
        Delete a todo.

        Args:
            todo_id: Todo ID to delete
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        todo = self.get_by_id(todo_id, user_id)
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True

    def mark_completed(self, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Mark a todo as completed.

        Args:
            todo_id: Todo ID to complete
            user_id: User ID (for authorization)

        Returns:
            Updated Todo object or None if not found
        """
        return self.update(todo_id, user_id, status="completed")


class ConversationRepository:
    """
    Repository for Conversation and Message operations.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: UUID) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_or_create_conversation(self, user_id: UUID, conversation_id: Optional[UUID] = None) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            user_id: User ID
            conversation_id: Optional conversation ID to fetch

        Returns:
            Conversation object
        """
        if conversation_id:
            query = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = self.session.exec(query).first()
            if conversation:
                return conversation

        # Create new conversation
        return self.create_conversation(user_id)

    def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation to add message to
            role: Message role (user, assistant, tool)
            content: Message content
            tool_calls: Optional tool calls made by AI

        Returns:
            Created Message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_conversation_history(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        """
        Get message history for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages

        Returns:
            List of Message objects ordered by creation time
        """
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(col(Message.created_at).asc()).limit(limit)
        return list(self.session.exec(query).all())


# Export for use in other modules
__all__ = ['TodoRepository', 'ConversationRepository']
