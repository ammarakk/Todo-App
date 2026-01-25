# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-ai-chatbot` | **Date**: 2025-01-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

## Summary

Phase III transforms the Phase II Todo App into an **AI-native conversational system** where users manage tasks through natural language in English and Urdu. The system uses **Qwen** (via HuggingFace SDK) as the AI engine, **Official MCP SDK** to expose task operations as secure tools, and **Neon PostgreSQL** for persistent conversation memory. The server is **stateless** — all AI context is rebuilt per request from the database, ensuring crash safety and horizontal scalability.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI backend), TypeScript/Next.js (frontend from Phase II)
**Primary Dependencies**:
- Hugging Face Inference API (Qwen model)
- Official MCP SDK (Python)
- FastAPI + SQLModel (from Phase II)
- Neon PostgreSQL (serverless)

**Storage**: Neon Serverless PostgreSQL
- Existing: User, Task tables (Phase II)
- New: Conversation, Message tables (AI memory)

**Testing**: pytest (Python), Jest/Playwright (frontend)
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Full-stack web application
**Performance Goals**:
- Chat endpoint p95 latency: <10 seconds
- Conversation history load: <500ms (p95)
- Support 100 concurrent users
- Support 10,000 messages per conversation

**Constraints**:
- Stateless server architecture (no in-memory session state)
- JWT authentication on every request (from Phase II)
- Absolute user isolation (no cross-user data access)
- MCP-only AI execution (no direct DB access)
- Bilingual support (English + Urdu)

**Scale/Scope**:
- 4 MCP tools (add_task, list_tasks, delete_task, update_task)
- 2 new database tables (Conversation, Message)
- 1 new API endpoint (/api/chat)
- 100 concurrent users capacity

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance Matrix

| Principle | Status | Notes |
|-----------|--------|-------|
| I. AI-Native Interaction | ✅ PASS | Chatbot as primary interface, all CRUD via NLP |
| II. Stateless Server | ✅ PASS | Zero session state, context rebuilt from DB per request |
| III. Persistence of Intelligence | ✅ PASS | Conversation + Message tables for full history |
| IV. Strict Security & User Isolation | ✅ PASS | JWT validation, user_id filters, MCP-only access |
| V. Multi-Language Support | ✅ PASS | English + Urdu with auto-detection |
| VI. MCP-First Tool Design | ✅ PASS | All task operations via MCP SDK, no direct DB |

### Technology Stack Validation

| Constitution Requirement | Plan Decision | Status |
|-------------------------|---------------|--------|
| Qwen (HuggingFace SDK) | HF Inference API for Qwen | ✅ PASS |
| Official MCP SDK | MCP SDK for Python tool exposure | ✅ PASS |
| Neon Serverless PostgreSQL | Neon DB with 2 new tables | ✅ PASS |
| FastAPI + SQLModel | Reuse Phase II stack | ✅ PASS |
| JWT (FastAPI native) | JWT auth on /api/chat endpoint | ✅ PASS |
| Next.js frontend | Reuse Phase II frontend | ✅ PASS |

### Architecture Law Compliance

**3.1 Stateless Server**: ✅ PASS
- Every request: JWT validate → load conversation from Neon → build message array → call Qwen
- No in-memory AI context storage
- Server restarts lose zero data

**3.2 Persistent Intelligence**: ✅ PASS
- Conversation table (one per user session)
- Message table (all turns with role, content, tool_calls)
- History reconstructed on every request

**3.3 Tool-Only Execution**: ✅ PASS
- AI forbidden from direct DB access
- All actions via MCP tools (add_task, list_tasks, delete_task, update_task)
- Tools enforce user_id filtering

**4. Security & User Isolation**: ✅ PASS
- JWT validation on every /api/chat request
- user_id extracted and passed to all MCP tools
- AI cannot see/access other users' tasks

**5. Language Law**: ✅ PASS
- Accept English and Urdu input
- Reply in detected language
- Confirm actions in user's language

**6. Spec-Driven Law**: ✅ PASS
- Hierarchy: Constitution > Spec > Plan > Tasks > Code
- No code without Task ID reference
- Claude Code only implementation system

