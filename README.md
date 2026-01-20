# Phase I — Console-Based In-Memory Todo App

**Phase**: I — Foundation
**Branch**: `phase-1-console`
**Status**: Complete ✅

---

## Overview

This is Phase I of the "Evolution of Todo" project - a demonstration of Spec-Driven Development (SDD) building a system that evolves from a simple console application into a cloud-native, AI-driven, event-based distributed platform.

**Current Phase**: In-memory console application (no database, no web, no AI)

**Next Phase**: Phase II will transform this into a full-stack web application with REST APIs and database persistence.

---

## Features

- ✅ Create Todo with title and optional description
- ✅ List all todos in insertion order
- ✅ View detailed todo information
- ✅ Update todo title and description
- ✅ Mark todos as completed (one-way status transition)
- ✅ Delete todos
- ✅ User-friendly error messages
- ✅ Menu-driven CLI interface

---

## Architecture

**Layered Design** (prepared for Phase II evolution):

```
CLI Layer (Temporary)
    ↓ calls
Service Layer (Permanent - Pure Functions)
    ↓ uses
Model Layer (Permanent - Dataclasses)
```

**Key Design Principles**:
- **Business Logic Independent**: `TodoService` has zero CLI dependencies
- **CLI is Temporary**: Can be replaced by REST API in Phase II
- **No Framework Lock-in**: Uses standard library only
- **Type-Safe**: Leverages Python type hints

---

## Prerequisites

- **Python 3.11+** (3.13 recommended)
- No external dependencies required (standard library only)

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

### Step 3: Run Application

```bash
python main.py
```

---

## Usage Examples

### Example 1: Create Your First Todo

```
=== Todo App ===
========================================
1. Create Todo
2. List Todos
3. View Todo
4. Update Todo
5. Complete Todo
6. Delete Todo
7. Exit
========================================

Enter choice (1-7): 1

=== Create Todo ===
Enter title (required): Buy groceries
Enter description (optional, press Enter to skip): Milk, eggs, bread

✅ Todo created successfully!
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: pending
Created: 2026-01-20 16:30:45
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

=== View Todo ===
Enter todo ID: 1

=== Todo Details ===
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: pending
Created: 2026-01-20 16:30:45
```

### Example 4: Complete Todo

```
Enter choice (1-7): 5

=== Complete Todo ===
Enter todo ID: 1

✅ Todo marked as completed!
ID: 1
Title: Buy groceries
Description: Milk, eggs, bread
Status: completed
Created: 2026-01-20 16:30:45
```

---

## Error Handling Examples

### Invalid Title (Empty)

```
Enter choice (1-7): 1

=== Create Todo ===
Enter title (required):

❌ Error: Title cannot be empty.
```

### Todo Not Found

```
Enter choice (1-7): 3

=== View Todo ===
Enter todo ID: 999

❌ Error: Todo with ID 999 not found
```

### Already Completed

```
Enter choice (1-7): 5

=== Complete Todo ===
Enter todo ID: 1

❌ Error: Todo 1 is already completed
```

---

## Project Structure

```
src/
├── models/
│   ├── __init__.py
│   └── todo.py           # Todo dataclass + TodoStatus enum
├── services/
│   ├── __init__.py
│   └── todo_service.py   # Business logic (CRUD operations)
└── cli/
    ├── __init__.py
    └── main.py           # Menu-driven CLI interface

main.py                    # Application entry point
README.md                  # This file
```

---

## Testing

### Manual Testing Checklist

**User Story 1: Create Todo**
- [x] Create todo with title only
- [x] Create todo with title and description
- [x] Reject empty title
- [x] Verify auto-increment ID
- [x] Verify default status is "pending"

**User Story 2: List Todos**
- [x] List displays all todos in insertion order
- [x] Show "No todos found" when empty

**User Story 3: View Todo**
- [x] View existing todo by ID
- [x] Display "No description" if not provided
- [x] Error message for invalid ID

**User Story 4: Update Todo**
- [x] Update title only
- [x] Update description only
- [x] Update both title and description
- [x] Reject empty title update
- [x] Error message for invalid ID

**User Story 5: Complete Todo**
- [x] Mark pending todo as completed
- [x] Error if already completed
- [x] Error for invalid ID

**User Story 6: Delete Todo**
- [x] Delete existing todo
- [x] Verify removed from list
- [x] Error for invalid ID

---

## Limitations (Phase I)

**Intentional Constraints** (per constitution):
- ❌ No database (all data lost on exit)
- ❌ No file persistence
- ❌ No web APIs / HTTP
- ❌ No authentication / authorization
- ❌ No AI, Agents, MCP
- ❌ No multi-user support
- ❌ No configuration files

**Why?** This phase establishes architectural foundation. Future phases will add these capabilities.

---

## Phase II Preview

After Phase I completion:
1. ✅ Merge `phase-1-console` → `master`
2. ✅ Create `phase-2-fullstack` branch
3. 🔄 Replace CLI with FastAPI REST endpoints
4. 🔄 Add SQLModel + PostgreSQL (Neon) persistence
5. 🔄 Add user authentication
6. 🔄 Build Next.js frontend

**Business logic remains unchanged** - only presentation and storage layers evolve!

---

## Development Commands

```bash
# Run application
python main.py

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Check Python version
python --version
```

---

## Troubleshooting

**"python: command not found"**
- Install Python 3.11+ from https://www.python.org/downloads/

**"ModuleNotFoundError: No module named 'src'"**
- Ensure you're in the repository root directory (where `src/` is located)

**Application crashes with stack trace**
- This is a bug! All errors should be user-friendly
- Report the issue with steps to reproduce

---

## Constitution Compliance

This phase follows the **Evolution of Todo Constitution**:
- ✅ Spec-Driven Development (Constitution → Specify → Plan → Tasks → Implement)
- ✅ No Manual Coding (all code generated via `/sp.implement`)
- ✅ Phase I Scope (console, in-memory, single-user)
- ✅ Forward-Compatible (business logic separate from CLI)
- ✅ Stateless Services (service layer is stateless, state in list)

**Phase I Definition of Done**:
- [x] All 6 user stories implemented and acceptance criteria pass
- [x] Behavior exactly matches specification
- [x] Application is fully in-memory
- [x] No manual code exists (all generated via `/sp.implement`)
- [x] Business logic separated from CLI
- [x] All error messages user-friendly
- [x] Application handles edge cases gracefully
- [x] Evolution to Phase II architecturally feasible

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
1. Check this README
2. Review `specs/phase-1-console/spec.md` for requirements
3. Review `specs/phase-1-console/data-model.md` for entity details
4. Review `specs/phase-1-console/contracts/todo-operations.md` for operation contracts
