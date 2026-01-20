# Tasks: Phase I — Console-Based In-Memory Todo

**Input**: Design documents from `specs/phase-1-console/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/todo-operations.md

**Tests**: Manual CLI testing per specification (no automated test framework)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Path Conventions

**Single project (console application)**:
- `src/` - All source code
- `main.py` - Application entry point
- `README.md` - Project documentation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Python project structure with src/ directory, __init__.py files, and main.py entry point
- [X] T002 Verify Python 3.11+ compatibility by checking version-specific syntax (dataclasses, match statement, pipe operator for Optional)
- [X] T003 [P] Create .gitignore for Python artifacts (__pycache__, venv, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Define TodoStatus enum in src/models/todo.py with PENDING and COMPLETED values
- [X] T005 [P] Define Todo dataclass in src/models/todo.py with id, title, description, status, created_at attributes
- [X] T006 [P] Define custom exceptions in src/services/todo_service.py: TodoError, InvalidTitleError, InvalidDescriptionError, TodoNotFoundError, AlreadyCompletedError
- [X] T007 Create TodoService class in src/services/todo_service.py with __init__ method initializing _todos list and _next_id counter
- [X] T008 Implement helper validation functions in src/services/todo_service.py: validate_title() and validate_description()
- [X] T009 [P] Create src/cli/main.py module structure with main() function placeholder

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Todo (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new todos with title and optional description

**Independent Test**: Create a todo with title "Test Task" and verify it appears with auto-incremented ID=1 and status="pending"

### Implementation for User Story 1

- [X] T010 [US1] Implement create_todo() method in src/services/todo_service.py with title validation, auto-increment ID, status default to PENDING
- [X] T011 [US1] Implement create_todo CLI command in src/cli/main.py with input prompts for title and description
- [X] T012 [US1] Add error handling in CLI create command to catch InvalidTitleError and display user-friendly message
- [X] T013 [US1] Add success confirmation in CLI create command displaying created todo's ID, title, and status

**Checkpoint**: At this point, users can create todos with independent testable functionality

---

## Phase 4: User Story 2 - List Todos (Priority: P2)

**Goal**: Display all todos in insertion order with ID, title, status, and created_at

**Independent Test**: Create 3 todos and verify they display in insertion order with correct attributes

### Implementation for User Story 2

- [X] T014 [US2] Implement list_todos() method in src/services/todo_service.py returning list of all todos
- [X] T015 [US2] Implement list_todos CLI command in src/cli/main.py displaying each todo with ID, title, status, created_at
- [X] T016 [US2] Add "No todos found" message in CLI list command when list is empty

**Checkpoint**: At this point, users can create todos AND see the full list (Stories 1 and 2 both work)

---

## Phase 5: User Story 3 - View Todo Details (Priority: P3)

**Goal**: Show detailed information for a specific todo by ID including description

**Independent Test**: Create todo with description, view it by ID, verify all fields display correctly

### Implementation for User Story 3

- [X] T017 [US3] Implement get_todo_by_id() method in src/services/todo_service.py with linear search through _todos list
- [X] T018 [US3] Add TodoNotFoundError raising in get_todo_by_id() when ID not found
- [X] T019 [US3] Implement view_todo CLI command in src/cli/main.py prompting for todo ID
- [X] T020 [US3] Add todo details display in CLI view command showing title, description (or "No description"), status, created_at
- [X] T021 [US3] Add error handling in CLI view command to catch TodoNotFoundError and display "Todo not found" message

**Checkpoint**: At this point, users can create, list, and view detailed todo information (Stories 1-3 all work)

---

## Phase 6: User Story 4 - Update Todo (Priority: P4)

**Goal**: Modify an existing todo's title and/or description

**Independent Test**: Create todo, update title, verify change persists and appears in list

### Implementation for User Story 4

- [X] T022 [US4] Implement update_todo() method in src/services/todo_service.py accepting todo_id, optional title, optional description
- [X] T023 [US4] Add validation in update_todo() to validate title if provided (non-empty, max 200 chars)
- [X] T024 [US4] Add validation in update_todo() to validate description if provided (max 1000 chars)
- [X] T025 [US4] Implement update_todo CLI command in src/cli/main.py prompting for ID, new title (press Enter to skip), new description (press Enter to skip)
- [X] T026 [US4] Add error handling in CLI update command for TodoNotFoundError and InvalidTitleError with user-friendly messages
- [X] T027 [US4] Add success confirmation in CLI update command displaying updated todo details

**Checkpoint**: At this point, users can create, list, view, and update todos (Stories 1-4 all work)

---

## Phase 7: User Story 5 - Complete Todo (Priority: P5)

**Goal**: Mark a pending todo as completed (one-way status transition)

**Independent Test**: Create pending todo, mark complete, verify status changes to "completed", attempt to complete again and verify error

### Implementation for User Story 5

- [X] T028 [US5] Implement complete_todo() method in src/services/todo_service.py changing status from PENDING to COMPLETED
- [X] T029 [US5] Add AlreadyCompletedError raising in complete_todo() when todo status is already COMPLETED
- [X] T030 [US5] Implement complete_todo CLI command in src/cli/main.py prompting for todo ID
- [X] T031 [US5] Add error handling in CLI complete command for TodoNotFoundError and AlreadyCompletedError with user-friendly messages
- [X] T032 [US5] Add success confirmation in CLI complete command displaying "Todo marked as completed!"

**Checkpoint**: At this point, users can manage full todo lifecycle (Stories 1-5 all work)

---

## Phase 8: User Story 6 - Delete Todo (Priority: P6)

**Goal**: Remove a todo from the in-memory list

**Independent Test**: Create todo, delete it, verify it no longer appears in list

### Implementation for User Story 6

- [X] T033 [US6] Implement delete_todo() method in src/services/todo_service.py removing todo from _todos list by ID
- [X] T034 [US6] Implement delete_todo CLI command in src/cli/main.py prompting for todo ID
- [X] T035 [US6] Add error handling in CLI delete command for TodoNotFoundError with user-friendly message
- [X] T036 [US6] Add success confirmation in CLI delete command displaying "Todo deleted successfully!"

**Checkpoint**: All user stories should now be independently functional (complete CRUD + lifecycle management)

---

## Phase 9: Main Menu & CLI UX Integration

**Purpose**: Integrate all user stories into cohesive menu-driven interface

- [X] T037 [P] Implement main menu loop in src/cli/main.py displaying 7 options (1-Create, 2-List, 3-View, 4-Update, 5-Complete, 6-Delete, 7-Exit)
- [X] T038 Implement menu choice validation in src/cli/main.py to handle non-integer input and out-of-range choices (1-7)
- [X] T039 Implement menu loop repetition in src/cli/main.py to redisplay menu after each command except Exit
- [X] T040 Implement Exit command in src/cli/main.py with "Goodbye!" message and clean exit
- [X] T041 Add clear section headers and formatting in src/cli/main.py for better UX (=== Todo App ===, === Your Todos ===, etc.)
- [X] T042 Add helper function in src/cli/main.py to format todo display consistently across list and view commands

---

## Phase 10: Validation & Error Handling Polish

**Purpose**: Ensure robust input validation and user-friendly error messages

- [X] T043 Add whitespace-only title validation in validate_title() helper function in src/services/todo_service.py
- [X] T044 Add title length validation (max 200 chars) in validate_title() helper function
- [X] T045 Add description length validation (max 1000 chars) in validate_description() helper function
- [X] T046 Add integer validation for todo ID input in src/cli/main.py to catch ValueError from int() conversion
- [X] T047 Add generic exception handler in src/cli/main.py main() function to catch unexpected errors and display user-friendly message without stack trace
- [X] T048 Test all error paths: empty title, invalid ID, non-integer ID, already completed, todo not found

---

## Phase 11: Documentation

**Purpose**: Complete project documentation for setup and usage

- [X] T049 Create README.md in repository root with project description, prerequisites (Python 3.11+), installation instructions
- [X] T050 Add usage examples to README.md showing sample CLI interactions with create, list, view, update, complete, delete commands
- [X] T051 Add troubleshooting section to README.md covering common issues (python not found, module errors, data persistence expectations)
- [X] T052 Update CLAUDE.md in repository root with Spec-Driven Development workflow notes and Phase I context
- [X] T053 Add architecture diagram to README.md showing CLI layer → Service layer → Model layer separation

---

## Phase 12: Entry Point & Final Integration

**Purpose**: Complete application entry point and final integration

- [X] T054 Implement main.py entry point in repository root importing and calling src.cli.main.main()
- [X] T055 Add if __name__ == "__main__": guard in main.py to allow both direct execution and module import
- [X] T056 Verify all imports work correctly: src.models.todo, src.services.todo_service, src.cli.main
- [X] T057 Run full manual test suite covering all 6 user stories and edge cases
- [X] T058 Verify application restart clears all data (confirm in-memory behavior per spec)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Menu Integration (Phase 9)**: Depends on all user stories being complete
- **Validation Polish (Phase 10)**: Depends on user stories being complete
- **Documentation (Phase 11)**: Can proceed in parallel with implementation
- **Final Integration (Phase 12)**: Depends on all previous phases

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Note**: All user stories are INDEPENDENT and can be developed in parallel after foundational phase!

### Within Each User Story

- Service methods before CLI commands
- Core functionality before error handling
- Success paths before edge cases

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T003)
- All Foundational tasks marked [P] can run in parallel (T004-T006, T009)
- Once Foundational phase completes, all 6 user stories can start in parallel
- Documentation (Phase 11) can run in parallel with user story implementation

---

## Parallel Example: User Story 1

```bash
# Single story tasks (sequential within story):
T010: Implement create_todo service method
T011: Implement create_todo CLI command
T012: Add error handling
T013: Add success confirmation
```

---

## Parallel Example: All User Stories

```bash
# After foundational phase (T007 complete), launch all stories in parallel:

