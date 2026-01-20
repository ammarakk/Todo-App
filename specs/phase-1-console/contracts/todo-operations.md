# Contracts: Todo CRUD Operations

**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-20
**Status**: Final

---

## Overview

This document defines the business operation contracts for Todo CRUD. These contracts are implemented by `TodoService` and invoked by the CLI layer (Phase I) or REST API layer (Phase II).

**Important**: These are **business operation contracts**, NOT REST API endpoints. The CLI/FastAPI layers are thin wrappers around these operations.

---

## Operation Signatures

### Create Todo

```python
def create_todo(title: str, description: str | None) -> Todo:
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
```

**Mapping to User Stories**: US-1 (Create Todo)

**Mapping to Functional Requirements**: FR-001, FR-002, FR-003, FR-004

**Behavior**:
1. Validate `title` is non-empty after stripping whitespace
2. Validate `title` length ≤ 200 characters
3. Validate `description` length ≤ 1000 characters (if provided)
4. Assign `id = self._next_id` and increment counter
5. Set `status = TodoStatus.PENDING`
6. Set `created_at = datetime.now()`
7. Append to in-memory list
8. Return new `Todo` object

**Edge Cases**:
- Empty title → Raise `InvalidTitleError`
- Whitespace-only title → Raise `InvalidTitleError`
- Title > 200 chars → Raise `InvalidTitleError`
- Description > 1000 chars → Raise `InvalidDescriptionError`
- Description = `None` → Valid, store as `None`

---

### List Todos

```python
def list_todos() -> list[Todo]:
    """List all todos in insertion order.

    Returns:
        list[Todo]: All todos, ordered by creation time (insertion order)
                    Returns empty list if no todos exist
    """
```

**Mapping to User Stories**: US-2 (List Todos)

**Mapping to Functional Requirements**: FR-005, FR-006

**Behavior**:
1. Return internal list (or copy) of all todos
2. Order is guaranteed to be insertion order (Python `list` preserves order)
3. If no todos exist, return empty list `[]`

**Edge Cases**:
- No todos → Return `[]` (CLI layer displays "No todos found")
- 1000+ todos → Return all (performance tested per SC-004)

**Note**: Phase I does not support filtering by status (can be added in Phase II)

---

### View Todo by ID

```python
def get_todo_by_id(todo_id: int) -> Todo:
    """Get a specific todo by ID.

    Args:
        todo_id: Integer ID of todo to retrieve

    Returns:
        Todo: The todo with matching ID

    Raises:
        TodoNotFoundError: If no todo exists with given ID
    """
```

**Mapping to User Stories**: US-3 (View Todo Details)

**Mapping to Functional Requirements**: FR-007

**Behavior**:
1. Search internal list for todo with matching `id`
2. If found, return `Todo` object
3. If not found, raise `TodoNotFoundError`

**Edge Cases**:
- ID not found → Raise `TodoNotFoundError`
- Multiple todos with same ID → Impossible (auto-increment guarantees uniqueness)

---

### Update Todo

```python
def update_todo(todo_id: int, title: str | None = None, description: str | None = None) -> Todo:
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
```

**Mapping to User Stories**: US-4 (Update Todo)

**Mapping to Functional Requirements**: FR-008, FR-009

**Behavior**:
1. Validate `todo_id` exists (raise `TodoNotFoundError` if not)
2. If `title` is provided (not `None`), validate and update
3. If `description` is provided (not `None`), validate and update
4. Mutate todo in place or replace in list
5. Return updated `Todo` object

**Edge Cases**:
- ID not found → Raise `TodoNotFoundError`
- Empty title → Raise `InvalidTitleError`
- Both `title` and `description` are `None` → No-op, return existing todo unchanged
- Title = `""` (empty string) → Raise `InvalidTitleError`
- Title = `"   "` (whitespace) → Raise `InvalidTitleError`

**Note**: Does NOT allow updating `status` (use `complete_todo` for that)

---

### Complete Todo

```python
def complete_todo(todo_id: int) -> Todo:
    """Mark a todo as completed.

    Args:
        todo_id: Integer ID of todo to mark complete

    Returns:
        Todo: Updated todo with COMPLETED status

    Raises:
        TodoNotFoundError: If no todo exists with given ID
        AlreadyCompletedError: If todo is already in COMPLETED status
    """
```

**Mapping to User Stories**: US-5 (Complete Todo)

**Mapping to Functional Requirements**: FR-010, FR-011

**Behavior**:
1. Validate `todo_id` exists (raise `TodoNotFoundError` if not)
2. Check current status
3. If `PENDING`, transition to `COMPLETED`
4. If `COMPLETED`, raise `AlreadyCompletedError` (one-way transition only)
5. Return updated `Todo` object

**Edge Cases**:
- ID not found → Raise `TodoNotFoundError`
- Already completed → Raise `AlreadyCompletedError`
- Re-completing → Not allowed (per FR-011)

**State Transition**:
```
PENDING → COMPLETED ✅ Allowed
COMPLETED → COMPLETED ❌ Raises AlreadyCompletedError
COMPLETED → PENDING ❌ Not allowed (no reversion)
```

---

### Delete Todo

```python
def delete_todo(todo_id: int) -> None:
    """Delete a todo by ID.

    Args:
        todo_id: Integer ID of todo to delete

    Returns:
        None

    Raises:
        TodoNotFoundError: If no todo exists with given ID
    """
```

**Mapping to User Stories**: US-6 (Delete Todo)