**GATE RESULT**: ✅ ALL PASS — Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for /api/chat endpoint
│   └── mcp-tools.yaml   # MCP tool schemas
├── speckit.constitution.md # Phase III constitution
├── speckit.specify.md   # Simplified user journeys
├── spec.md              # Full feature specification
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── todo.py          # Existing (Phase II)
│   │   ├── user.py          # Existing (Phase II)
│   │   ├── conversation.py  # NEW: Conversation model
│   │   └── message.py       # NEW: Message model
│   ├── services/
│   │   ├── todo_service.py  # Existing (Phase II)
│   │   ├── auth_service.py  # Existing (Phase II)
│   │   ├── chat_service.py  # NEW: Chat orchestration
│   │   └── mcp_server.py    # NEW: MCP tool server
│   ├── api/
│   │   ├── todos.py         # Existing (Phase II)
│   │   ├── auth.py          # Existing (Phase II)
│   │   └── chat.py          # NEW: /api/chat endpoint
│   └── mcp_tools/
│       ├── add_task.py      # NEW: MCP tool implementation
│       ├── list_tasks.py    # NEW: MCP tool implementation
│       ├── delete_task.py   # NEW: MCP tool implementation
│       └── update_task.py   # NEW: MCP tool implementation
├── tests/
│   ├── contract/
│   │   ├── test_chat_api.py      # NEW: API contract tests
│   │   └── test_mcp_tools.py     # NEW: MCP tool contract tests
│   ├── integration/
│   │   ├── test_chat_flow.py     # NEW: End-to-end chat tests
│   │   └── test_bilingual.py     # NEW: Language detection tests
│   └── unit/
│       ├── test_conversation.py  # NEW: Model unit tests
│       ├── test_message.py       # NEW: Model unit tests
│       └── test_chat_service.py  # NEW: Service unit tests
└── main.py                    # Existing (Phase II) - add /api/chat route

frontend/
├── src/
│   ├── components/
│   │   ├── TodoList.tsx     # Existing (Phase II)
│   │   ├── TodoForm.tsx     # Existing (Phase II)
│   │   └── ChatInterface.tsx # NEW: Chat UI component
│   ├── pages/
│   │   ├── index.tsx        # Existing (Phase II)
│   │   └── chat.tsx         # NEW: Dedicated chat page
│   └── services/
│       ├── api.ts           # Existing (Phase II)
│       └── chat.ts          # NEW: Chat API client
└── tests/
    └── integration/
        └── chat.test.tsx    # NEW: Chat integration tests
```

**Structure Decision**: Web application structure (backend + frontend) extends existing Phase II architecture. New AI/MCP components isolated in separate modules to preserve Phase II functionality.

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Next.js Frontend                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ TodoList     │  │ TodoForm     │  │ ChatInterface│     │
│  │ (Phase II)   │  │ (Phase II)   │  │ (Phase III)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ /api/todos   │  │ /api/auth    │  │ /api/chat    │     │
│  │ (Phase II)   │  │ (Phase II)   │  │ (Phase III)  │     │
│  └──────────────┘  └──────┬───────┘  └──────┬───────┘     │
│                            │                 │              │
│                            ▼                 ▼              │
│  ┌──────────────────────────────────────────────────┐    │
│  │           MCP Server (Phase III)                  │    │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐ │    │
│  │  │add_task │ │list_tasks│ │del_task │ │upd_task│ │    │
│  │  └────┬────┘ └─────┬────┘ └────┬────┘ └───┬───┘  │    │
│  └───────┼────────────┼──────────┼──────────┼────────┘    │
│          ▼            ▼          ▼          ▼             │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Chat Service (Phase III)                 │    │
│  │   • Load conversation from Neon                 │    │
│  │   • Build message array for Qwen                │    │
│  │   • Call HuggingFace Inference API              │    │
│  │   • Execute MCP tools based on AI decisions     │    │
│  │   • Save messages to Neon                       │    │
│  └───────────────────┬──────────────────────────────┘    │
└──────────────────────┼────────────────────────────────────┘
                       │ SQL
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Neon PostgreSQL                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌───────────┐│
│  │   User   │ │   Todo   │ │Conversation  │ │  Message  ││
│  │(Phase II)│ │(Phase II)│ │ (Phase III)  │ │(Phase III)││
│  └──────────┘ └──────────┘ └──────────────┘ └───────────┘│
└─────────────────────────────────────────────────────────────┘
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Hugging Face Inference API                     │
│                    Qwen Model                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Chat Request

```
1. User sends message (English/Urdu)
   ↓
