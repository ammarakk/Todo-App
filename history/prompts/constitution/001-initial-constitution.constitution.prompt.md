---
id: 001
title: Initial Constitution
stage: constitution
date: 2026-01-20
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: User
command: /sp.constitution
labels: ["constitution","setup","governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md (created, 369 lines)
tests: []
---

## Prompt

```text
# speckit.constitution
# Evolution of Todo — Full Project Constitution

---

## 1. Purpose (WHY)

This project exists to demonstrate **Spec-Driven Development (SDD)** for building a system that evolves from a **simple console application** into a **cloud-native, AI-driven, event-based distributed platform**.

The primary objective is **architectural discipline**, not feature velocity.

---

## 2. Absolute Non-Negotiable Rules

### 2.1 Spec-Driven Development Only
All work MUST follow this strict order:

Constitution
→ Specify
→ Plan
→ Tasks
→ Implement

❌ No skipping
❌ No merging steps
❌ No code without tasks

---

### 2.2 No Manual Coding
- Humans MUST NOT write application code.
- ALL code must be generated via `/sp.implement`.
- Humans may:
  - Edit specs
  - Review output
  - Request regeneration

Manual coding = **phase failure**.

---

### 2.3 Single Source of Truth
- Specs are the only authority.
- If behavior is not written, it **does not exist**.
- Implementation may NEVER introduce new behavior.

---

## 3. Phase Evolution Contract

The project MUST evolve strictly in this order:

| Phase | Scope |
|-----|-----|
| Phase I | In-memory console app |
| Phase II | Full-stack web app |
| Phase III | AI agents via MCP |
| Phase IV | Kubernetes deployment |
| Phase V | Event-driven cloud system |

No phase may skip responsibilities.

---

## 4. Phase-Wise Enforcement Rules

### Phase I — Console (Foundation)
- Single user
- In-memory only
- No database
- No web
- No auth
- No AI
- No agents

---

### Phase II — Full Stack
- Persistent database
- REST APIs
- Frontend + backend separation
- Authentication mandatory
- User-level data isolation

---

### Phase III — AI & MCP
- AI agents MUST operate via MCP tools
- No direct DB access by agents
- Chat must be stateless
- Conversation state persisted externally

---

### Phase IV — Kubernetes
- All services containerized
- Helm charts required
- Minikube parity with production
- No environment-specific logic

---

### Phase V — Event-Driven Cloud
- CRUD emits events
- Asynchronous consumers
- Kafka via Dapr only
- No service-to-service tight coupling

---

## 5. Architecture Principles

### 5.1 Stateless Services
- Backend services MUST be stateless
- State stored in:
  - Database
  - Dapr state store
- Restarting services must not break functionality

---

### 5.2 Agent-First Design
- Agents invoke **tools**, not functions
- All agent behavior must be explicit
- No autonomous free-form execution

---

### 5.3 Event-Driven by Default (Phase V)
- Events represent facts
- Consumers react independently
- No synchronous dependencies

---

## 6. Security Rules

- Authentication mandatory once introduced
- JWT verification at backend boundary
- User data isolation enforced in backend
- Secrets NEVER hard-coded
- No trust in frontend

---

## 7. Technology Constraints

### Allowed Stack
- Frontend: Next.js (App Router)
- Backend: FastAPI (Python)
- ORM: SQLModel
- Database: PostgreSQL (Neon)
- Auth: Better Auth
- AI: OpenAI Agents SDK
- MCP: Official MCP SDK
- Orchestration: Kubernetes
- Messaging: Kafka (via Dapr)

Changes require spec updates.

---

## 8. Error Handling Rules

- Errors must be user-friendly
- No crashes on invalid input
- System must recover gracefully
- Errors must not leak internals

---

## 9. Change Management

| Change Type | Required Action |
|-----------|----------------|
| Behavior | Update `speckit.specify` |
| Architecture | Update `speckit.plan` |
| Tasks | Update `speckit.tasks` |
| Principles | Update this constitution |

---

## 10. Enforcement Hierarchy

If conflicts occur, precedence is:

Constitution
> Specify
> Plan
> Tasks
> Implementation

Lower layers must obey higher layers.

---

## 11. Definition of Success

This project is successful when:

- Every feature traces to a spec
- No manual code exists
- Agents operate only via tools
- System scales from CLI to cloud
- Architecture is explainable and auditable

---

## 12. Final Rule

If it is not specified,
**it is forbidden**.
```

## Response snapshot

Successfully created the Evolution of Todo Constitution (v1.0.0) with:

**Core Principles Established:**
1. Purpose - Spec-Driven Development demonstration from console to cloud
2. SDD Workflow - Constitution → Specify → Plan → Tasks → Implement (strict order)
3. No Manual Coding - All code via `/sp.implement`, humans only edit specs
4. Single Source of Truth - Specs are the only authority
5. Phase Evolution - 5 phases: Console → Full Stack → AI/MCP → Kubernetes → Event-Driven
6. Stateless Services - Backend stateless, state in DB/Dapr
7. Agent-First Design - Agents invoke tools, not functions
8. Event-Driven - Events represent facts, independent consumers (Phase V)
9. Security Rules - Auth mandatory, JWT verification, user data isolation, no secrets
10. Technology Constraints - Defined stack (Next.js, FastAPI, SQLModel, PostgreSQL, etc.)
11. Error Handling - User-friendly errors, graceful recovery, no leaks
12. Change Management - Behavior→spec, Architecture→plan, Tasks→tasks, Principles→constitution

**Phase Enforcement Rules:**
- Phase I (Console): Single user, in-memory, no infrastructure
- Phase II (Full Stack): Persistent DB, REST APIs, auth mandatory
- Phase III (AI/MCP): MCP tools only, no direct DB access, stateless chat
- Phase IV (Kubernetes): Containerized, Helm charts, env parity
- Phase V (Event-Driven): CRUD events, async consumers, Kafka via Dapr

**Governance:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Compliance review required for all PRs
- Constitution supersedes all practices
- Enforcement hierarchy: Constitution > Specify > Plan > Tasks > Implementation

**Final Rule:** If it is not specified, it is forbidden.

File created: `.specify/memory/constitution.md` (369 lines)
Version: 1.0.0 | Ratified: 2026-01-20 | Last Amended: 2026-01-20

## Outcome

- ✅ Impact: Foundation established for Spec-Driven Development with comprehensive governance framework
- 🧪 Tests: N/A (constitutional document)
- 📁 Files: Created `.specify/memory/constitution.md` with complete project governance
- 🔁 Next prompts: Consider updating plan-template.md Constitution Check section with phase-specific gates
- 🧠 Reflection: Constitution successfully transforms user requirements into enforceable governance framework with clear rationales for all principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Update plan-template.md to include phase-specific constitution check gates referencing the 5-phase evolution contract
