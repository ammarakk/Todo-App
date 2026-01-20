# Quickstart Guide: Phase I Console Todo App

**Phase**: 1 (Design & Contracts)
**Last Updated**: 2026-01-20
**Prerequisites**: Python 3.11+

---

## Overview

This guide helps you set up and run the Phase I console-based todo application. This is a foundational prototype demonstrating the core domain logic with strict separation between business logic and CLI layer.

---

## Prerequisites

### Required

- **Python 3.11+** (3.13 recommended)
  - Verify: `python --version` or `python3 --version`
  - Install: https://www.python.org/downloads/

### Optional

- **rich** (for pretty CLI output)
  - Install: `pip install rich`
  - Not required for MVP, but improves UX

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/ammarakk/Todo-App.git
cd Todo-App
git checkout phase-1-console
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Verify Project Structure

```bash
tree src/
# Expected output:
# src/
# ├── __init__.py
# ├── models/
# │   ├── __init__.py
# │   └── todo.py
# ├── services/
# │   ├── __init__.py
# │   └── todo_service.py
# └── cli/
#     ├── __init__.py
#     └── main.py
```

### Step 4: Run Application

```bash
python main.py
```

You should see the main menu:
```
=== Todo App ===
1. Create Todo
2. List Todos
3. View Todo
4. Update Todo
5. Complete Todo
6. Delete Todo
7. Exit

Enter choice (1-7):
```

---

## Usage Examples

### Example 1: Create Your First Todo

```
Enter choice (1-7): 1

Enter title: Buy groceries
Enter description (optional, press Enter to skip): Milk, eggs, bread

✅ Todo created successfully!
ID: 1
Title: Buy groceries
Status: pending
```

### Example 2: List All Todos

```
Enter choice (1-7): 2

=== Your Todos ===
ID: 1 | Title: Buy groceries | Status: pending
```

### Example 3: View Todo Details

```
Enter choice (1-7): 3

Enter todo ID: 1

=== Todo Details ===
Title: Buy groceries
Description: Milk, eggs, bread
Status: pending
Created: 2026-01-20 15:30:00
```

### Example 4: Update Todo

```
Enter choice (1-7): 4

Enter todo ID: 1
Enter new title (press Enter to keep current): Buy weekly groceries
Enter new description (press Enter to keep current):

✅ Todo updated successfully!
```

### Example 5: Mark Todo as Complete

```
Enter choice (1-7): 5

Enter todo ID: 1

✅ Todo marked as completed!
```

### Example 6: Delete Todo

```
Enter choice (1-7): 6

Enter todo ID: 1

✅ Todo deleted successfully!
```

### Example 7: Exit Application

```
Enter choice (1-7): 7

Goodbye! 👋
```

---

## Error Handling Examples

### Invalid Title (Empty)

```
Enter choice (1-7): 1

Enter title:

❌ Error: Title cannot be empty
```

### Todo Not Found

```
Enter choice (1-7): 3

Enter todo ID: 999

❌ Error: Todo not found
```

### Already Completed

```
Enter choice (1-7): 5

Enter todo ID: 1

❌ Error: Todo is already completed
```

### Invalid Menu Choice

```
Enter choice (1-7): 99

❌ Invalid choice. Please enter a number between 1 and 7.
```

---

## Key Features

### ✅ Implemented

- **Create Todo**: Add tasks with title and optional description
- **List Todos**: View all todos in insertion order
- **View Todo**: See detailed information for a specific todo
- **Update Todo**: Modify title and description
- **Complete Todo**: Mark todos as completed (one-way transition)
- **Delete Todo**: Remove todos from the list

### ✅ Validation

- Title must be non-empty (whitespace-only rejected)
- Title max 200 characters
- Description max 1000 characters (if provided)
- Todo ID must be an integer
- User-friendly error messages (no stack traces)

### ✅ In-Memory Storage

- All data stored in RAM
- Data resets on application exit
- No database or file persistence (per Phase I scope)

---

## Architecture

### Layer Separation

```
┌─────────────────────────────────────┐
│  CLI Layer (src/cli/main.py)        │
│  - Menu loop, input/output          │
│  - Error handling, user messages    │
└──────────────┬──────────────────────┘
               │ Calls
               ▼
┌─────────────────────────────────────┐
│  Service Layer (src/services/)      │
│  - TodoService class                │
│  - Business logic, CRUD operations  │
└──────────────┬──────────────────────┘
               │ Uses
               ▼
┌─────────────────────────────────────┐
│  Model Layer (src/models/)          │
│  - Todo dataclass                   │
│  - TodoStatus enum                  │
└─────────────────────────────────────┘
```

