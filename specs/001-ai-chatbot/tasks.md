# Tasks: AI-Powered Todo Chatbot

**Feature Branch**: `001-ai-chatbot`
**Input**: Design documents from `/specs/001-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

**Tests**: Integration tests included for critical user journeys (bilingual chat, task operations, security isolation)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (Next.js/React)
- **Tests**: `backend/tests/` (pytest)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure for Phase III

- [X] T001 Create backend AI directory structure in backend/src/models/, backend/src/services/, backend/src/api/, backend/src/mcp_tools/
- [ ] T002 [P] Install Python dependencies: pip install fastapi sqlmodel huggingface_hub mcp psycopg2-binary python-jose[cryptography]
- [ ] T003 [P] Install frontend dependencies: npm install axios @types/axios in frontend/
- [ ] T004 [P] Create backend/.env file with NEON_DATABASE_URL, HUGGINGFACE_API_KEY, JWT_SECRET, QWEN_MODEL
- [ ] T005 [P] Create frontend/.env.local file with NEXT_PUBLIC_API_URL=http://localhost:8000
- [X] T006 Create backend/scripts/migrate_ai_tables.py for database migration script

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer (Shared by All Stories)

- [X] T007 Create Conversation model in backend/src/models/conversation.py with id, user_id, created_at, updated_at fields
- [X] T008 Create Message model in backend/src/models/message.py with id, conversation_id, role, content, created_at, tool_calls fields
- [ ] T009 Run database migration to create conversation and message tables in Neon PostgreSQL

### Authentication Layer (Shared by All Stories)

- [X] T010 Implement JWT verification middleware in backend/src/middleware/auth.py that extracts user_id and rejects invalid tokens
- [ ] T011 Register JWT middleware with FastAPI application in backend/main.py

### MCP Server Foundation (Shared by All Stories)

- [X] T012 Initialize Official MCP SDK server in backend/src/services/mcp_server.py with FastAPI integration
- [X] T013 [P] Create MCP tool base schema and error handling utilities in backend/src/mcp_tools/base.py

### Qwen Integration Foundation (Shared by All Stories)

- [X] T014 Create Hugging Face client wrapper in backend/src/services/qwen_client.py with timeout and retry logic
- [X] T015 [P] Create bilingual system prompts (English and Urdu) in backend/src/prompts/system_prompts.py

### Chat API Foundation (Shared by All Stories)

- [X] T016 Create /api/chat endpoint stub in backend/src/api/chat.py with JWT authentication middleware
- [X] T017 [P] Create ChatInterface React component in frontend/src/components/ChatInterface.tsx
- [X] T018 [P] Create chat page in frontend/src/pages/chat.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by conversing with AI in English or Urdu

**Independent Test**: Send "Add a task to buy milk" (English) or "Doodh lene ka task add karo" (Urdu), verify task created with correct title and confirmation in matching language

### Integration Tests for User Story 1

- [ ] T019 [P] [US1] Write integration test for add_task flow in English in backend/tests/integration/test_us1_add_task_english.py
- [ ] T020 [P] [US1] Write integration test for add_task flow in Urdu in backend/tests/integration/test_us1_add_task_urdu.py
- [ ] T021 [P] [US1] Write integration test for missing task title prompt in backend/tests/integration/test_us1_add_task_validation.py

### Implementation for User Story 1

- [ ] T022 [P] [US1] Implement add_task MCP tool in backend/src/mcp_tools/add_task.py with user_id, title, description parameters
- [ ] T023 [P] [US1] Implement task title validation (1-200 chars) in backend/src/mcp_tools/add_task.py
- [ ] T024 [US1] Register add_task tool with MCP server in backend/src/services/mcp_server.py
- [ ] T025 [US1] Implement conversation creation/loading logic in backend/src/services/chat_service.py
- [ ] T026 [US1] Implement message persistence (save user and assistant messages) in backend/src/services/chat_service.py
- [ ] T027 [US1] Implement Qwen prompt builder with conversation history in backend/src/services/chat_service.py
- [ ] T028 [US1] Implement language detection (English vs Urdu) from user message in backend/src/services/chat_service.py
- [ ] T029 [US1] Integrate add_task tool execution with Qwen in backend/src/services/chat_service.py
- [ ] T030 [US1] Connect ChatInterface component to /api/chat endpoint in frontend/src/components/ChatInterface.tsx
- [ ] T031 [US1] Add bilingual error handling for add_task failures in frontend/src/components/ChatInterface.tsx

**Checkpoint**: User Story 1 complete - can add tasks via chat in English and Urdu

---

## Phase 4: User Story 2 - View Tasks via Conversation (Priority: P2)

**Goal**: Users can request to see their tasks through natural language queries

**Independent Test**: Send "Show my tasks" (English) or "Mere tasks dikhao" (Urdu), verify only user's own tasks displayed in matching language

### Integration Tests for User Story 2

- [ ] T032 [P] [US2] Write integration test for list_tasks in English in backend/tests/integration/test_us2_list_tasks_english.py
- [ ] T033 [P] [US2] Write integration test for list_tasks in Urdu in backend/tests/integration/test_us2_list_tasks_urdu.py
- [ ] T034 [P] [US2] Write integration test for empty task list in backend/tests/integration/test_us2_list_tasks_empty.py

### Implementation for User Story 2

- [ ] T035 [P] [US2] Implement list_tasks MCP tool in backend/src/mcp_tools/list_tasks.py with user_id and optional status filter
- [ ] T036 [US2] Register list_tasks tool with MCP server in backend/src/services/mcp_server.py
- [ ] T037 [US2] Integrate list_tasks tool execution with Qwen in backend/src/services/chat_service.py
- [ ] T038 [US2] Add task list display formatting in ChatInterface component in frontend/src/components/ChatInterface.tsx
- [ ] T039 [US2] Handle empty task list response with friendly message in frontend/src/components/ChatInterface.tsx

**Checkpoint**: User Stories 1 AND 2 both work - can add and view tasks via chat

---

## Phase 5: User Story 3 - Delete Tasks via Natural Commands (Priority: P3)

**Goal**: Users can remove tasks by instructing the AI, with ownership verification

**Independent Test**: Send "Delete task 5" (English) or "Task number 2 hata do" (Urdu), verify task deleted with ownership check and confirmation in matching language

### Integration Tests for User Story 3

- [ ] T040 [P] [US3] Write integration test for delete_task with ownership verification in backend/tests/integration/test_us3_delete_task_ownership.py
- [ ] T041 [P] [US3] Write integration test for delete_task non-existent task error in backend/tests/integration/test_us3_delete_task_not_found.py
- [ ] T042 [P] [US3] Write integration test for delete_task cross-user access denial in backend/tests/integration/test_us3_delete_task_security.py

### Implementation for User Story 3

- [ ] T043 [P] [US3] Implement delete_task MCP tool in backend/src/mcp_tools/delete_task.py with user_id and task_id parameters
- [ ] T044 [US3] Implement ownership verification (user_id filtering) in backend/src/mcp_tools/delete_task.py
- [ ] T045 [US3] Add permission denied error for cross-user deletion attempts in backend/src/mcp_tools/delete_task.py
- [ ] T046 [US3] Register delete_task tool with MCP server in backend/src/services/mcp_server.py
- [ ] T047 [US3] Integrate delete_task tool execution with Qwen in backend/src/services/chat_service.py
- [ ] T048 [US3] Add bilingual confirmation messages for task deletion in frontend/src/components/ChatInterface.tsx

**Checkpoint**: User Stories 1, 2, AND 3 all work - can add, view, and delete tasks via chat

---

## Phase 6: User Story 4 - Mark Tasks Complete (Priority: P4)

**Goal**: Users can mark tasks as completed through natural language instructions

**Independent Test**: Send "Mark task 1 as done" (English) or "Pehla task complete karo" (Urdu), verify task status changed to completed with confirmation in matching language

### Integration Tests for User Story 4

- [ ] T049 [P] [US4] Write integration test for update_task mark completed in backend/tests/integration/test_us4_update_task_complete.py
- [ ] T050 [P] [US4] Write integration test for update_task already completed error in backend/tests/integration/test_us4_update_task_already_done.py
- [ ] T051 [P] [US4] Write integration test for update_task status change reflection in frontend in backend/tests/integration/test_us4_update_task_reflection.py

### Implementation for User Story 4

- [ ] T052 [P] [US4] Implement update_task MCP tool in backend/src/mcp_tools/update_task.py with user_id, task_id, status parameters
- [ ] T053 [US4] Implement status validation (pending/completed) in backend/src/mcp_tools/update_task.py
- [ ] T054 [US4] Add already-completed error handling in backend/src/mcp_tools/update_task.py
- [ ] T055 [US4] Register update_task tool with MCP server in backend/src/services/mcp_server.py
- [ ] T056 [US4] Integrate update_task tool execution with Qwen in backend/src/services/chat_service.py
- [ ] T057 [US4] Add bilingual confirmation messages for task completion in frontend/src/components/ChatInterface.tsx
- [ ] T058 [US4] Add visual indicator for completed tasks in ChatInterface component in frontend/src/components/ChatInterface.tsx

**Checkpoint**: All user stories complete - full task management via chat (add, list, delete, complete)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling & Resilience

- [ ] T059 [P] Implement Qwen inference retry logic with exponential backoff in backend/src/services/qwen_client.py
- [ ] T060 [P] Add bilingual fallback error messages for Qwen failures in backend/src/services/chat_service.py
- [ ] T061 [P] Implement graceful degradation for Hugging Face API timeouts in backend/src/services/chat_service.py

### Security Hardening

- [ ] T062 [P] Add input sanitization for user messages before sending to Qwen in backend/src/services/chat_service.py
- [ ] T063 [P] Add output sanitization for Qwen responses in frontend/src/components/ChatInterface.tsx
- [ ] T064 Verify user_id filtering on all MCP tools in backend/src/mcp_tools/add_task.py, list_tasks.py, delete_task.py, update_task.py

### Performance Optimization

- [ ] T065 [P] Add database index on conversation.user_id in backend/scripts/migrate_ai_tables.py
- [ ] T066 [P] Add database index on message(conversation_id, created_at DESC) in backend/scripts/migrate_ai_tables.py
- [ ] T067 Implement conversation history pagination (last 100 messages) in backend/src/services/chat_service.py

### Observability & Monitoring

- [ ] T068 [P] Add structured logging for all MCP tool calls with user_id, tool_name, timestamp in backend/src/services/mcp_server.py
- [ ] T069 [P] Add metrics tracking for chat latency, Qwen inference time in backend/src/api/chat.py
- [ ] T070 [P] Add error rate monitoring and alerting setup in backend/main.py

### Documentation

- [ ] T071 Update README.md with Phase III chatbot features in README.md
- [ ] T072 Create API documentation for /api/chat endpoint in docs/api.md
- [ ] T073 Document MCP tool usage for developers in docs/mcp-tools.md

### Validation

- [ ] T074 Run all integration tests and verify 100% pass rate via pytest backend/tests/
- [ ] T075 Run quickstart.md validation and verify setup instructions work
- [ ] T076 Perform end-to-end testing of all 4 user stories in English and Urdu

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Add Tasks)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - View Tasks)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3 - Delete Tasks)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P4 - Complete Tasks)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3

### Within Each User Story

- Integration tests MUST be written and FAIL before implementation (TDD approach)
- Models before services (within foundational phase)
- MCP tools before chat service integration
- Chat service before frontend integration
- Core implementation before error handling

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T002, T003, T004, T005 can run in parallel (different files, no dependencies)

**Foundational Phase (Phase 2)**:
- T007, T008 can run in parallel (different models)
- T013, T015, T017 can run in parallel (different files)
- After T012 completes: T022, T035, T043, T052 can all run in parallel (different MCP tools)

**User Story 1 (Phase 3)**:
- T019, T020, T021 can run in parallel (different test files)
- T022 can run in parallel with foundational tasks

**User Story 2 (Phase 4)**:
- T032, T033, T034 can run in parallel (different test files)

**User Story 3 (Phase 5)**:
- T040, T041, T042 can run in parallel (different test files)

**User Story 4 (Phase 6)**:
- T049, T050, T051 can run in parallel (different test files)

**Polish Phase (Phase 7)**:
- T059, T060, T061 can run in parallel
- T062, T063, T064 can run in parallel
- T065, T066, T067 can run in parallel
- T068, T069, T070 can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# After Foundational phase completes, launch User Story 1 tests together:
Task: "T019 [P] [US1] Write integration test for add_task flow in English"
Task: "T020 [P] [US1] Write integration test for add_task flow in Urdu"
Task: "T021 [P] [US1] Write integration test for missing task title prompt"

# Then launch add_task MCP tool implementation:
Task: "T022 [P] [US1] Implement add_task MCP tool"

# Work on remaining US1 tasks sequentially or in parallel where marked [P]
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T018) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T019-T031)
4. **STOP and VALIDATE**: Test add_task in English and Urdu independently
5. Deploy/demo MVP if ready

**MVP delivers**: Users can add tasks via bilingual chat interface

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (Phases 1-2)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: Add tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (Add: View tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (Add: Delete tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (Add: Complete tasks)
6. Complete Polish → Full production-ready system

Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational (Phase 2) is done:
   - Developer A: User Story 1 (Phase 3) - Add tasks
   - Developer B: User Story 2 (Phase 4) - View tasks
   - Developer C: User Story 3 (Phase 5) - Delete tasks
   - Developer D: User Story 4 (Phase 6) - Complete tasks
3. Stories complete and integrate independently
4. Team converges for Polish phase (Phase 7)

---

## Notes

- **Total Tasks**: 76 tasks across 7 phases
- **Test Coverage**: 12 integration tests (3 per user story) for critical bilingual flows
- **Parallel Opportunities**: 30 tasks marked [P] can run in parallel with proper staffing
- **[P] tasks** = different files, no dependencies on incomplete tasks
- **[Story] label** maps task to specific user story for traceability
- Each user story independently completable and testable
- Integration tests written first (TDD), verified to fail before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Format validation: ALL tasks follow checklist format (checkbox, ID, labels, file paths)

---

**Next Step**: Run `/sp.implement` to begin execution starting with Phase 1: Setup
