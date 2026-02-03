"""
Conversation and Message Models
"""
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Text, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Conversation(BaseModel):
    """Chatbot conversation"""
    __tablename__ = "conversations"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    dapr_state_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class Message(BaseModel):
    """Conversation message with AI metadata"""
    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent_detected: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    skill_agent_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
