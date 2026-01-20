# Research: Phase I Technology Decisions

**Phase**: 0 (Research & Decision Making)
**Date**: 2026-01-20
**Status**: Complete

---

## Overview

This document consolidates research findings for all technical decisions required to implement Phase I (Console-Based In-Memory Todo). All "NEEDS CLARIFICATION" items from the plan have been resolved through research and analysis.

---

## Decision 1: Python Version Selection

**Chosen**: Python 3.11+ (3.13 recommended for production)

### Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Python 3.8 | Minimum version, widely available | Missing pattern matching, slower type checking | ❌ Rejected |
| Python 3.11 | Performance improvements (10-60% faster), better error messages | Not as cutting-edge as 3.13 | ⚠️ Acceptable |
| Python 3.13 | Latest stable, best performance, improved type checking | Newer, may require manual install | ✅ **CHOSEN** |

### Rationale

- **Performance**: Python 3.11+ includes significant performance optimizations
- **Type Checking**: Better support for `typing` module enables cleaner domain model code
- **Future-Proof**: Aligns with FastAPI/SQLModel requirements for Phase II
- **Availability**: Python 3.13 is available on all major platforms (Windows, macOS, Linux)

### Alternatives Considered

- **PyPy**: Faster execution but incompatible with some Phase II libraries (FastAPI)
- **Rust/Cython**: Premature optimization, adds complexity, violates "keep it simple" principle

---

## Decision 2: Domain Model Implementation

**Chosen**: Python `dataclasses` from standard library

### Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Plain `dict` | No imports, maximum flexibility | No type safety, no IDE autocomplete | ❌ Rejected |
| `dataclasses` | Standard library, type-safe, clean syntax, `__eq__` auto-generated | Less flexible than `attrs` | ✅ **CHOSEN** |
| `TypedDict` | Type-safe, lightweight | No methods, mutable by default | ❌ Rejected |
| Pydantic v2 | Powerful validation, JSON serialization | External dependency, overkill for in-memory | ❌ Rejected |
| `attrs` | More features than dataclasses | External dependency | ❌ Rejected |

### Rationale

```python
# Proposed Todo entity using dataclass
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TodoStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@dataclass
class Todo:
    id: int
    title: str
    description: str | None
    status: TodoStatus
    created_at: datetime
```

**Benefits**:
- **Standard library**: Zero dependencies, aligns with Phase I scope
- **Type-safe**: IDE autocomplete and type checking work correctly
- **Immutable by default**: Can use `frozen=True` if needed (Phase I allows mutable)
- **Phase II ready**: Easy to migrate to SQLModel (which supports dataclass-like syntax)

### Evolution Path

- **Phase I**: `dataclass` with standard library types
- **Phase II**: Replace with SQLModel base class for database persistence
- **Migration cost**: Minimal - change base class, add table configuration

---

## Decision 3: Storage Mechanism

**Chosen**: Python `list` with auto-incrementing integer counter

### Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| `list` | Simple, maintains insertion order, fast iteration | O(n) lookup by ID | ✅ **CHOSEN** |
| `dict[int, Todo]` | O(1) lookup by ID | Loses insertion order (pre-3.7) | ⚠️ Backup option |
| `deque` | Fast appends/pops from ends | No random access by ID | ❌ Rejected |

### Rationale

```python
# Proposed storage in TodoService
class TodoService:
    def __init__(self):
        self._todos: list[Todo] = []
        self._next_id: int = 1

    def create(self, title: str, description: str | None) -> Todo:
        todo = Todo(
            id=self._next_id,
            title=title,
            description=description,
            status=TodoStatus.PENDING,
            created_at=datetime.now()
        )
        self._todos.append(todo)
        self._next_id += 1
        return todo
```

**Why `list` over `dict`**:
- **Insertion order**: Required by spec FR-005 ("display in insertion order")
- **Simplicity**: For <1000 todos, O(n) lookup is acceptable (< 2ms per search)
- **Performance**: Meets spec SC-004 (1000+ todos without degradation)
- **Migration path**: Easy to add `dict` index in Phase II if needed

### Performance Validation

| Operation | Time Complexity | Estimated Time (1000 todos) |
|-----------|-----------------|----------------------------|
| Create | O(1) append | < 0.1ms |
| List All | O(n) iteration | < 1ms |
| Find by ID | O(n) linear search | < 1ms |
| Update | O(n) find + O(1) update | < 2ms |
| Delete | O(n) find + O(n) shift | < 2ms |

**Conclusion**: All operations meet < 2 second requirement (SC-001).

---

## Decision 4: CLI Framework

**Chosen**: Standard library `input()` + `print()` with optional `rich` for formatting

### Options Considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| `input()`/`print()` | Standard library, zero dependencies | Plain text, no colors | ✅ **CHOSEN** |
| `click` | Powerful CLI framework, subcommands | External dependency, overkill for simple menu | ❌ Rejected |
| `rich` | Beautiful output, tables, progress bars | External dependency | ⚠️ Optional |
| `prompt_toolkit` | Advanced editing, autocomplete | Heavy dependency, overkill | ❌ Rejected |