2. Frontend: POST /api/chat
   Headers: Authorization: Bearer <JWT>
   Body: { "message": "Doodh lene ka task add karo" }
   ↓
3. FastAPI: Validate JWT → Extract user_id
   ↓
4. Chat Service:
   a) Load or create Conversation (user_id)
   b) Load Message history for conversation
   c) Append user message to array
   ↓
5. Qwen Integration:
   a) Send message array to HuggingFace Inference API
   b) Qwen analyzes intent and decides action
   c) If tool needed → Execute MCP tool
   d) Tool result returned to Qwen
   e) Qwen generates final reply (in user's language)
   ↓
6. Chat Service:
   a) Save assistant reply to Message table
   b) Return { "reply": "Task kamyabi se add ho gaya" }
   ↓
7. Frontend: Display reply to user
```

## Complexity Tracking

> **No violations requiring justification — all design decisions align with constitution principles**

| N/A | N/A | N/A |
|-----|-----|-----|
| — | — | — |

---

## Phase 0: Research & Technology Decisions

### Research Tasks

**R1: MCP SDK Integration Patterns**
- **Question**: How to integrate Official MCP SDK with FastAPI?
- **Research needed**: MCP SDK documentation, FastAPI middleware patterns, tool schema definitions
- **Output**: Integration architecture for `mcp_server.py`

**R2: Qwen Model Capabilities**
- **Question**: Does Qwen support English-Urdu language detection and response?
- **Research needed**: Qwen model card, HuggingFace API docs, language support testing
- **Output**: Language detection strategy, prompt engineering patterns

**R3: Conversation Pagination Strategy**
- **Question**: How to handle conversations with 10,000+ messages efficiently?
- **Research needed**: PostgreSQL pagination patterns, context window optimization, message summarization
- **Output**: Pagination strategy, context truncation rules

**R4: MCP Tool Schema Design**
- **Question**: What schemas should MCP tools expose for task operations?
- **Research needed**: MCP tool specification, JSON schema patterns, error handling
- **Output**: Tool schemas for add_task, list_tasks, delete_task, update_task

**R5: Error Handling Best Practices**
- **Question**: How to handle Qwen inference failures gracefully?
- **Research needed**: Retry strategies, fallback responses, timeout handling
- **Output**: Error handling patterns, retry logic

### Deliverables

- `research.md` with decisions, rationale, and alternatives considered for all R1-R5

---

## Phase 1: Design & Contracts

### 1.1 Data Model (`data-model.md`)

**Entities to Define**:

1. **Conversation**
   - Fields: id (UUID, PK), user_id (UUID, FK), created_at (timestamp), updated_at (timestamp)
   - Indexes: user_id (for lookup)
   - Relationships: One user has many conversations (or one active conversation)

2. **Message**
   - Fields: id (UUID, PK), conversation_id (UUID, FK), role (enum: user/assistant/tool), content (text), created_at (timestamp), tool_calls (JSONB, optional)
   - Indexes: conversation_id, created_at (for ordering)
   - Relationships: Belongs to Conversation

3. **Todo** (Existing - Phase II)
   - Unchanged, but accessed via MCP tools only

4. **User** (Existing - Phase II)
   - Unchanged, JWT authentication preserved

**State Transitions**:
- Conversation: created → active → (no explicit deletion, archive inactive)
- Message: created (immutable)

**Validation Rules**:
- Conversation.user_id MUST reference valid User
- Message.conversation_id MUST reference valid Conversation
- Message.role MUST be one of: user, assistant, tool
- Message.content MUST be non-empty for role=user/assistant
- Message.tool_calls MUST be valid JSON if present

### 1.2 API Contracts (`contracts/`)

**chat-api.yaml** (OpenAPI 3.0):
```yaml
POST /api/chat
Description: Send message to AI chatbot
Security: BearerAuth (JWT)
Request Body:
  message: string (required, 1-1000 chars)
