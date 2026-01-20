<!--
Sync Impact Report:
Version Change: Initial → 1.0.0
Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (12 sections)
  - Phase Evolution Contract
  - Phase-Wise Enforcement Rules
  - Architecture Principles
  - Security Rules
  - Technology Constraints
  - Error Handling Rules
  - Change Management
  - Enforcement Hierarchy
  - Definition of Success
Removed Sections: N/A
Templates Requiring Updates:
  - .specify/templates/plan-template.md (Constitution Check section needs phase-specific gates)
  - .specify/templates/spec-template.md (aligned with constitution requirements)
  - .specify/templates/tasks-template.md (aligned with phase-based enforcement)
Follow-up TODOs: None
-->

# Evolution of Todo Constitution

## Core Principles

### I. Purpose

This project exists to demonstrate **Spec-Driven Development (SDD)** for building a system that evolves from a **simple console application** into a **cloud-native, AI-driven, event-based distributed platform**.

The primary objective is **architectural discipline**, not feature velocity.

---

### II. Spec-Driven Development Only

All work MUST follow this strict order:

Constitution → Specify → Plan → Tasks → Implement

**Mandatory Rules:**
- No skipping steps
- No merging steps
- No code without tasks

**Rationale:** This ensures every implementation decision is traceable to requirements, prevents scope creep, and maintains architectural integrity across all evolution phases.

---

### III. No Manual Coding

**Non-Negotiable Rules:**
- Humans MUST NOT write application code
- ALL code must be generated via `/sp.implement`
- Humans MAY: edit specs, review output, request regeneration

**Rationale:** Manual coding bypasses the spec-driven workflow and introduces untraceable behavior changes. Manual coding equals phase failure.

---

### IV. Single Source of Truth

**Mandatory Rules:**
- Specs are the only authority
- If behavior is not written, it does not exist
- Implementation may NEVER introduce new behavior

**Rationale:** Prevents implementation drift and ensures all features are properly specified, reviewed, and approved before coding begins.

---

### V. Phase Evolution Contract

The project MUST evolve strictly in this order:

| Phase | Scope |
|-----|-----|
| Phase I | In-memory console app |
| Phase II | Full-stack web app |
| Phase III | AI agents via MCP |
| Phase IV | Kubernetes deployment |
| Phase V | Event-driven cloud system |

**Non-Negotiable:** No phase may skip responsibilities.

**Rationale:** Each phase builds upon previous foundations. Skipping phases breaks the evolutionary principle and introduces architectural debt.

---

### VI. Stateless Services

**Mandatory Rules:**
- Backend services MUST be stateless
- State stored in: Database or Dapr state store
- Restarting services must not break functionality

**Rationale:** Enables horizontal scaling, fault tolerance, and cloud-native deployment patterns. Stateful services create scaling bottlenecks and operational complexity.

---

### VII. Agent-First Design

**Mandatory Rules:**
- Agents invoke tools, not functions
- All agent behavior must be explicit
- No autonomous free-form execution

**Rationale:** Explicit tool invocations are auditable, testable, and可控. Free-form execution creates unpredictable behavior and security risks.

---

### VIII. Event-Driven by Default (Phase V)

**Mandatory Rules:**
- Events represent facts
- Consumers react independently
- No synchronous dependencies

**Rationale:** Enables loose coupling, independent scaling, and resilience. Synchronous dependencies create cascading failures and tight coupling.

---

### IX. Security Rules

**Mandatory Rules:**
- Authentication mandatory once introduced
- JWT verification at backend boundary
- User data isolation enforced in backend
- Secrets NEVER hard-coded
- No trust in frontend

**Rationale:** Defense-in-depth prevents unauthorized access and data leakage. Frontend is inherently untrustworthy; backend must enforce all security rules.

---

### X. Technology Constraints

**Allowed Stack:**
- Frontend: Next.js (App Router)
- Backend: FastAPI (Python)
- ORM: SQLModel
- Database: PostgreSQL (Neon)
- Auth: Better Auth
- AI: OpenAI Agents SDK
- MCP: Official MCP SDK
- Orchestration: Kubernetes
- Messaging: Kafka (via Dapr)

**Non-Negotiable:** Changes require spec updates.