# User Story 1
T010, T011, T012, T013

# User Story 2
T014, T015, T016

# User Story 3
T017, T018, T019, T020, T021

# User Story 4
T022, T023, T024, T025, T026, T027

# User Story 5
T028, T029, T030, T031, T032

# User Story 6
T033, T034, T035, T036
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T010-T013)
4. **STOP and VALIDATE**: Test User Story 1 independently - create todos, verify they appear
5. Deploy/demo if ready

**MVP Result**: Users can create todos (minimum viable product)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Create) → Test independently → MVP! 🎯
3. Add User Story 2 (List) → Test independently → Users can see what they created
4. Add User Story 3 (View) → Test independently → Detailed view available
5. Add User Story 4 (Update) → Test independently → Full CRUD except delete
6. Add User Story 5 (Complete) → Test independently → Status tracking
7. Add User Story 6 (Delete) → Test independently → Complete CRUD lifecycle
8. Add Menu Integration (Phase 9) → Cohesive user experience
9. Add Polish + Docs (Phases 10-12) → Production-ready

**Each story adds value without breaking previous stories**

### Parallel Team Strategy

With multiple developers (if applicable):

1. Team completes Setup + Foundational together
2. Once Foundational (T007) is done:
   - Developer A: User Story 1 (T010-T013)
   - Developer B: User Story 2 (T014-T016)
   - Developer C: User Story 3 (T017-T021)
   - Developer D: User Story 4 (T022-T027)
   - Developer E: User Story 5 (T028-T032)
   - Developer F: User Story 6 (T033-T036)
3. Stories complete and integrate independently
4. Team completes Menu + Polish + Docs together

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundational phase (T004-T009) is CRITICAL - blocks all user stories
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All manual testing per spec (no automated test framework in Phase I)

---

## Summary

- **Total Tasks**: 58
- **Setup**: 3 tasks
- **Foundational**: 6 tasks (BLOCKS all user stories)
- **User Story 1**: 4 tasks
- **User Story 2**: 3 tasks
- **User Story 3**: 5 tasks
- **User Story 4**: 6 tasks
- **User Story 5**: 5 tasks
- **User Story 6**: 4 tasks
- **Menu Integration**: 6 tasks
- **Validation Polish**: 6 tasks
- **Documentation**: 5 tasks
- **Final Integration**: 5 tasks

**Parallel Opportunities**: 17 tasks marked [P] can run in parallel
**Critical Path**: T001 → T007 (Foundational) → T010-T036 (User Stories, can parallelize) → T037-T058 (Integration)
