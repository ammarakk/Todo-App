# Implementation Plan: Phase I — Console-Based In-Memory Todo

**Branch**: `phase-1-console` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/phase-1-console/spec.md`

**Note**: This plan follows Spec-Driven Development (SDD) workflow per project constitution.

---

## Summary

Phase I establishes the architectural foundation for the Evolution of Todo system. This phase builds a simple, in-memory console application that demonstrates core domain logic (Todo CRUD operations) while maintaining strict separation between business logic and presentation layer. The CLI is intentionally temporary and will be replaced by REST APIs in Phase II without requiring business logic changes.

**Primary Requirements**:
- Python-based console application with menu-driven interface
- In-memory storage (no persistence, database, or file I/O)
- Complete CRUD operations: Create, Read, Update, Delete (plus Mark Complete)
- Strict separation: Business logic independent of CLI layer
- User-friendly error handling without crashes

**Success Metrics**:
- All 6 user stories independently testable
- Business logic separated from CLI (verified via code review)
- Zero manual code (all generated via `/sp.implement`)
- Ready for Phase II evolution to REST API

---

## Technical Context

**Language/Version**: Python 3.11+ (3.13 recommended)
- Chosen for: Readability, strong typing support, async-ready for future phases
- Rationale: Aligns with constitution's allowed stack (FastAPI/SQLModel for Phase II)

**Primary Dependencies**:
- **Standard library only**: `datetime`, `typing`, `dataclasses`, `enum`
- **CLI formatting**: Optional - `rich` (if needed for polished output)
- **Avoid**: ORMs, web frameworks, database drivers (per Phase I scope)
- Rationale: Minimize dependencies, avoid premature abstraction

**Storage**: In-memory Python collections (list/dict)
- `TodoService` maintains list of `Todo` entities
- No persistence layer, no file I/O
- Rationale: Constitution Phase I requirement - in-memory only

**Testing**: Manual CLI testing per specification
- No automated test framework required (Phase I)
- Verification via user story acceptance scenarios
- Rationale: Focus on architectural foundation, not test coverage

**Target Platform**: Any platform with Python 3.11+ runtime
- Windows, macOS, Linux
- Terminal/console with stdin/stdout support
- Rationale: Maximum portability, platform-agnostic design

**Project Type**: Single project (console application)
- Source under `src/` with clear separation of concerns
- Tests optional (manual verification per spec)
- Rationale: Simple structure for foundation phase

**Performance Goals**:
- Operation latency: < 2 seconds for any CRUD operation (per SC-001)
- Capacity: 1000+ todos in memory without degradation (per SC-004)
- Startup: Instant (< 1 second to menu display)

**Constraints**:
- **Zero persistence**: All data lost on exit (per FR-016, constitution Phase I)
- **No blocking I/O**: Synchronous operations only (no async needed yet)
- **Memory efficiency**: Single user, no concurrency concerns
- **Deterministic behavior**: No randomness in core logic

**Scale/Scope**:
- Single user session
- In-memory todo list (bounded by available RAM)
- ~500 lines of code including CLI and business logic
- 6 user stories, 20 functional requirements

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase I Compliance Verification

**✅ PASS**: All Phase I constitutional requirements met

| Requirement | Status | Evidence |
|------------|--------|----------|
| Single-user execution | ✅ PASS | Spec FR-015, no multi-user logic in domain model |
| In-memory only | ✅ PASS | FR-015, FR-016, no persistence in scope |
| No database | ✅ PASS | Explicitly out of scope, Python collections only |
| No web/HTTP | ✅ PASS | CLI interface only, no API endpoints |
| No authentication | ✅ PASS | No user concept in domain model, implicit single user |
| No AI/MCP | ✅ PASS | Explicitly out of scope for Phase I |
| No concurrency | ✅ PASS | Single-threaded, synchronous operations |
| Business logic separation | ✅ PASS | FR-020, forward-compatibility requirements enforced |

### Forward-Compatibility Validation

**✅ PASS**: Design allows Phase II evolution without breaking changes

| Evolution Requirement | Design Decision | Status |
|----------------------|-----------------|--------|
| CLI replaceable by REST API | Business logic in `TodoService` (pure functions) | ✅ PASS |
| No framework assumptions | Domain entity uses standard `dataclass` | ✅ PASS |
| No transport layer coupling | Operations independent of input method | ✅ PASS |
| Add users in Phase II | No user concept in current domain model | ✅ PASS |
| Replace in-memory with SQLModel | Storage abstracted behind service interface | ✅ PASS |

### Enforcement Hierarchy

**✅ PASS**: Constitution → Specify → Plan → Tasks → Implementation

- Constitution Phase I rules: ✅ Followed
- Specification requirements: ✅ All 20 FRs addressed
- Plan design: ✅ Aligns with both constitution and spec
- No violations found: **Justification not required**

**Re-check after Phase 1 design**: ✅ PASSED (no design violations detected)

---

## Project Structure

### Documentation (this feature)

```text
specs/phase-1-console/
├── spec.md              # Feature specification (6 user stories, 20 FRs)
├── plan.md              # This file (architecture and technical decisions)
├── research.md          # Phase 0: Technology research and rationale
├── data-model.md        # Phase 1: Todo entity definition and relationships
├── quickstart.md        # Phase 1: Setup and usage instructions
├── contracts/           # Phase 1: Business operation contracts (not REST APIs)
│   └── todo-operations.md  # CRUD operation signatures and behaviors
└── tasks.md             # Phase 2: Implementation tasks (NOT created yet)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── todo.py           # Todo entity (dataclass with id, title, description, status, created_at)
├── services/
│   ├── __init__.py
│   └── todo_service.py   # Business logic: pure functions for CRUD operations
└── cli/
    ├── __init__.py
    └── main.py           # Menu-driven CLI interface (temporary presentation layer)

main.py                    # Application entry point
```

**Structure Decision Rationale**:

1. **Single project layout** (not web/mobile): Phase I is console-only
2. **`models/`** separate from **`services/`**: Enables Phase II to reuse models with FastAPI
3. **`cli/`** isolated: CLI is explicitly temporary, will be removed in Phase II
4. **No tests/ directory**: Manual testing per spec (automated tests optional)

**Evolution Path**:
- Phase I: `src/cli/main.py` → `TodoService` → `Todo` model
- Phase II: `backend/api/` (FastAPI) → `TodoService` (unchanged) → `Todo` model (add SQLModel base)
- Phase III: AI agents invoke MCP tools → `TodoService` (unchanged)

---

## Complexity Tracking

> **No violations requiring justification**

Constitution check passed all gates. No complexity tracking needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Architecture Rationale**:

The design intentionally avoids premature complexity:
- No repository pattern (in-memory list is sufficient)
- No dependency injection (single service, no swapping needed yet)
- No configuration system (no environment-specific logic per Phase I scope)
- No logging framework (stdout only for console app)

These abstractions will be added in later phases when actually needed (e.g., repository pattern in Phase II for database).
