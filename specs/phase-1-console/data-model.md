# Data Model: Phase I — Todo Entity

**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-20
**Status**: Final

---

## Overview

This document defines the canonical data model for Phase I. The `Todo` entity is the foundation for all future phases and must evolve cleanly from in-memory storage (Phase I) to SQLModel database persistence (Phase II).

---

## Entity: Todo

### Purpose

Represents a unit of work that needs to be tracked. This is the core domain entity for the entire system.

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | `int` | Yes | Auto-generated | Unique identifier within runtime, auto-incrementing from 1 |
| `title` | `str` | Yes | N/A | Name of the task, must be non-empty and ≤200 characters |
| `description` | `str \| None` | No | `None` | Optional details about the task, max 1000 characters if provided |
| `status` | `TodoStatus` | Yes | `TodoStatus.PENDING` | Current state: `PENDING` or `COMPLETED` |
| `created_at` | `datetime` | Yes | `datetime.now()` | Timestamp when todo was created (informational only) |

### Python Implementation

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class TodoStatus(Enum):
    """Status of a todo item."""
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Todo:
    """Represents a unit of work to be tracked.

    This entity is designed to evolve cleanly from in-memory storage
    (Phase I) to SQLModel database persistence (Phase II).
    """
    id: int
    title: str
    description: Optional[str]
    status: TodoStatus
    created_at: datetime
```

### Validation Rules

| Attribute | Rule | Error Message |
|-----------|------|---------------|
| `id` | Must be positive integer | "Invalid todo ID" |
| `title` | Must be non-empty after `str.strip()` | "Title cannot be empty" |
| `title` | Length ≤ 200 characters | "Title cannot exceed 200 characters" |
| `description` | If provided, length ≤ 1000 characters | "Description cannot exceed 1000 characters" |
| `status` | Must be `TodoStatus.PENDING` or `TodoStatus.COMPLETED` | "Invalid todo status" |
| `created_at` | Must not be in the future | "Created date cannot be in the future" |

### State Transitions

```
┌─────────────┐
│   PENDING   │ ← Initial state for all new todos
└──────┬──────┘
       │
       │ User marks complete
       │ (one-way transition)
       ▼
┌─────────────┐
│  COMPLETED  │ ← Terminal state (no transition back)
└─────────────┘
```

**Constraints**:
- **Forward-only**: `PENDING` → `COMPLETED` is allowed
- **No reversion**: `COMPLETED` → `PENDING` is NOT allowed (per FR-011)
- **Re-complete prevention**: Attempting to complete an already completed todo returns error

---

## Relationships

**Phase I**: No relationships (single todo list)

**Future Phases**:
- **Phase II**: Add `user_id` foreign key (multi-user support)
- **Phase III**: Add `conversation_id` for AI agent associations
- **Phase V**: Emit `TodoCreated`, `TodoCompleted` events (no changes to entity)

---

## Storage Layout

### Phase I: In-Memory List

```python
# TodoService maintains list of todos
class TodoService:
    def __init__(self):
        self._todos: list[Todo] = []  # Insertion order preserved
        self._next_id: int = 1        # Auto-increment counter
```

**Characteristics**:
- **Insertion order**: Maintained via `list.append()`
- **Lookup by ID**: O(n) linear search (acceptable for <1000 todos)
- **Persistence**: None (all data lost on exit, per FR-016)

### Phase II: SQLModel Table (Future)

```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")  # NEW: Multi-user support
```

**Migration Path**:
1. Change base class from `dataclass` to `SQLModel`
2. Add `Field()` configurations for database mapping
3. Add `user_id` for authentication (Phase II feature)
4. Replace `list[Todo]` with SQLModel `Session` queries

**Zero Business Logic Changes**:
- `TodoService` methods remain identical (only storage backend changes)
- Validation rules stay the same
- CLI/FastAPI interaction unchanged

---

## Operations

See [contracts/todo-operations.md](./contracts/todo-operations.md) for complete operation signatures and behaviors.

---

## JSON Representation (Future Reference)

Not used in Phase I, but documented for Phase II API design:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-20T15:30:00Z"
}
```

---

## Examples

### Example 1: Create Pending Todo

```python
todo = Todo(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    status=TodoStatus.PENDING,
    created_at=datetime(2026, 1, 20, 15, 30, 0)
)
```

### Example 2: Create Todo Without Description

```python
todo = Todo(
    id=2,
    title="Walk the dog",
    description=None,  # Optional field
    status=TodoStatus.PENDING,
    created_at=datetime(2026, 1, 20, 16, 0, 0)
)
```

### Example 3: Completed Todo

```python
todo = Todo(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    status=TodoStatus.COMPLETED,  # Status changed
    created_at=datetime(2026, 1, 20, 15, 30, 0)
)
```

---

## Design Decisions

### Why `dataclass` instead of `dict`?

**Decision**: Use `@dataclass` for type safety and IDE support.

**Rationale**:
- **Type checking**: Catches errors at development time
- **IDE autocomplete**: Improves developer experience
- **Self-documenting**: Explicit field definitions
- **Phase II ready**: Easy migration to SQLModel (similar syntax)

### Why `Optional[str]` for description?

**Decision**: Use `None` for missing description, not empty string.

**Rationale**:
- **Clear intent**: `None` means "not provided", `""` means "provided but empty"
- **Consistency**: Aligns with database NULL convention
- **Validation**: Can check `if todo.description is None` vs `if todo.description`

### Why enum for status?

**Decision**: Use `TodoStatus` enum instead of raw strings.

**Rationale**:
- **Type safety**: Prevents typos (e.g., "pendign" vs "pending")
- **IDE support**: Autocomplete shows only valid values
- **Refactoring**: Easy to add new statuses in future phases
- **Documentation**: Enum definition serves as documentation

---

## Evolution Guarantees

This data model is designed to support evolution through all 5 phases:

✅ **Phase I** (Current): In-memory `dataclass`
✅ **Phase II**: SQLModel with `user_id`, minimal changes to service layer
✅ **Phase III**: No entity changes (AI agents operate via service layer)
✅ **Phase IV**: No entity changes (containerization doesn't affect data)
✅ **Phase V**: No entity changes (events emitted by service layer, not entity)
