<!--
Sync Impact Report:
===================
Version: 1.0.0 → 3.0.0 (MAJOR - New phase with AI-first architecture)
Modified Principles: N/A (Initial constitution for Phase III)
Added Sections:
  - Core Principles (6 principles defined)
  - Technical Stack Constraints
  - Architectural Principles
  - Security & User Isolation
  - Language & Interaction
  - Development Workflow (SDD)
Removed Sections: None
Templates Requiring Updates:
  - ✅ .specify/templates/plan-template.md (aligned with AI-Native architecture)
  - ✅ .specify/templates/spec-template.md (aligned with NLP requirements)
  - ✅ .specify/templates/tasks-template.md (aligned with MCP tool patterns)
  - ✅ .specify/templates/commands/*.md (validated for generic references)
Follow-up TODOs: None
-->

# Evolution of Todo Constitution - Phase III

## Core Objective

The system must evolve from a standard web application into a **conversational AI-native system** where users manage tasks through natural language, maintaining all Phase II functionality while introducing intelligent task management.

---

## Core Principles

### I. AI-Native Interaction

The chatbot MUST be the primary interface for task management, not an add-on. All CRUD operations MUST be accessible through natural language commands in English and Urdu. The AI agent MUST maintain context across conversations to provide coherent, personalized assistance.

**Rationale**: Users expect conversational interfaces that understand context and intent, not rigid command-line interfaces. AI-native design ensures natural task management.

### II. Stateless Server Architecture

The backend MUST hold NO session state. Every request MUST be independent, fetching conversation history from the database to build the message array for the agent. All state MUST be persisted in Neon PostgreSQL.

**Rationale**: Stateless design enables horizontal scaling, fault tolerance, and clean separation of concerns. Server restarts MUST NOT lose conversation context.

### III. Persistence of Intelligence

All chat sessions MUST be stored in `Conversation` and `Message` tables to ensure context is maintained across server restarts. Every user interaction MUST be traceable and replayable for debugging and improvement.

**Rationale**: Context persistence is essential for usable AI assistants. Users MUST NOT lose conversation history due to server issues.

### IV. Strict Security & User Isolation

Every chat request MUST verify the Better Auth JWT token from Phase II. The AI agent is STRICTLY PROHIBITED from accessing or modifying any task that does not belong to the authenticated `user_id`. All database queries MUST include user_id filters.

**Rationale**: Multi-tenant systems require absolute isolation. Security vulnerabilities are unacceptable in user data systems.

### V. Multi-Language Support

The chatbot MUST support Urdu and English for both input commands and assistant responses. The AI MUST automatically detect language and respond in kind. Action confirmations MUST be provided in the user's language.

**Rationale**: Accessibility and inclusivity are non-negotiable. Language barriers MUST NOT prevent task management.

### VI. MCP-First Tool Design

All task operations MUST be exposed as Model Context Protocol (MCP) tools using the Official MCP SDK. The AI agent MUST interact with the system ONLY through these tools, never through direct database access.

**Rationale**: MCP provides a standardized, secure, and observable interface for AI agents. Direct database access bypasses critical security and validation layers.

---

## Technical Stack Constraints

### AI Engine
- **Qwen** (via Hugging Face SDK) for all natural language processing and reasoning
- MUST use Hugging Face Inference API for model access
- MUST handle inference errors gracefully with fallback responses

### Agent Architecture
- **Official MCP SDK** to build Model Context Protocol server
- Task operations exposed as MCP tools with proper schemas
- MUST support tool streaming for real-time feedback

### Database
- **Neon Serverless PostgreSQL** for persistent storage
- Tables: `Todo`, `User`, `Conversation`, `Message`
- MUST use connection pooling for performance
- MUST implement proper indexing for user_id queries

### Backend
- **FastAPI** and **SQLModel** stack from Phase II
- MUST maintain existing REST API endpoints
- MUST add new chat endpoint `/api/chat` with JWT auth
- MUST preserve Phase II authentication system

### Frontend (Phase II+)
- **Next.js** with TypeScript
- MUST integrate chat interface alongside existing UI
- MUST support real-time streaming responses
- MUST maintain existing CRUD functionality

---

## Architectural Principles

### 1. Separation of Concerns
- **MCP Server**: Exposes tools (create_todo, delete_todo, etc.)
- **Chat Service**: Orchestrates Qwen + MCP tools
- **FastAPI Endpoints**: HTTP layer with JWT auth
- **Database**: Persistent storage layer

### 2. Error Handling
- All tool errors MUST be caught and translated to user-friendly messages
- Inference failures MUST NOT crash the server
- Database errors MUST be logged and masked from users

### 3. Observability
- All tool calls MUST be logged with user_id and timestamp
- Conversation metrics MUST be tracked (length, language, success rate)
- AI inference time MUST be monitored

### 4. Performance
- Chat requests MUST complete within 10 seconds (p95)
- Database queries MUST be optimized with proper indexes
- Conversation history loading MUST be paginated for long sessions

---

## Security & User Isolation

### JWT Enforcement
- Every `/api/chat` request MUST include valid JWT token
- Token MUST contain `user_id` claim
- Expired tokens MUST be rejected with 401 Unauthorized

### Database Isolation
- ALL queries MUST include `WHERE user_id = ?` filter
- MCP tools MUST validate user_id before operations
- Conversation and Message tables MUST be user-scoped

### Input Sanitization
- User messages MUST be sanitized before AI inference
- SQL injection protection via SQLModel parameterization
- XSS protection via proper escaping in responses

---

## Language & Interaction

### Supported Languages
- **English**: Primary language with full grammar support
- **Urdu**: Full support for input and responses
- Language MUST be auto-detected from user message
- Response language MUST match input language

### Action Confirmation
- After EVERY tool call, AI MUST provide confirmation in user's language
- Examples:
  - English: "✅ Task 'Buy groceries' has been added."
  - Urdu: "✅ 'خریداری کرنا' کام شامل ہو گیا ہے۔"
- Confirmation MUST include task details

### Error Messages
- MUST be bilingual (English + Urdu)
- MUST provide actionable guidance
- MUST be user-friendly (no technical jargon)

---

## Development Workflow (SDD)

### No Task = No Code
- No agent is allowed to generate code without a referenced Task ID from `speckit.tasks`
- ALL implementation MUST be traced to a specific requirement
- Code without task reference MUST be rejected

### Hierarchy of Truth
In case of conflict, the hierarchy is:
1. **Constitution** (this document)
2. **Spec** (feature specification)
3. **Plan** (architecture decisions)
4. **Tasks** (implementation tasks)

### Manual Coding Ban
- All implementation MUST be generated by Claude Code after refining specification
- Manual coding is ONLY allowed for:
  - Critical bug fixes (documented in issue)
  - Configuration changes (documented in commit)
- Manual code MUST be reviewed and converted to spec-driven tasks ASAP

### Reusable Intelligence
- Implementation MUST favor Agent Skills and Subagents
- Logic MUST be modular and reusable across phases
- MCP tools MUST be designed for composability

---

## Data Model Requirements

### Conversation Table
```sql
- id: UUID (PK)
- user_id: UUID (FK to User table)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- title: TEXT (optional, auto-generated from first message)
- language: VARCHAR(5) (en-US, ur-PK)
```

### Message Table
```sql
- id: UUID (PK)
- conversation_id: UUID (FK to Conversation)
- role: TEXT (user, assistant, system)
- content: TEXT
- created_at: TIMESTAMP
- tool_calls: JSONB (optional, array of MCP tool invocations)
```

### Phase II Tables (Unchanged)
- Todo (with user_id FK)
- User (with Better Auth integration)

---

## Testing Requirements

### Unit Tests
- All MCP tools MUST have unit tests
- Chat service logic MUST be tested in isolation
- Language detection MUST have test cases

### Integration Tests
- End-to-end chat flows MUST be tested
- Multi-turn conversations MUST be validated
- Urdu language support MUST be tested

### Security Tests
- JWT validation MUST be tested
- User isolation MUST be verified
- SQL injection attempts MUST be tested

---

## Non-Functional Requirements

### Performance
- Chat endpoint p95 latency: <10 seconds
- Conversation history load: <500ms (p95)
- MCP tool execution: <2 seconds (p95)

### Reliability
- 99.5% uptime target for chat service
- Graceful degradation if AI inference fails
- Automatic retry for transient errors

### Scalability
- Support 100 concurrent users
- Support 10,000 messages per conversation
- Horizontal scaling via stateless design

---

## Governance

### Amendment Procedure
1. Proposal submitted as issue with rationale
2. Impact analysis on existing phases
3. Review by project architect
4. Approval via pull request
5. Migration plan for breaking changes
6. Version bump (MAJOR/MINOR/PATCH)

### Compliance Review
- All PRs MUST verify constitution compliance
- Complexity MUST be justified against principles
- Security violations MUST block merge
- Performance violations MUST be documented

### Version Policy
- **MAJOR**: Backward incompatible governance/principle removals
- **MINOR**: New principle/section added or materially expanded
- **PATCH**: Clarifications, wording, typo fixes

### Runtime Guidance
- Use this constitution as ultimate authority
- Refer to `CLAUDE.md` for agent-specific guidance
- Consult phase-specific specs for implementation details

---

**Version**: 3.0.0 | **Ratified**: 2025-01-25 | **Last Amended**: 2025-01-25

---

## Phase III Definition of Done

- [ ] All 6 core principles implemented and validated
- [ ] Qwen AI integrated via Hugging Face SDK
- [ ] MCP server exposes all CRUD tools
- [ ] Chat endpoint with JWT authentication functional
- [ ] Conversation and Message tables deployed
- [ ] Multi-language support (English + Urdu) working
- [ ] User isolation verified with security tests
- [ ] Stateless server architecture validated
- [ ] All acceptance criteria from spec.md met
- [ ] Performance benchmarks achieved (p95 <10s)
- [ ] Observability (logging, metrics) in place
- [ ] Phase II features remain functional (regression tests pass)
