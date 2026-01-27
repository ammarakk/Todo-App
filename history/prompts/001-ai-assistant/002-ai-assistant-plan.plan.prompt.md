---
id: 002
title: AI Assistant Integration Implementation Plan
stage: plan
date: 2026-01-27
surface: agent
model: claude-sonnet-4-5
feature: 001-ai-assistant
branch: 001-ai-assistant
user: User
command: /sp.plan
labels: ["phase3", "ai-integration", "architecture", "implementation-plan"]
links:
  spec: specs/001-ai-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-assistant/plan.md
tests:
  - Constitution compliance validation (PASS)
---

## Prompt

Perfect. Ab main tumhe clean, final, structured speckit.plan de raha hoon — jisme:

Phase 2 system preserved

Phase 3 AI integration

Replacement workflow

Testing flow

Deployment flow

Security principles


Ye hi tumhara official execution blueprint hoga.


---

📘 SPECKIT.PLAN — FINAL EXECUTION PLAN


---

🎯 PROJECT OBJECTIVE

Build a single unified AI-powered Todo application where:

Phase 2 = Stable Todo System

Phase 3 = AI Assistant integrated inside same system


No separate chatbot application allowed.


---

🧱 SYSTEM ARCHITECTURE

Frontend (Next.js Dashboard)
   ├── Todo UI (existing)
   └── AI Assistant (floating chat)

Backend
   ├── Todo APIs (Phase 2)
   └── AI Command API (Phase 3)

Database
   └── Single task store (shared)

AI = control layer
Todo system = core system


---

🔄 PHASE 2 PROTECTION RULE

Existing Phase 2 system must:

Remain functional

Not be rebuilt

Not be replaced

Not be broken


AI layer must extend system, not modify its core logic.


---

🤖 PHASE 3 IMPLEMENTATION

UI Integration

Add floating AI button inside Dashboard

Open chat panel/modal

No standalone chatbot page



---

Backend Integration

Add new endpoint:

POST /api/ai-command

Flow:

1. Receive user message


2. Send to AI


3. AI returns structured action


4. Map action → existing Todo API




---

AI Action Map

AI Action    System Call

create_task    POST /tasks
list_tasks    GET /tasks
update_task    PUT /tasks/:id
delete_task    DELETE /tasks/:id
complete_task    PUT /tasks/:id


AI must never access database directly.


---

🔐 SECURITY DESIGN PRINCIPLES

All APIs must follow:

Least Privilege

Users access only their own tasks. AI acts as that user only.

Fail-Safe Defaults

All APIs require authentication.

Complete Mediation

JWT verified on every request.

Open Design

Use standard auth and middleware. No hidden logic.

AI endpoint must enforce same rules as UI.


---

🧪 MANDATORY FULL SYSTEM TEST

Before deployment, simulate full user journey:

Auth Test

Signup

Login

Session valid


Todo UI Test

Create task

Edit task

Delete task

Mark complete


AI Test

User commands:

Add task buy milk

Show my tasks

Mark task done

Delete task


If any fails → stop.


---

🔄 REPLACEMENT STRATEGY

Old standalone chatbot must be removed:

Delete chatbot page routes

Remove duplicate task logic

Remove separate chatbot backend



---

🌿 GITHUB WORKFLOW

1. Create new branch:

phase-3-ai-integration


2. Replace old Phase 3 chatbot code


3. Keep Phase 2 branch unchanged


4. Update README with AI integration details




---

☁ DEPLOYMENT PLAN

Vercel (Frontend)

Replace old deployment with integrated system


Hugging Face (Backend)

Remove old chatbot backend

Deploy updated backend with AI endpoint



---

🚦 DEPLOYMENT SAFETY RULE

Deployment allowed only if:

No console errors

No API failures

No broken routes

Todo works via UI & AI

Auth stable



---

✅ PHASE 3 COMPLETION DEFINITION

Phase complete when:

✔ One unified app
✔ No standalone chatbot
✔ AI controls Todo system
✔ System secure
✔ All tests pass
✔ GitHub updated
✔ Deployments replaced


---

Ye plan follow hoga to:

👉 No rebuild
👉 No confusion
👉 No architecture mistake
👉 Professional hackathon-level system


---

Next bolo:
"Execution instruction do"

## Response snapshot

Created comprehensive implementation plan (specs/001-ai-assistant/plan.md) with the following structure:

**Technical Context**:
- Frontend: TypeScript, Next.js 13+, React 18, Tailwind CSS
- Backend: Python 3.11+, FastAPI, SQLModel, Qwen (Hugging Face), MCP SDK
- Storage: PostgreSQL (Neon) - no new tables required
- Performance: AI response <3s (p95), task creation <10s, 100 concurrent requests

**Constitution Check**: ✅ ALL GATES PASSED
- Principle I-VI: All compliant (AI-native, stateless, persistent, secure, multi-language, MCP-first)
- Technical Stack: All constraints satisfied
- Architectural Principles: Separation of concerns, error handling, observability, performance
- Security: JWT enforcement, database isolation, input sanitization
- Development Workflow: SDD compliant

**Phase 0: Research & Decisions**
- Frontend chat UI pattern (modal vs slide-over vs widget)
- Real-time communication (SSE vs WebSocket vs polling)
- Session management strategy
- Error recovery patterns
- Dashboard state synchronization

**Phase 1: Design & Contracts**
- Data model: No new entities (reuse existing Todo, User, Conversation, Message)
- API contracts: OpenAPI spec for /api/ai-command endpoint
- Component contracts: TypeScript interfaces for all AI chat components
- Quickstart guide: Development setup and testing instructions

**Phase 2: Architecture Decisions**
- Frontend: Floating bottom-right panel, React Context for state, localStorage for persistence
- Backend: Reuse existing chat.py, MCP tools call Todo APIs, no direct DB access
- Security: JWT on all endpoints, user_id filters, input sanitization
- Performance: Pagination, caching, async processing

**Phase 3: Migration & Replacement**
- Delete: frontend/src/app/chat/page.tsx, standalone chatbot routes
- Modify: dashboard/page.tsx (add AI button), chat.py (refactor for dashboard), main.py (remove old route)
- Timeline: Deploy alongside → Monitor → Deprecate → Remove → Update docs

**Phase 4: Testing Strategy**
- Mandatory full system test (Auth, Todo UI, AI, Integration)
- Backend tests (ai_integration.test.py)
- Frontend tests (ai-chat.test.tsx)
- Security tests (JWT, user isolation, input sanitization)

**Phase 5: Deployment Plan**
- Vercel (frontend): Build, deploy, verify
- Hugging Face (backend): Push, verify, monitor
- Safety rules: No errors, no failures, all tests pass
- Rollback plan: Vercel rollback, git revert

**Phase 6: Monitoring & Observability**
- Metrics: Response time, success rate, engagement
- Logging: Backend (user_id, action, timing), Frontend (error tracking)

**Phase 7: Documentation**
- README updates: AI usage instructions, supported commands, security notes
- API documentation: OpenAPI docs at /docs endpoint

**Key Architectural Decisions Identified**:
1. Floating chat panel vs separate page (User requirement enforced)
2. Communication protocol: Simple HTTP (not SSE/WebSocket)

## Outcome

- ✅ Impact: Complete architectural blueprint for Phase 3 AI integration with zero Phase 2 duplication
- 🧪 Tests: Constitution compliance validated, all gates passed
- 📁 Files: Created plan.md with 7 phases, research tasks, contracts, deployment strategy
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks, `/sp.adr chat-integration-pattern` if ADR needed
- 🧠 Reflection: User's explicit requirement for "unified app" (not separate chatbot) is correctly enforced. Plan leverages existing Phase III infrastructure (Qwen, MCP, Conversation/Message tables) while removing standalone /chat route. Architecture is clean, secure, and implementable.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script during setup succeeded, no other failures
- Graders run and results (PASS/FAIL): Constitution compliance - PASS (all 6 principles, technical stack, architectural principles, security)
- Prompt variant (if applicable): Standard plan-creation workflow with user's explicit security and testing requirements
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to break down implementation into executable tasks, then execute via `/sp.implement`
