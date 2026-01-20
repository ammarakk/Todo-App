---
id: 002
title: Phase 1 Architectural Design
stage: plan
date: 2026-01-20
surface: agent
model: claude-sonnet-4-5
feature: phase-1-console
branch: phase-1-console
user: User
command: /sp.plan
labels: ["phase1","architecture","design","python","console","in-memory"]
links:
  spec: specs/phase-1-console/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-1-console/plan.md (created, 191 lines - technical context, constitution check, project structure)
  - specs/phase-1-console/research.md (created, Phase 0: 8 technical decisions with rationale)
  - specs/phase-1-console/data-model.md (created, Phase 1: Todo entity definition, validation rules, state transitions)
  - specs/phase-1-console/contracts/todo-operations.md (created, Phase 1: 6 CRUD operation contracts with signatures and behaviors)
  - specs/phase-1-console/quickstart.md (created, Phase 1: Setup guide, usage examples, testing instructions)
  - CLAUDE.md (updated with Python 3.11+ and in-memory storage context)
tests: []
---

## Prompt

```text
# Phase 1: In-Memory Python Console Todo App Plan
@phase1-console

## Goal
Build a CLI-based todo application that stores tasks in memory. No persistent database yet. Implement all Basic Level features using Spec-Driven Development (Claude Code + Spec-Kit Plus).

## Features
- Add Task
- Delete Task
- Update Task
- View Task List
- Mark as Complete

## Tasks

### Task 1: Project Setup
- Initialize Python project structure
  - /src folder
  - main.py entry point
- Setup virtual environment (venv or pipenv)
- Install required packages (click, datetime, typing, rich for CLI formatting optional)
- Create CLAUDE.md instructions in root
- Verify Python 3.13+ compatibility

### Task 2: Task Model
- Define in-memory task structure
  - Fields: id, title, description, completed, created_at, updated_at
- Implement auto-increment ID
- Ensure clean data types (string, bool, datetime)
- Create task list storage (list/dict)

### Task 3: Add Task CLI Command
- Input: title (required), description (optional)
- Validation: title length 1-200 chars, description max 1000 chars
- Append new task to in-memory storage
- Print confirmation message

### Task 4: View Tasks CLI Command
- List all tasks with:
  - ID, title, status (complete/incomplete), created_at
- Support optional filter by completion status
- Display empty list message if no tasks

### Task 5: Update Task CLI Command
- Input: task ID, new title (optional), new description (optional)
- Validation: ID exists, title/description within limits
- Update fields in in-memory storage
- Print confirmation with updated task details

### Task 6: Delete Task CLI Command
- Input: task ID
- Validation: ID exists
- Remove task from in-memory storage
- Print confirmation message

### Task 7: Mark as Complete CLI Command
- Input: task ID
- Validation: ID exists
- Toggle `completed` boolean
- Print confirmation message

### Task 8: CLI UX & Navigation
- Menu-based or command-based interface
- Commands:
  - add, view, update, delete, complete, exit
- Provide help text and clear instructions

### Task 9: Testing
- Manual CLI tests for all commands
- Ensure proper input validation, error handling, and confirmations
- Test edge cases: empty title, invalid ID, duplicate IDs

### Task 10: Documentation
- README.md setup instructions
- CLAUDE.md instructions for spec-driven workflow
- Sample commands and output examples

## Milestones
1. Project setup + Task model complete
2. Add/View/Update/Delete/Complete commands working
3. CLI UX polished with help text
4. Testing passed for all features
5. Documentation complete

## Next Steps After Phase 1
- Phase-2: Convert CLI app into Full-Stack Web App
- Ensure data model compatibility with SQLModel/Neon DB
- Prepare specs for frontend UI and API endpoints
```

## Response snapshot

Successfully completed Phase 0 (Research) and Phase 1 (Design & Contracts) for Phase I console-based in-memory todo application.

**Phase 0: Research & Decision Making** (`research.md` - 8 major decisions):
1. Python Version: 3.11+ (3.13 recommended) - Performance, type checking, Phase II ready
2. Domain Model: `dataclasses` from standard library - Zero dependencies, type-safe
3. Storage: Python `list` with auto-increment counter - Insertion order, < 2ms operations
4. CLI Framework: Standard library `input()`/`print()` - Zero deps, CLI is temporary
5. Input Validation: Helper functions with clear error messages - User-friendly
6. Separation: Service layer pattern - Business logic independent of CLI
7. Error Handling: Exception-based with custom exceptions - No crashes
8. Timestamps: `datetime.now()` - Type-safe, SQLModel compatible

**Phase 1: Design & Contracts** (3 core documents):

1. **Data Model** (`data-model.md`):
   - Todo entity: `id`, `title`, `description`, `status`, `created_at`
   - TodoStatus enum: PENDING, COMPLETED
   - Validation rules for all attributes
   - One-way state transition: PENDING → COMPLETED
   - Phase II migration path to SQLModel documented

2. **Operation Contracts** (`contracts/todo-operations.md`):
   - 6 CRUD operations with complete signatures:
     - `create_todo(title, description) -> Todo`
     - `list_todos() -> list[Todo]`
     - `get_todo_by_id(todo_id) -> Todo`
     - `update_todo(todo_id, title, description) -> Todo`
     - `complete_todo(todo_id) -> Todo`
     - `delete_todo(todo_id) -> None`
   - Exception hierarchy: TodoError, InvalidTitleError, TodoNotFoundError, AlreadyCompletedError
   - Pre-conditions and post-conditions for each operation
   - Performance analysis: O(n) acceptable for Phase I, O(1) in Phase II with DB

3. **Quickstart Guide** (`quickstart.md`):
   - Prerequisites (Python 3.11+)
   - Installation instructions
   - Usage examples for all 6 operations
   - Error handling examples
   - Manual testing checklist
   - Architecture diagram
   - Troubleshooting guide

**Implementation Plan** (`plan.md` - 191 lines):
- Technical Context: Language, dependencies, storage, testing, platform, performance goals
- Constitution Check: ✅ ALL GATES PASSED
  - Phase I compliance verified (single-user, in-memory, no DB/auth/AI)
  - Forward-compatibility validated (CLI replaceable, no framework assumptions)
  - Enforcement hierarchy satisfied
- Project Structure: `src/models/`, `src/services/`, `src/cli/` separation documented
- Complexity Tracking: No violations, no premature abstractions
- Evolution path to Phase II (REST API) clearly defined

**Agent Context Updated**:
- CLAUDE.md updated with Python 3.11+ and in-memory storage context
- Ready for `/sp.implement` to generate code

## Outcome

- ✅ Impact: Complete architectural design establishes technical foundation with all constitutional requirements satisfied and forward-compatibility guaranteed for Phase II evolution
- 🧪 Tests: N/A (planning phase - testing comes during implementation)
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, contracts/todo-operations.md, quickstart.md) + updated CLAUDE.md with Phase I tech stack
- 🔁 Next prompts: `/sp.tasks` to generate actionable implementation task list, then `/sp.implement` to generate actual code
- 🧠 Reflection: Research phase resolved all technical decisions with clear rationale (Python dataclasses, list storage, service layer pattern). Design phase produced contracts that enable independent CLI and business logic evolution. Constitution check confirmed zero violations - Phase I scope strictly enforced with clean migration path to Phase II REST API.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution compliance check PASSED (all 8 Phase I requirements), forward-compatibility validation PASSED (5 evolution requirements), complexity check PASSED (no violations)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to convert architectural design into actionable, dependency-ordered implementation tasks that can be executed via `/sp.implement`
