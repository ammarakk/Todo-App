# Data Model: Phase 5

**Feature**: 007-advanced-cloud-deployment
**Date**: 2026-02-04
**Status**: Final

## Overview

This document defines all data entities for Phase 5, including their fields, relationships, validation rules, and state transitions. All entities are stored in PostgreSQL/Neon with SQLAlchemy ORM.

---

## Entity: Task

**Purpose**: Represents a todo item created by the user via chatbot or UI.

**Schema**:
```python
class Task(Base):
    __tablename__ = "tasks"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Core Fields (Required)
    title: str = Column(String(500), nullable=False)
    status: TaskStatus = Column(Enum(TaskStatus), default=TaskStatus.ACTIVE, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Optional Fields
    description: Optional[str] = Column(Text, nullable=True)
    due_date: Optional[datetime] = Column(DateTime, nullable=True)
    priority: Optional[Priority] = Column(Enum(Priority), nullable=True)
    tags: Optional[JSON] = Column(JSON, nullable=True)  # ["tag1", "tag2"]

    # Reminder Configuration
    reminder_config: Optional[JSON] = Column(JSON, nullable=True)  # {lead_time: "15m", delivery_method: "email"}

    # Recurrence Configuration
    recurrence_rule: Optional[JSON] = Column(JSON, nullable=True)  # {pattern: "daily", interval: 1}

    # Relationships
    user_id: str = Column(String, foreign_key="users.id", nullable=False)  # From Phase III
    reminder_id: Optional[str] = Column(String, foreign_key="reminders.id", nullable=True)
    parent_task_id: Optional[str] = Column(String, nullable=True)  # For recurring series

    # Metadata
    completed_at: Optional[datetime] = Column(DateTime, nullable=True)
```

**Enums**:
```python
class TaskStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DELETED = "deleted"  # Soft delete

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

**Validation Rules**:
- `title`: Required, max 500 chars
- `due_date`: Must be in future (if set)
- `priority`: Must be one of [low, medium, high]
- `tags`: Array of strings, max 10 tags
- `recurrence_rule`: Must include pattern and interval

**State Transitions**:
```
[ACTIVE] → (complete) → [COMPLETED]
[ACTIVE] → (delete) → [DELETED]
[COMPLETED] → (restore) → [ACTIVE]
[DELETED] → (restore) → [ACTIVE]
```

**Indexes**:
- `idx_tasks_user_id`: (user_id) - Filter tasks by user
- `idx_tasks_status`: (status) - Filter active/completed
- `idx_tasks_due_date`: (due_date) - Sort by due date
- `idx_tasks_created_at`: (created_at) - Sort by creation time

---

## Entity: Reminder

**Purpose**: Represents a scheduled notification for a task.

**Schema**:
```python
class Reminder(Base):
    __tablename__ = "reminders"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Core Fields
    task_id: str = Column(String, foreign_key="tasks.id", nullable=False)
    trigger_time: datetime = Column(DateTime, nullable=False)
    status: ReminderStatus = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING, nullable=False)

    # Delivery Configuration
    delivery_method: DeliveryMethod = Column(Enum(DeliveryMethod), nullable=False)
    destination: str = Column(String(500), nullable=False)  # Email address or push token

    # Retry Tracking
    retry_count: int = Column(Integer, default=0, nullable=False)
    last_retry_at: Optional[datetime] = Column(DateTime, nullable=True)

    # Metadata
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at: Optional[datetime] = Column(DateTime, nullable=True)
```

**Enums**:
```python
class ReminderStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class DeliveryMethod(Enum):
    EMAIL = "email"
    PUSH = "push"
```

**Validation Rules**:
- `trigger_time`: Must be in future when created
- `destination`: Valid email format (if email) or non-empty (if push)
- `retry_count`: Max 3 retries

**State Transitions**:
```
[PENDING] → (send success) → [SENT]
[PENDING] → (retry 1) → [PENDING]
[PENDING] → (retry 3 failed) → [FAILED]
[FAILED] → (manual retry) → [PENDING]
```

**Indexes**:
- `idx_reminders_task_id`: (task_id) - Join with tasks
- `idx_reminders_trigger_time`: (trigger_time) - Query due reminders
- `idx_reminders_status`: (status) - Filter pending reminders

---

## Entity: Conversation

**Purpose**: Represents a chat session between user and AI assistant (from Phase III, enhanced).

**Schema**:
```python
class Conversation(Base):
    __tablename__ = "conversations"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Relationships
    user_id: str = Column(String, foreign_key="users.id", nullable=False)

    # Metadata
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at: Optional[datetime] = Column(DateTime, nullable=True)

    # Dapr State Store Key (for caching)
    dapr_state_key: str = Column(String(500), nullable=False)  # "conversation:{id}"
