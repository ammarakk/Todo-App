# Data Model: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot
**Phase**: Phase 1 - Design & Contracts
**Date**: 2025-01-25

## Overview

This document defines the database schema for Phase III, extending the Phase II Todo application with conversational AI memory. Two new tables are added: `Conversation` and `Message`.

---

## Entities

### 1. Conversation

**Purpose**: Represents a chat session between a user and the AI assistant. Stores metadata for the conversation and serves as the parent for all messages in that session.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier for the conversation |
| `user_id` | UUID | FOREIGN KEY → User.id, NOT NULL, INDEXED | User who owns this conversation |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was created |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `idx_conversation_user_id` on `(user_id)` for fast user conversation lookup

**Relationships**:
- **Belongs To**: User (many-to-one: one user has many conversations)
- **Has Many**: Messages (one-to-many: one conversation has many messages)

**Validation Rules**:
- `user_id` MUST reference an existing User in the database
- `updated_at` MUST be automatically updated on new message creation

**SQL Definition**:
```sql
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
```

**SQLModel Definition** (Python):
```python
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 2. Message

**Purpose**: Represents a single interaction within a conversation. Stores the content, role (user/assistant/tool), and optional tool execution details.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier for the message |
| `conversation_id` | UUID | FOREIGN KEY → Conversation.id, NOT NULL, INDEXED | Conversation this message belongs to |
| `role` | ENUM | NOT NULL | Role of the message sender: `user`, `assistant`, or `tool` |
| `content` | TEXT | NOT NULL (for role=user/assistant) | Message content (user input or AI response) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the message was created |
| `tool_calls` | JSONB | NULL, OPTIONAL | Array of MCP tool calls made by the AI |

**Indexes**:
- `idx_message_conversation_id` on `(conversation_id, created_at DESC)` for ordered message retrieval

**Relationships**:
- **Belongs To**: Conversation (many-to-one: one conversation has many messages)

**Validation Rules**:
- `conversation_id` MUST reference an existing Conversation in the database
- `role` MUST be one of: `user`, `assistant`, `tool`
- `content` MUST be non-empty for role=`user` or role=`assistant`
- `content` MAY be null for role=`tool` (tool results in `tool_calls` array)
- `tool_calls` MUST be valid JSON if present (array of tool call objects)

**tool_calls JSONB Structure**:
```json
[
  {
    "tool": "add_task",
    "parameters": {
      "user_id": "uuid",
      "title": "Buy milk"
    },
    "result": {
      "task_id": 123,
      "title": "Buy milk",
      "status": "pending"
    }
  }
]
```

**SQL Definition**:
```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'tool');

CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tool_calls JSONB
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id, created_at DESC);
```

**SQLModel Definition** (Python):
```python
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON, Enum as SQLEnum
import enum

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole)))
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

### 3. Todo (Existing - Phase II)

**Purpose**: Represents a task. Unchanged from Phase II, but accessed via MCP tools only in Phase III.

**Phase III Changes**: None. Existing schema preserved.

**Access Control**:
- All MCP tools MUST filter by `user_id` before returning or modifying todos
- AI agent MUST NOT access todos directly from database

---

### 4. User (Existing - Phase II)

**Purpose**: Represents a user account. Unchanged from Phase II.

**Phase III Changes**: None. Existing schema and authentication preserved.

**Relationship** (Added):
- **Has Many**: Conversations (one-to-many: one user has many conversations)

---

## Entity Relationship Diagram

```
User (Phase II)
  ├── Todo (Phase II) - [1:N]
  └── Conversation (Phase III) - [1:N]
       └── Message (Phase III) - [1:N]
```

---

## State Transitions

### Conversation Lifecycle

```
[Created]
    |
    v
[Active] (receives messages)
    |
    v
[Inactive] (no new messages for 30 days - optional archive)
```

**Notes**:
- No explicit deletion (conversations archived if inactive)
- Soft delete possible: add `is_archived` boolean field (Phase IV)

### Message Lifecycle

```
[Created] (immutable)
```

**Notes**:
- Messages are NEVER modified after creation (append-only)
- Edits not supported (create new message for correction)
- Deletion via cascade when parent conversation deleted

---

## Validation Rules Summary

### Conversation
- ✅ `id` is unique UUID
- ✅ `user_id` references existing User
- ✅ `created_at` <= `updated_at`
- ✅ One active conversation per user (enforced at application level)