Response 200:
  reply: string (AI response in user's language)
Response 401:
  error: string (JWT invalid/expired)
Response 500:
  error: string (AI inference failure)
```

**mcp-tools.yaml** (MCP Tool Schemas):
```yaml
tools:
  add_task:
    description: Create a new task for the user
    input_schema:
      user_id: UUID (required)
      title: string (1-200 chars, required)
      description: string (optional)
    output_schema:
      task_id: integer
      title: string
      status: "pending"

  list_tasks:
    description: List all tasks for the user
    input_schema:
      user_id: UUID (required)
    output_schema:
      tasks: array of Task objects

  delete_task:
    description: Delete a specific task
    input_schema:
      user_id: UUID (required)
      task_id: integer (required)
    output_schema:
      success: boolean
      message: string

  update_task:
    description: Mark task as completed
    input_schema:
      user_id: UUID (required)
      task_id: integer (required)
    output_schema:
      task_id: integer
      status: "completed"
```

### 1.3 Quickstart Guide (`quickstart.md`)

**Prerequisites**:
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL account
- Hugging Face API key (Qwen access)
- Phase II backend + frontend running

**Setup Steps**:
1. Clone repo, checkout `001-ai-chatbot` branch
2. Install backend dependencies: `pip install fastapi sqlmodel huggingface_hub mcp-sdk`
3. Install frontend dependencies: `npm install` (from Phase II)
4. Configure environment variables:
   ```bash
   NEON_DATABASE_URL=postgresql://...
   HUGGINGFACE_API_KEY=hf_...
   JWT_SECRET=... (from Phase II)
   ```
5. Run database migrations: `python backend/scripts/migrate_ai_tables.py`
6. Start backend: `uvicorn backend.main:app --reload`
7. Start frontend: `npm run dev` (from frontend/)
8. Access chat UI: `http://localhost:3000/chat`

**Testing**:
- English: "Add a task to buy milk"
- Urdu: "میرے ٹاسک دکھاؤ"
- Verify: Task created/listed in user's language

### 1.4 Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to append:
- MCP SDK patterns
- Qwen integration approach
- Bilingual chat architecture

---

## Phase 2: Implementation Preparation

**NOTE**: This phase is executed by `/sp.tasks` command, NOT `/sp.plan`.

The plan document provides the architectural foundation. The next command (`/sp.tasks`) will break this plan into:
- Concrete implementation tasks
- Task dependencies
- Test requirements
- Task IDs for Claude Code execution

---

## Dependencies & Integration Points

### External Services
- **Hugging Face Inference API**: Qwen model access
  - API endpoint: `https://api-inference.huggingface.co`
  - Model: `Qwen/Qwen-72B-Chat` (or similar)
  - Authentication: Bearer token in headers

- **Neon PostgreSQL**: Serverless database
  - Connection pooling via `psycopg2`
  - Migrations via `alembic` or custom scripts

### Internal Systems (Phase II)
- **JWT Authentication**: Reuse existing auth middleware
- **Todo CRUD**: Existing services accessed via MCP wrapper
- **User Management**: Existing User model and queries

### Critical Integration Points
1. **Chat Service → MCP Server**: In-process tool execution (no network)
2. **Chat Service → Qwen**: HTTP client with retry logic
3. **Chat Service → Neon**: SQLModel session per request
4. **Frontend → Chat API**: Fetch/axios with JWT bearer token

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Qwen inference latency >10s | High (UX degradation) | Implement streaming responses, show typing indicator, set 8s timeout |
| Language detection fails | Medium (wrong language response) | Fallback to English, add "switch language" command |
| Conversation history too large | Medium (slow load times) | Paginate messages (last 100), summarize older messages |
| MCP tool execution failure | High (action not performed) | Retry with exponential backoff, log errors, inform user |
| JWT expiry during chat | Low (re-auth required) | Frontend auto-refresh token, clear error on 401 |
| Neon connection pool exhausted | Medium (request failures) | Configure pool size (min 5, max 20), implement retry logic |

---

## Performance Optimization Strategy

1. **Database**:
   - Index on `conversation.user_id` for fast lookup
   - Index on `message.conversation_id, created_at` for ordered retrieval
   - Connection pooling (5-20 connections based on load)

2. **AI Inference**:
   - Cache recent Qwen responses (5-minute TTL)
   - Use streaming responses for perceived speed
   - Implement request timeout (8s) + retry

3. **API**:
   - Async FastAPI endpoints for concurrent requests
   - Response compression (gzip)
   - CORS configuration for frontend origin

4. **Frontend**:
   - Lazy-load chat history (virtual scrolling)
   - Debounce user input (300ms)
   - Show typing indicator during Qwen inference

---

## Monitoring & Observability

### Metrics to Track
- Chat request latency (p50, p95, p99)
- Qwen inference time
- MCP tool execution count and duration
- Conversation length (messages per conversation)
- Language detection accuracy
- Error rates (401, 500, inference failures)

### Logging Strategy
- **Structured logging** (JSON format)
- **Log levels**: INFO (requests), ERROR (failures), DEBUG (tool calls)
- **Key fields**: user_id, conversation_id, tool_name, latency_ms

### Alerts
- Chat endpoint p95 >10s for 5 minutes
- Error rate >5% for 5 minutes
- Qwen inference failure rate >10%
- Database connection pool exhausted

---

## Security Considerations

### Input Validation
- Sanitize user messages before sending to Qwen
- Limit message length (1-1000 chars)
- Escape SQL parameters (SQLModel handles this)

### Output Sanitization
- Escape Qwen responses before displaying in frontend
- Prevent XSS in chat messages

### Access Control
- JWT validation on every /api/chat request
- user_id filtering in all MCP tools
- No cross-user data access

### Secrets Management
- Store Hugging Face API key in environment variable
- Store JWT secret in environment variable
- Never log sensitive data

---

## Testing Strategy

### Unit Tests
- `test_conversation.py`: Conversation model CRUD
- `test_message.py`: Message model CRUD
- `test_chat_service.py`: Message array building, Qwen prompt construction
- `test_mcp_tools.py`: Each tool's input validation and output format

### Integration Tests
- `test_chat_flow.py`: End-to-end chat request → Qwen → MCP tool → response
- `test_bilingual.py`: English/Urdu language detection and response
- `test_security.py`: JWT validation, user_id isolation

### Contract Tests
- `test_chat_api.py`: OpenAPI spec compliance
- `test_mcp_tools.py`: MCP tool schema compliance

### Manual Testing
- Test all 4 user stories from spec.md
- Test edge cases (empty message, very long message, mixed language)
- Test error scenarios (invalid JWT, task not found, Qwen timeout)

---

## Definition of Done (Phase III)

- [ ] All 6 constitution principles implemented and validated
- [ ] All 4 user stories from spec.md working
- [ ] Qwen integrated via HuggingFace SDK
- [ ] MCP server exposes 4 tools (add_task, list_tasks, delete_task, update_task)
- [ ] /api/chat endpoint functional with JWT auth
- [ ] Conversation and Message tables deployed and tested
- [ ] Multi-language support (English + Urdu) working with auto-detection
- [ ] User isolation verified (security tests pass)
- [ ] Stateless server architecture validated (restart test)
- [ ] All 15 functional requirements from spec.md met
- [ ] All 8 success criteria from spec.md achieved
- [ ] Phase II features still functional (regression tests pass)
- [ ] Performance benchmarks met (<10s p95, <500ms history load)
- [ ] Observability in place (logging, metrics, alerts)
- [ ] Documentation complete (research.md, data-model.md, contracts/, quickstart.md)

---

## Next Step

Run `/sp.tasks` to break this plan into implementable tasks with Task IDs for Claude Code execution.
