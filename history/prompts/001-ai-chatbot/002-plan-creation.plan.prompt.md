---
id: 002
title: Phase III Implementation Plan Creation
stage: plan
date: 2025-01-25
surface: agent
model: claude-sonnet-4-5
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: User
command: /sp.plan
labels: ["plan","phase-iii","architecture","mcp","qwen","database-design"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot/plan.md
  - specs/001-ai-chatbot/research.md
  - specs/001-ai-chatbot/data-model.md
  - specs/001-ai-chatbot/contracts/chat-api.yaml
  - specs/001-ai-chatbot/contracts/mcp-tools.yaml
  - specs/001-ai-chatbot/quickstart.md
  - history/prompts/001-ai-chatbot/002-plan-creation.plan.prompt.md
tests:
  - Constitution compliance validation (ALL PASS)
  - Research tasks completion (R1-R5 resolved)
  - Data model validation (Conversation + Message entities)
  - API contract specification (OpenAPI 3.0)
  - MCP tool schema definition (4 tools)
  - Quickstart guide completeness
---

## Prompt

Perfect. Based on your **`speckit.constitution`** and **`speckit.specify`**, here is the **Phase III Technical Plan (`/sp.plan`)**.

Copy-paste this into:

```
/specs/speckit.plan
```

---

# ===============================

# speckit.plan

# ===============================

**Phase III – AI Powered Todo Chatbot (Technical Plan)**

---

## 1. System Overview

Phase III extends the Phase-II Todo App into an **AI-native system** where all task management happens through a conversational agent powered by **Qwen** and controlled via **MCP tools**.

The system consists of:

```
Next.js (UI)
FastAPI (API + MCP Server)
Neon PostgreSQL (Data + Memory)
Qwen (HuggingFace)
```

The server is **stateless**.
All AI context is rebuilt per request from Neon.

---

## 2. Database Design (Neon)

### 2.1 Core Tables (Already in Phase II)

```
User
Task
```

These remain unchanged.

---

### 2.2 New AI Memory Tables

#### Conversation

| Field      | Type                |
| ---------- | ------------------- |
| id         | uuid (PK)           |
| user_id    | uuid (FK → User.id) |
| created_at | timestamp           |
| updated_at | timestamp           |

One Conversation per user AI session.

---

#### Message

| Field           | Type                         |
| --------------- | ---------------------------- |
| id              | uuid (PK)                    |
| conversation_id | uuid (FK → Conversation.id)  |
| role            | enum (user, assistant, tool) |
| content         | text                         |
| created_at      | timestamp                    |

Stores every chat turn for AI memory.

---

## 3. Authentication Flow

1. Frontend sends JWT in `Authorization: Bearer <token>`
2. FastAPI validates token
3. `user_id` is extracted
4. All DB + MCP calls are filtered by `user_id`

AI never receives raw JWT — only `user_id`.

---

## 4. MCP Server Architecture

FastAPI will host an **MCP server** exposing tools:

| Tool        | Action         |
| ----------- | -------------- |
| add_task    | Create a task  |
| list_tasks  | List all tasks |
| delete_task | Delete a task  |
| update_task | Mark complete  |

Each tool:

* Receives `user_id`
* Operates only on that user's data
* Returns structured JSON

No direct DB writes from AI.

---

## 5. Qwen Integration Flow

FastAPI uses **HuggingFace SDK** to call Qwen.

For every chat request:

```
1) Load Conversation
2) Load Messages
3) Build message array
4) Send to Qwen
5) Qwen decides:
    - reply OR
    - MCP tool call
6) If tool called:
    - execute MCP
    - store result
    - send result back to Qwen
7) Qwen generates final reply
8) Save reply to Message table
9) Return to frontend
```

---

## 6. Chat API Endpoint

```
POST /api/chat
Headers:
Authorization: Bearer <JWT>

Body:
{
  "message": "Doodh lene ka task add karo"
}
```

### Response

```
{
  "reply": "Task kamyabi se add ho gaya"
}
```

---

## 7. Conversation Lifecycle

1. If user has no conversation → create one
2. Else → load existing conversation
3. Append user message
4. Run Qwen agent
5. Store assistant + tool messages

Memory is always reconstructed from Neon.

---

## 8. Error Handling Rules

| Scenario       | Behavior              |
| -------------- | --------------------- |
| Task not found | Friendly message      |
| Invalid JWT    | 401                   |
| Tool failure   | Explain error         |
| Qwen error     | Retry or safe message |

---

## 9. What Phase III Will Deliver

After implementation:

User can:

* Type in Urdu or English
* Chat with AI
* Manage todos
* Resume conversations
* Never see another user's data

The app becomes a **real AI SaaS**.

---

# ✅ Next Step

Run:

```
/sp.tasks
```

This will break this plan into **precise, implementable tasks** that Claude Code will follow line-by-line.

You are now in **real enterprise AI engineering mode** 🚀

## Response snapshot

Completed Phase 0 and Phase 1 planning for AI-Powered Todo Chatbot, generating comprehensive implementation plan with research findings, data model, API contracts, and quickstart guide.

**Phase 0: Research** (5 Critical Decisions Resolved)

1. **MCP SDK Integration** (R1):
   - Decision: In-process MCP server with FastAPI
   - Rationale: Simpler deployment, lower latency, easier testing
   - Architecture: MCP tools as async Python functions within FastAPI process

2. **Qwen Language Support** (R2):
   - Decision: Use Qwen auto-detection with bilingual system prompts
   - Rationale: Native multilingual support, no separate detection service needed
   - Language Strategy: Auto-detect input language, respond in same language

3. **Conversation Pagination** (R3):
   - Decision: Load last 100 messages for AI context
   - Rationale: Within 32K token limit, sufficient for task conversations
   - Scalability: Handles 10,000+ message conversations

4. **MCP Tool Schema Design** (R4):
   - Decision: JSON Schema for 4 tools (add_task, list_tasks, delete_task, update_task)
   - Rationale: Standard validation, security isolation, AI-friendly errors
   - Security: user_id required in all tools

5. **Error Handling** (R5):
   - Decision: Retry with exponential backoff + bilingual fallback responses
   - Rationale: Handles transient failures, maintains UX during outages
   - Strategy: 3 retries with exponential backoff, 8s timeout

**Phase 1: Design & Contracts** (4 Artifacts Created)

1. **Data Model** (`data-model.md`):
   - Conversation entity (id, user_id, created_at, updated_at)
   - Message entity (id, conversation_id, role, content, tool_calls, created_at)
   - Foreign keys to User table (Phase II)
   - Indexes for performance (user_id, conversation_id + created_at)
   - Validation rules and state transitions
   - Migration script and rollback plan

2. **API Contract** (`contracts/chat-api.yaml`):
   - OpenAPI 3.0 specification for POST /api/chat
   - JWT authentication (Bearer token)
   - Request/response schemas with examples
   - Error responses (400, 401, 500, 503)
   - Bilingual examples (English + Urdu)

3. **MCP Tool Schemas** (`contracts/mcp-tools.yaml`):
   - add_task: Create task with user_id, title, description
   - list_tasks: List all tasks with optional status filter
   - delete_task: Delete task with ownership verification
   - update_task: Update task status or title/description
   - JSON Schema validation for all inputs/outputs
   - Security rules (user_id enforcement, ownership verification)

4. **Quickstart Guide** (`quickstart.md`):
   - Prerequisites (accounts, software, existing system)
   - Setup instructions (backend, frontend, environment, migrations)
   - Testing guide (6 test cases: English + Urdu)
   - Troubleshooting common issues
   - Development tips and production deployment

**Constitution Compliance**:

✅ **ALL 6 PRINCIPLES PASS**:
- I. AI-Native Interaction: Chatbot as primary interface
- II. Stateless Server: Zero session state, context from DB
- III. Persistence of Intelligence: Conversation + Message tables
- IV. Strict Security: JWT validation, user_id isolation
- V. Multi-Language Support: English + Urdu with auto-detection
- VI. MCP-First Tool Design: All operations via MCP tools

✅ **TECHNOLOGY STACK VALIDATED**:
- Qwen (HuggingFace SDK)
- Official MCP SDK (Python)
- Neon PostgreSQL (2 new tables)
- FastAPI + SQLModel (Phase II stack)
- JWT authentication (Phase II system)
- Next.js frontend (Phase II UI)

**Architecture Diagrams**:
- Component diagram (Frontend → FastAPI → MCP Server → Neon → Qwen)
- Data flow for chat request (7 steps from user message to AI response)
- Entity relationship diagram (User → Conversation → Message)

**Performance & Security**:
- Performance targets: <10s p95 latency, <500ms history load
- Security rules: user_id filtering, JWT validation, SQL injection prevention
- Error handling: Retry logic, bilingual fallbacks, graceful degradation
- Monitoring: Metrics tracking, structured logging, alerts

**Risk Analysis**:
- 6 risks identified with mitigation strategies
- High-impact risks: Qwen latency, tool execution failure
- Mitigations: Streaming responses, retry logic, fallback messages

**Definition of Done** (15 checkpoints):
- All 6 constitution principles implemented
- All 4 user stories working
- Qwen + MCP integrated
- Bilingual support functional
- User isolation verified
- Stateless architecture validated
- Performance benchmarks met
- Phase II features preserved

## Outcome

- ✅ Impact: Complete Phase III plan with research findings, data model, API/MCP contracts, and quickstart guide
- 🧪 Tests: Constitution compliance validated (100% pass rate), all research questions resolved, data model validated, contracts specified
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, chat-api.yaml, mcp-tools.yaml, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to break plan into implementable tasks with Task IDs for Claude Code execution
- 🧠 Reflection: Plan successfully balances constitutional requirements (stateless, secure, MCP-first) with practical implementation (in-process MCP, Qwen auto-detection, pagination). All technical unknowns resolved through systematic research. Ready for implementation phase with clear architecture, contracts, and testing strategy.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully with all deliverables
- Graders run and results (PASS/FAIL):
  - Constitution compliance: PASS (all 6 principles, all stack requirements)
  - Research completeness: PASS (5/5 questions resolved with decisions)
  - Data model validity: PASS (entities, relationships, indexes, migrations defined)
  - API contract completeness: PASS (OpenAPI spec, auth, errors, examples)
  - MCP tool schemas: PASS (4 tools with JSON Schema, security rules)
  - Quickstart guide: PASS (setup, testing, troubleshooting, deployment)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to generate implementation task breakdown with dependencies, Task IDs, and test requirements for Claude Code execution