**Rationale:** Standardized stack reduces complexity, improves maintainability, and ensures team expertise depth.

---

### XI. Error Handling

**Mandatory Rules:**
- Errors must be user-friendly
- No crashes on invalid input
- System must recover gracefully
- Errors must not leak internals

**Rationale:** User experience and security. Crashes and leaked internals create frustration and security vulnerabilities.

---

### XII. Change Management

**Change Type Mapping:**

| Change Type | Required Action |
|-----------|----------------|
| Behavior | Update `speckit.specify` |
| Architecture | Update `speckit.plan` |
| Tasks | Update `speckit.tasks` |
| Principles | Update this constitution |

**Rationale:** Ensures all changes are properly traced through the spec-driven workflow.

---

## Phase Enforcement Rules

### Phase I — Console (Foundation)

**Scope Constraints:**
- Single user
- In-memory only
- No database
- No web
- No auth
- No AI
- No agents

**Rationale:** Establish core domain logic without infrastructure complexity.

---

### Phase II — Full Stack

**Scope Requirements:**
- Persistent database
- REST APIs
- Frontend + backend separation
- Authentication mandatory
- User-level data isolation

**Rationale:** Transition from prototype to production-ready application.

---

### Phase III — AI & MCP

**Scope Requirements:**
- AI agents MUST operate via MCP tools
- No direct DB access by agents
- Chat must be stateless
- Conversation state persisted externally

**Rationale:** Enable AI capabilities while maintaining security and scalability.

---

### Phase IV — Kubernetes

**Scope Requirements:**
- All services containerized
- Helm charts required
- Minikube parity with production
- No environment-specific logic

**Rationale:** Enable cloud-native deployment and operational consistency.

---

### Phase V — Event-Driven Cloud

**Scope Requirements:**
- CRUD emits events
- Asynchronous consumers
- Kafka via Dapr only
- No service-to-service tight coupling

**Rationale:** Enable distributed system patterns and independent scaling.

---

## Architecture Principles

### 1. Stateless Services

Backend services MUST be stateless. State stored in:
- Database (PostgreSQL/Neon)
- Dapr state store (Phase III+)

Restarting services must not break functionality.

---

### 2. Agent-First Design

- Agents invoke tools, not functions
- All agent behavior must be explicit
- No autonomous free-form execution

---

### 3. Event-Driven by Default (Phase V)

- Events represent facts
- Consumers react independently
- No synchronous dependencies

---

## Security Rules

- Authentication mandatory once introduced
- JWT verification at backend boundary
- User data isolation enforced in backend
- Secrets NEVER hard-coded
- No trust in frontend

---

## Technology Stack

**Allowed Technologies:**
- Frontend: Next.js (App Router)
- Backend: FastAPI (Python)
- ORM: SQLModel
- Database: PostgreSQL (Neon)
- Auth: Better Auth
- AI: OpenAI Agents SDK
- MCP: Official MCP SDK
- Orchestration: Kubernetes
- Messaging: Kafka (via Dapr)

**Changes require spec updates.**

---

## Error Handling Standards

- Errors must be user-friendly
- No crashes on invalid input
- System must recover gracefully
- Errors must not leak internals

---

## Enforcement Hierarchy

If conflicts occur, precedence is:

Constitution > Specify > Plan > Tasks > Implementation

Lower layers MUST obey higher layers.

---

## Definition of Success

This project is successful when:

- Every feature traces to a spec
- No manual code exists
- Agents operate only via tools
- System scales from CLI to cloud
- Architecture is explainable and auditable

---

## Final Rule

If it is not specified,
**it is forbidden.**

---

## Governance

### Amendment Procedure

1. Changes to this constitution require:
   - Documentation of rationale
   - Impact analysis on existing specs
   - Migration plan for affected features
   - Version bump following semantic versioning

2. Versioning Policy:
   - **MAJOR**: Backward incompatible governance/principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

3. Compliance Review:
   - All PRs MUST verify constitution compliance
   - Plan templates MUST include constitution check gates
   - Spec templates MUST enforce principle requirements

### Enforcement

- Constitution supersedes all other practices
- Complexity MUST be justified against principles
- All agents and tools MUST follow constitution rules

**Version**: 1.0.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-01-20
