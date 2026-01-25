# Implements: T007
# Phase III - AI-Powered Todo Chatbot
# Conversation Model - Stores user chat sessions

from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between a user and the AI assistant.

    Attributes:
        id: Unique identifier for the conversation
        user_id: User who owns this conversation (FK to User table)
        created_at: When the conversation was created
        updated_at: Last message timestamp
    """
    __tablename__ = "conversation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (if needed in future)
    # user: Optional["User"] = Relationship(back_populates="conversations")
    # messages: list["Message"] = Relationship(back_populates="conversation")