### Rationale

**Approach**: Build menu loop with standard library, optionally enhance with `rich`

```python
# Proposed menu structure (standard library)
def main():
    while True:
        print("\n=== Todo App ===")
        print("1. Create Todo")
        print("2. List Todos")
        print("3. View Todo")
        print("4. Update Todo")
        print("5. Complete Todo")
        print("6. Delete Todo")
        print("7. Exit")

        choice = input("\nEnter choice (1-7): ")
        # Handle choice...
```

**Benefits**:
- **Zero dependencies**: Aligns with Phase I simplicity principle
- **Learning curve**: Simple for anyone reading the code
- **Phase II**: CLI will be completely removed, no investment lost

**Optional Enhancement** (if time permits):
- Install `rich` for pretty tables when listing todos
- Not required for MVP, but improves UX

---

## Decision 5: Input Validation Strategy

**Chosen**: Helper functions with clear error messages

### Validation Requirements

From specification:
- **FR-002**: Title must be non-empty (not whitespace-only)
- **FR-019**: IDs must be integers
- **Edge cases**: Non-integer IDs, extremely long titles, special characters

### Proposed Implementation

```python
def validate_title(title: str) -> str:
    """Validate and clean todo title."""
    stripped = title.strip()
    if not stripped:
        raise ValueError("Title cannot be empty")
    if len(stripped) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    return stripped

def validate_todo_id(id_str: str) -> int:
    """Validate and convert todo ID from string."""
    try:
        return int(id_str)
    except ValueError:
        raise ValueError("Todo ID must be a number")
```

**Error Handling**:
- Validation errors raise `ValueError` with user-friendly messages
- CLI layer catches exceptions and displays message to user
- Program continues running (FR-014: no crashes)

---

## Decision 6: Separation of Concerns

**Chosen**: Service layer pattern (business logic separate from CLI)

### Architecture

```
┌─────────────────────────────────────────┐
│         CLI Layer (Temporary)           │
│  - Menu loop, input/output formatting   │
│  - Catches validation errors            │
│  - Calls TodoService methods            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│      Service Layer (Permanent)          │
│  - Pure functions for CRUD operations   │
│  - Maintains in-memory todo list        │
│  - No CLI concepts leak here            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Model Layer (Permanent)         │
│  - Todo dataclass with validation       │
│  - TodoStatus enum                      │
└─────────────────────────────────────────┘
```

### Benefits

1. **Phase II evolution**: Replace CLI with FastAPI, keep service/model unchanged
2. **Testability**: Business logic can be tested without CLI
3. **Clarity**: Each layer has single responsibility
4. **Compliance**: Satisfies FR-020 (separation requirement)

---

## Decision 7: Error Handling Strategy

**Chosen**: Exception-based with user-friendly messages

### Requirements

From specification:
- **FR-013**: User-friendly error messages
- **FR-014**: No crashes, program continues
- **FR-003**: All error messages non-technical

### Implementation Strategy

```python
# Custom exceptions for clear error types
class TodoNotFoundError(Exception):
    """Raised when todo ID not found."""

class InvalidTitleError(Exception):
    """Raised when title validation fails."""

# CLI layer catches all exceptions
try:
    todo = service.get_by_id(todo_id)
except TodoNotFoundError as e:
    print(f"❌ {e}")  # User-friendly message
except Exception as e:
    print(f"❌ An error occurred: {e}")  # Fallback
```

**Error Messages**:
- ❌ "Todo not found" (not "IndexError: list index out of range")
- ❌ "Title cannot be empty" (not "ValueError: empty string")
- ❌ "Todo ID must be a number" (not "ValueError: invalid literal for int()")

---

## Decision 8: Timestamp Handling

**Chosen**: `datetime.datetime.now()` with `datetime` module

### Rationale

```python
from datetime import datetime

@dataclass
class Todo:
    created_at: datetime  # Informational only, per spec
```

**Decisions**:
- Use UTC timezone? **No** - Phase I is single-user, local time is fine
- Store as string? **No** - Use `datetime` object for type safety
- Display format? **ISO 8601** or user-friendly string in CLI

**Phase II Consideration**:
- SQLModel supports `datetime` fields natively
- No migration complexity

---

## Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python Version | 3.11+ (3.13 rec) | Performance, type checking, Phase II ready |
| Domain Model | `dataclasses` | Standard library, type-safe, easy migration |
| Storage | `list[Todo]` | Insertion order, simple, meets performance |
| CLI Framework | `input()`/`print()` | Zero deps, CLI is temporary |
| Validation | Helper functions | Clear error messages, reusable |
| Architecture | Service layer | Separation, Phase II ready |
| Error Handling | Exceptions | User-friendly, no crashes |
| Timestamps | `datetime.now()` | Type-safe, SQLModel compatible |

---

## Next Steps

All research complete. Proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` with final entity definitions
2. Create `contracts/todo-operations.md` with operation signatures
3. Write `quickstart.md` with setup instructions