### Message
- ✅ `id` is unique UUID
- ✅ `conversation_id` references existing Conversation
- ✅ `role` is valid enum value
- ✅ `content` non-empty for role=user/assistant
- ✅ `tool_calls` valid JSON if present
- ✅ Messages ordered by `created_at DESC`

---

## Database Migration Plan

### Migration Script

```python
# backend/scripts/migrate_ai_tables.py
from sqlmodel import SQLModel, create_engine, Session
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
import os

DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate():
    SQLModel.metadata.create_all(engine)
    print("✅ Conversation and Message tables created")

if __name__ == "__main__":
    migrate()
```

### Rollback Plan

```sql
-- WARNING: This deletes all conversation data!
DROP INDEX IF EXISTS idx_message_conversation_id;
DROP INDEX IF EXISTS idx_conversation_user_id;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS conversation;
DROP TYPE IF EXISTS message_role;
```

---

## Performance Considerations

### Query Optimization

**1. Load User's Active Conversation** (with message count):
```sql
SELECT c.*, COUNT(m.id) as message_count
FROM conversation c
LEFT JOIN message m ON c.id = m.conversation_id
WHERE c.user_id = $1
ORDER BY c.updated_at DESC
LIMIT 1;
```
- Uses index: `idx_conversation_user_id`
- Expected latency: <50ms

**2. Load Last 100 Messages** (for AI context):
```sql
SELECT id, role, content, created_at, tool_calls
FROM message
WHERE conversation_id = $1
ORDER BY created_at DESC
LIMIT 100;
```
- Uses index: `idx_message_conversation_id`
- Expected latency: <100ms for 100 messages

**3. Create Conversation** (with initial message):
```sql
BEGIN;
INSERT INTO conversation (user_id) VALUES ($1) RETURNING id;
INSERT INTO message (conversation_id, role, content) VALUES ($2, 'user', $3);
COMMIT;
```
- Transaction ensures atomicity
- Expected latency: <50ms

### Scaling Strategy

- **Current**: 100 concurrent users, 10K messages/conversation
- **Optimization**: Add Redis caching for recent messages (Phase IV)
- **Optimization**: Partition conversations by user_id hash (Phase IV)

---

## Security Considerations

### User Isolation

**CRITICAL**: All queries MUST include user_id filter:

```python
# ❌ WRONG - returns all conversations
conversations = session.query(Conversation).all()

# ✅ CORRECT - returns only user's conversations
conversations = session.query(Conversation)\
    .filter(Conversation.user_id == user_id)\
    .all()
```

### Cascade Delete Behavior

- Deleting a User cascades to Conversations (via `ON DELETE CASCADE`)
- Deleting a Conversation cascades to Messages
- This ensures no orphaned data

### Foreign Key Constraints

- `conversation.user_id` → `user.id` prevents invalid user references
- `message.conversation_id` → `conversation.id` prevents orphaned messages
- Constraints enforced at database level (defense in depth)

---

## Testing Strategy

### Unit Tests

```python
def test_create_conversation():
    conv = Conversation(user_id=user_id)
    session.add(conv)
    session.commit()
    assert conv.id is not None
    assert conv.user_id == user_id

def test_create_message():
    msg = Message(
        conversation_id=conv_id,
        role=MessageRole.USER,
        content="Add a task"
    )
    session.add(msg)
    session.commit()
    assert msg.id is not None
    assert msg.content == "Add a task"
```

### Integration Tests

```python
def test_conversation_with_messages():
    conv = create_conversation(user_id)
    msg1 = create_message(conv.id, "user", "Hello")
    msg2 = create_message(conv.id, "assistant", "Hi there")
    messages = get_messages(conv.id, limit=100)
    assert len(messages) == 2
    assert messages[0].role == MessageRole.ASSISTANT  # DESC order
```

### Load Tests

- Insert 10,000 messages in one conversation
- Verify query time <500ms for last 100 messages
- Verify user conversation lookup <50ms

---

## Future Enhancements (Phase IV+)

1. **Message Summarization**: Auto-summarize old messages to compress context
2. **Conversation Sharing**: Allow users to share task lists (multi-user)
3. **Message Attachments**: Support images/files in messages
4. **Conversation Export**: Export conversation as JSON/markdown
5. **Conversation Search**: Full-text search across conversations
6. **Archival**: Soft-delete old conversations (30+ days inactive)

---

## Next Steps

1. Review and approve data model
2. Create `contracts/chat-api.yaml` with OpenAPI spec
3. Create `contracts/mcp-tools.yaml` with tool schemas
4. Implement migration script
5. Create unit tests for models
6. Proceed to implementation (Phase 2: `/sp.tasks`)