**Mapping to Functional Requirements**: FR-012

**Behavior**:
1. Search internal list for todo with matching `id`
2. If not found, raise `TodoNotFoundError`
3. Remove todo from list (shift subsequent elements)
4. Return `None`

**Edge Cases**:
- ID not found → Raise `TodoNotFoundError`
- Deleting already deleted ID → Raise `TodoNotFoundError` (idempotent check)
- Deleting from empty list → Raise `TodoNotFoundError`

**Note**: Does NOT return deleted todo (API design choice, simplifies error handling)

---

## Exception Hierarchy

```python
# Base exception for all todo-related errors
class TodoError(Exception):
    """Base exception for todo operations."""
    pass

# Validation errors
class InvalidTitleError(TodoError):
    """Raised when title validation fails."""
    pass

class InvalidDescriptionError(TodoError):
    """Raised when description validation fails."""
    pass

# Not found errors
class TodoNotFoundError(TodoError):
    """Raised when todo ID not found."""
    pass

# Business logic errors
class AlreadyCompletedError(TodoError):
    """Raised when attempting to complete an already completed todo."""
    pass
```

**Usage Pattern**:
```python
try:
    todo = service.complete_todo(todo_id)
    print(f"✅ Todo {todo_id} marked complete")
except TodoNotFoundError:
    print(f"❌ Todo not found")
except AlreadyCompletedError:
    print(f"❌ Todo already completed")
except TodoError as e:
    print(f"❌ Error: {e}")
```

---

## Service Interface

Complete `TodoService` class interface:

```python
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

    def create_todo(self, title: str, description: str | None = None) -> Todo: ...
    def list_todos(self) -> list[Todo]: ...
    def get_todo_by_id(self, todo_id: int) -> Todo: ...
    def update_todo(self, todo_id: int, title: str | None = None, description: str | None = None) -> Todo: ...
    def complete_todo(self, todo_id: int) -> Todo: ...
    def delete_todo(self, todo_id: int) -> None: ...
```

---

## Pre-conditions and Post-conditions

### create_todo

**Pre-conditions**:
- Title is non-empty string (1-200 chars)
- Description is `None` or string ≤ 1000 chars

**Post-conditions**:
- New todo added to list
- Todo has unique auto-incremented ID
- Todo status is `PENDING`
- `created_at` is set to current time
- List size increased by 1

---

### list_todos

**Pre-conditions**:
- None

**Post-conditions**:
- Returns list of all todos (may be empty)
- Order is insertion order
- No state modification

---

### get_todo_by_id

**Pre-conditions**:
- `todo_id` is positive integer

**Post-conditions**:
- Returns matching `Todo` object
- Raises `TodoNotFoundError` if ID not found
- No state modification

---

### update_todo

**Pre-conditions**:
- `todo_id` exists in list
- If `title` provided, it is non-empty (1-200 chars)
- If `description` provided, it is ≤ 1000 chars

**Post-conditions**:
- Todo's fields are updated with new values
- Other fields (`id`, `status`, `created_at`) unchanged
- Returns updated `Todo` object
- List size unchanged (mutation in place)

---

### complete_todo

**Pre-conditions**:
- `todo_id` exists in list
- Todo status is `PENDING`

**Post-conditions**:
- Todo status changed to `COMPLETED`
- Other fields unchanged
- Returns updated `Todo` object
- List size unchanged

---

### delete_todo

**Pre-conditions**:
- `todo_id` exists in list

**Post-conditions**:
- Todo removed from list
- List size decreased by 1
- IDs of remaining todos unchanged (no renumbering)

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| `create_todo` | O(1) append | O(1) new object |
| `list_todos` | O(n) iteration | O(n) return list |
| `get_todo_by_id` | O(n) linear search | O(1) return reference |
| `update_todo` | O(n) find + O(1) update | O(1) in-place mutation |
| `complete_todo` | O(n) find + O(1) update | O(1) in-place mutation |
| `delete_todo` | O(n) find + O(n) shift | O(1) remove reference |

**Bottleneck**: O(n) search for ID-based operations

**Mitigation**:
- Acceptable for Phase I (<1000 todos, < 2ms per search)
- Can add `dict[int, Todo]` index in Phase II if needed
- Database indexing will solve this in Phase II (SQLModel)

---

## Testability

Each operation is designed to be independently testable:

```python
# Example unit test (pseudo-code)
def test_create_todo_with_valid_title():
    service = TodoService()
    todo = service.create_todo("Buy groceries", None)
    assert todo.id == 1
    assert todo.title == "Buy groceries"
    assert todo.status == TodoStatus.PENDING

def test_complete_todo_already_completed():
    service = TodoService()
    todo = service.create_todo("Task", None)
    service.complete_todo(todo.id)
    with pytest.raises(AlreadyCompletedError):
        service.complete_todo(todo.id)
```

---

## Phase II Evolution

**No changes to operation signatures** when migrating to Phase II:

```python
# Phase I: In-memory storage
class TodoService:
    def __init__(self):
        self._todos: list[Todo] = []  # ← In-memory list

# Phase II: Database storage
class TodoService:
    def __init__(self, session: Session):
        self._session = session  # ← SQLModel database session

# Operation signatures remain IDENTICAL
def create_todo(self, title: str, description: str | None) -> Todo: ...
```

**Benefits**:
- CLI/FastAPI layers require zero changes
- Business logic validation remains identical
- Only storage backend implementation changes