### Key Design Principles

1. **Business Logic Independent**: `TodoService` has zero CLI dependencies
2. **CLI is Temporary**: Can be replaced by REST API in Phase II
3. **No Framework Lock-in**: Uses standard library only
4. **Type-Safe**: Leverages Python type hints for clarity

---

## Manual Testing

### Test All User Stories

**US-1: Create Todo**
```bash
# Test: Create todo with title only
Create Todo → Title: "Test task" → Description: [Enter]
# Expected: Success with ID 1, status pending

# Test: Create todo with title and description
Create Todo → Title: "Test task 2" → Description: "With description"
# Expected: Success with ID 2, status pending

# Test: Create todo with empty title
Create Todo → Title: "   " → Description: [Enter]
# Expected: Error "Title cannot be empty"
```

**US-2: List Todos**
```bash
# Test: List with todos
List Todos
# Expected: Show all todos in insertion order

# Test: List with no todos
Delete all todos → List Todos
# Expected: "No todos found" message
```

**US-3: View Todo**
```bash
# Test: View existing todo
View Todo → ID: 1
# Expected: Show title, description, status

# Test: View non-existent todo
View Todo → ID: 999
# Expected: "Todo not found" error
```

**US-4: Update Todo**
```bash
# Test: Update title
Update Todo → ID: 1 → New title: "Updated task"
# Expected: Title changed successfully

# Test: Update with empty title
Update Todo → ID: 1 → New title: "   "
# Expected: Error "Title cannot be empty"

# Test: Update non-existent todo
Update Todo → ID: 999 → New title: "Test"
# Expected: "Todo not found" error
```

**US-5: Complete Todo**
```bash
# Test: Complete pending todo
Complete Todo → ID: 1
# Expected: Status changed to completed

# Test: Re-complete already completed todo
Complete Todo → ID: 1
# Expected: "Todo already completed" error
```

**US-6: Delete Todo**
```bash
# Test: Delete existing todo
Delete Todo → ID: 1
# Expected: Todo removed from list

# Test: Delete non-existent todo
Delete Todo → ID: 999
# Expected: "Todo not found" error
```

---

## Troubleshooting

### "python: command not found"

**Solution**: Install Python 3.11+ from https://www.python.org/downloads/

### "ModuleNotFoundError: No module named 'src'"

**Solution**: Ensure you're in the repository root directory (where `src/` is located)

### Application crashes with stack trace

**Solution**: This is a bug! Report it with steps to reproduce.
Expected behavior: User-friendly error message, no crash.

### Data persists between runs (unexpected)

**Solution**: This violates Phase I scope. Ensure no file persistence code exists.

---

## Next Steps

### Phase I Completion Checklist

- [ ] All 6 user stories working per acceptance criteria
- [ ] Business logic separated from CLI (code review)
- [ ] User-friendly error messages for all edge cases
- [ ] Application handles 1000+ todos without slowdown
- [ ] Manual testing completed for all operations

### Phase II Preview

After Phase I is complete:
1. Merge `phase-1-console` → `master`
2. Create `phase-2-fullstack` branch
3. Replace CLI with FastAPI REST endpoints
4. Add SQLModel + PostgreSQL (Neon) persistence
5. Add user authentication
6. Build Next.js frontend

**Business logic remains unchanged** - only presentation and storage layers evolve.

---

## Development Commands

### Run Application
```bash
python main.py
```

### Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Install Optional Dependencies
```bash
pip install rich
```

### Check Python Version
```bash
python --version
```

---

## File Reference

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `src/models/todo.py` | Todo entity definition |
| `src/services/todo_service.py` | Business logic CRUD operations |
| `src/cli/main.py` | Menu-driven CLI interface |

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review `specs/phase-1-console/spec.md` for requirements
3. Review `specs/phase-1-console/data-model.md` for entity details
4. Review `specs/phase-1-console/contracts/todo-operations.md` for operation contracts

---

## Constitution Compliance

This phase follows the **Evolution of Todo Constitution**:
- ✅ Spec-Driven Development (Constitution → Specify → Plan → Tasks → Implement)
- ✅ No Manual Coding (all code via `/sp.implement`)
- ✅ Phase I Scope (console, in-memory, single-user)
- ✅ Forward-Compatible (business logic separate from CLI)

**Phase I Definition of Done** (from constitution):
- All 6 user stories implemented and acceptance criteria pass
- Behavior exactly matches specification
- Application is fully in-memory
- No manual code exists
- Business logic separated from CLI
- All error messages user-friendly
- Application handles edge cases gracefully
- Evolution to Phase II architecturally feasible
