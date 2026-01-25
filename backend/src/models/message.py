# Implements: T008
# Phase III - AI-Powered Todo Chatbot
# Message Model - Stores individual chat interactions

from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
import enum


class MessageRole(str, enum.Enum):
    """Role of the message sender"""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(SQLModel, table=True):
    """
    Represents a single interaction within a conversation.

    Attributes:
        id: Unique identifier for the message
        conversation_id: Conversation this message belongs to
        role: Role of the message sender (user/assistant/tool)
        content: Message content (user input or AI response)
        created_at: When the message was created
        tool_calls: Optional array of MCP tool calls made by the AI
    """
    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    role: MessageRole = Field(default=MessageRole.USER)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Relationships (if needed in future)
    # conversation: Optional["Conversation"] = Relationship(back_populates="messages")
