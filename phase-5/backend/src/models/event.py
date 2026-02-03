"""
Event and Audit Log Models
"""
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Event(BaseModel):
    """Kafka event tracking for at-least-once delivery"""
    __tablename__ = "events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_service: Mapped[str] = mapped_column(String(100), nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, event_type={self.event_type}, status={self.processing_status})>"


class AuditLog(BaseModel):
    """Audit trail for all system changes"""
    __tablename__ = "audit_logs"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    old_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, entity_type={self.entity_type}, action={self.action})>"