```

**Relationships**:
- One user has many conversations
- One conversation has many messages

**Indexes**:
- `idx_conversations_user_id`: (user_id) - Filter by user
- `idx_conversations_last_message_at`: (last_message_at) - Sort by recent

---

## Entity: Message

**Purpose**: Represents a single message in a conversation (from Phase III).

**Schema**:
```python
class Message(Base):
    __tablename__ = "messages"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Relationships
    conversation_id: str = Column(String, foreign_key="conversations.id", nullable=False)

    # Content
    role: MessageRole = Column(Enum(MessageRole), nullable=False)
    content: str = Column(Text, nullable=False)

    # Metadata
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    # AI Processing Metadata (NEW for Phase V)
    intent_detected: Optional[str] = Column(String(100), nullable=True)  # "create_task", "query_tasks"
    skill_agent_used: Optional[str] = Column(String(100), nullable=True)  # "TaskAgent", "ReminderAgent"
    confidence_score: Optional[float] = Column(Float, nullable=True)  # 0.0-1.0
    processing_time_ms: Optional[int] = Column(Integer, nullable=True)
```

**Enums**:
```python
class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
```

**Relationships**:
- One conversation has many messages

**Indexes**:
- `idx_messages_conversation_id`: (conversation_id) - Load conversation history
- `idx_messages_created_at`: (created_at) - Sort by time

---

## Entity: Event (Kafka Event Log)

**Purpose**: Logs all Kafka events for audit and replay (NEW for Phase V).

**Schema**:
```python
class Event(Base):
    __tablename__ = "events"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Event Metadata
    event_type: str = Column(String(100), nullable=False, index=True)
    topic_name: str = Column(String(100), nullable=False, index=True)
    correlation_id: str = Column(String(100), nullable=False, index=True)

    # Event Payload
    payload: JSON = Column(JSON, nullable=False)

    # Processing Metadata
    source_service: str = Column(String(100), nullable=False)  # "backend", "notification"
    processing_status: EventStatus = Column(Enum(EventStatus), default=EventStatus.PROCESSED, nullable=False)
    error_message: Optional[str] = Column(Text, nullable=True)

    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at: Optional[datetime] = Column(DateTime, nullable=True)
```

**Enums**:
```python
class EventStatus(Enum):
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"
```

**Event Types**:
- `task.created`: New task created
- `task.updated`: Task modified
- `task.completed`: Task marked complete
- `task.deleted`: Task deleted
- `reminder.triggered`: Reminder fired
- `reminder.sent`: Reminder delivered
- `reminder.failed`: Reminder delivery failed
- `recurring.generated`: Next recurring task created
- `audit.logged`: Audit event logged

**Indexes**:
- `idx_events_event_type`: (event_type) - Filter by type
- `idx_events_topic_name`: (topic_name) - Filter by topic
- `idx_events_correlation_id`: (correlation_id) - Trace related events
- `idx_events_created_at`: (created_at) - Time-based queries

---

## Entity: AuditLog

**Purpose**: Immutable audit trail for all system actions (NEW for Phase V).

**Schema**:
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    # Primary Key
    id: str = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Action Details
    entity_type: str = Column(String(100), nullable=False, index=True)  # "Task", "Reminder"
    entity_id: str = Column(String(100), nullable=False, index=True)
    action: str = Column(String(50), nullable=False)  # "CREATE", "UPDATE", "DELETE"

    # Actor
    actor_type: ActorType = Column(Enum(ActorType), nullable=False)
    actor_id: str = Column(String(100), nullable=False)  # user_id or "system"

    # Changes
    old_values: Optional[JSON] = Column(JSON, nullable=True)
    new_values: Optional[JSON] = Column(JSON, nullable=True)

    # Metadata
    timestamp: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    correlation_id: str = Column(String(100), nullable=False, index=True)
```

**Enums**:
```python
class ActorType(Enum):
    USER = "user"
    SYSTEM = "system"
    SERVICE = "service"  # "notification-service", "recurring-service"
```

**Indexes**:
- `idx_audit_entity`: (entity_type, entity_id) - Query entity history
- `idx_audit_actor`: (actor_type, actor_id) - Query user actions
- `idx_audit_timestamp`: (timestamp) - Time-range queries
- `idx_audit_correlation_id`: (correlation_id) - Trace requests

---

## Entity Relationships

```
User (Phase III)
  ├── 1:N → Task
  ├── 1:N → Conversation
  └── 1:N → AuditLog

Task
  ├── N:1 → User
  ├── 1:1 → Reminder (optional)
  ├── 1:1 → Task (parent_task_id, for recurring series)
  └── 1:N → AuditLog

Reminder
  └── N:1 → Task

Conversation
  ├── N:1 → User
  └── 1:N → Message

Message
  └── N:1 → Conversation

Event (standalone, logs all Kafka events)
AuditLog (standalone, logs all actions)
```

---

## Database Schema

**Schemas**:
- `public`: Main application tables (tasks, reminders, conversations, messages, users)
- `audit`: Audit logs (audit_logs, events)

**Migrations**:
- Use Alembic for schema versioning
- All migrations must be reversible
- No data loss migrations (add columns before removing)

---

**Data Model Status**: ✅ Final - Ready for implementation
