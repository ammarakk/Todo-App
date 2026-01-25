---
id: 2
title: phase-2-premium-saas-plan
stage: plan
date: 2025-01-23
surface: agent
model: claude-sonnet-4.5
feature: 001-phase-2-saas
branch: 001-phase-2-saas
user: User
command: /sp.plan
labels: [phase-2, saas, planning, architecture]
links:
  spec: specs/001-phase-2-saas/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-2-saas/plan.md
  - specs/001-phase-2-saas/research.md
  - specs/001-phase-2-saas/data-model.md
  - specs/001-phase-2-saas/contracts/openapi.json
  - specs/001-phase-2-saas/contracts/frontend-api.md
  - specs/001-phase-2-saas/quickstart.md
tests:
  - Constitution compliance check: PASSED
  - Phase 2 requirements validation: PASSED
  - Architecture decision review: PASSED
---

## Prompt

Perfect — ab hum is **premium Phase-2** ko **engineering-grade execution plan** me convert kar rahe hain.

Here is the **official `/sp.plan` for Phase-2**
(fully aligned with your last premium `/sp.specify`).

---

# **/sp.plan — Phase 2**

**Premium Web SaaS (Vercel + Neon + Hugging Face)**

---

## **PLAN OBJECTIVE**

Deliver a **production-ready SaaS web app** where:

* Phase-1 remains untouched
* Phase-2 adds web, auth, UI, database, and AI
* App is live on Vercel
* Uses Neon PostgreSQL
* Uses JWT + bcrypt
* Has premium UI

---

## **PLAN PHASE A — Project Foundation**

Purpose: Create a stable, professional web app base.

1. Initialize Next.js 14 (App Router, stable)
2. Configure Tailwind CSS
3. Install shadcn/ui
4. Install Framer Motion
5. Setup global layout, theme provider
6. Configure dark/light mode
7. Create project structure (app/, components/, lib/, api/)
8. Setup environment variable system

Output:
→ A running premium UI shell on localhost.

---

## **PLAN PHASE B — Backend API (FastAPI)**

Purpose: Turn Phase-1 into a web-connected engine.

1. Create FastAPI project
2. Install SQLModel
3. Connect to Neon PostgreSQL
4. Implement User model
5. Implement Todo model
6. Setup Alembic migrations
7. Create auth utilities (bcrypt + JWT)
8. Create auth middleware
9. Create REST routes
10. Test API with real DB

Output:
→ Secure API that can store users and todos.

---

## **PLAN PHASE C — Authentication System**

Purpose: Secure the SaaS.

1. Signup endpoint
2. Login endpoint
3. Password hashing
4. JWT generation
5. JWT verification
6. Session expiry
7. Protect all todo routes
8. User context injection
9. Logout handling
10. Auth error handling

Output:
→ Fully working auth system.

---

## **PLAN PHASE D — Web Auth UI**

Purpose: Premium login & signup.

1. Design login page
2. Design signup page
3. Form validation
4. Error messages
5. Loading states
6. Animated transitions
7. Auth API integration
8. Token storage
9. Auto-redirect after login

Output:
→ Beautiful, real SaaS auth flow.

---

## **PLAN PHASE E — Dashboard & Todo UI**

Purpose: Build the actual app.

1. Dashboard layout
2. User profile header
3. Todo list UI
4. Create todo modal
5. Edit todo page
6. Delete todo
7. Complete todo
8. Filters & search
9. Sorting
10. Stats cards
11. Skeleton loaders
12. Mobile layout

Output:
→ Full premium todo dashboard.

---

## **PLAN PHASE F — AI Integration (Hugging Face)**

Purpose: Add premium AI features.

1. Connect Hugging Face API
2. Create AI service layer
3. Generate todos from text
4. Summarize tasks
5. Prioritize tasks
6. UI for AI
7. Error handling
8. Loading animations

Output:
→ Working AI assistant inside app.

---

## **PLAN PHASE G — Production Hardening**

Purpose: Make it real SaaS-grade.

1. Input validation
2. API error formatting
3. Frontend error boundaries
4. Token expiry handling
5. CORS setup
6. Secure headers
7. Rate limiting
8. Logging

Output:
→ No fragile behavior.

---

## **PLAN PHASE H — Deployment**

Purpose: Go live.

1. Deploy FastAPI
2. Deploy Next.js on Vercel
3. Setup Neon database
4. Configure env variables
5. Test production login
6. Test production AI
7. Test mobile
8. Verify security

Output:
→ Live SaaS app.

---

## **PLAN PHASE I — Phase-2 Closure**

1. Verify all `/sp.specify` rules
2. Confirm no broken flows
3. Tag GitHub branch: `phase-2`
4. Phase-1 remains in `phase-1`

---

If you want, next I will generate:

**→ `/sp.tasks`** (50–80 atomic tasks)
that exactly implement this plan without chaos.

Say **"next"** when ready 🔥

## Response snapshot

Successfully created comprehensive Phase 2 implementation plan with complete technical architecture.

**Artifacts Generated**:

1. **plan.md** - Complete implementation plan with:
   - 14 phases (A-N) with detailed deliverables and validation
   - Technical context (stack, performance goals, constraints)
   - Constitution compliance check (PASSED)
   - Project structure for frontend/backend
   - Architecture Decision Records (ADR-001: Custom JWT)
   - Risk analysis with mitigation strategies
   - Success criteria mapping to implementation phases

2. **research.md** - Phase 0 research resolving all 10 open questions:
   - JWT token storage: httpOnly cookies selected
   - Avatar storage: Cloudinary free tier
   - AI models: Mistral 7B + BART
   - Database pooling: pool_size=10, max_overflow=20
   - Pagination: Offset-based for Phase 2
   - Rate limiting: slowapi library
   - Backend deployment: Render
   - AI prompts: Few-shot with JSON output
   - Testing: Playwright for E2E
   - Session refresh: Single 7-day JWT

3. **data-model.md** - Complete database schema:
   - 4 tables: users, todos, sessions, ai_requests
   - SQLModel definitions with relationships
   - Alembic migration SQL
   - Indexes and validation rules
   - Performance considerations

4. **contracts/openapi.json** - Full OpenAPI 3.0 spec:
   - 15 REST endpoints documented
   - Request/response schemas
   - Authentication flow
   - Error responses
   - Rate limiting notes

5. **contracts/frontend-api.md** - Frontend integration guide:
   - TypeScript types for all API operations
   - API client implementation
   - React hooks (useAuth, useTodos)
   - Usage examples
   - Error handling patterns

6. **quickstart.md** - Developer setup guide:
   - Prerequisites
   - Local development setup
   - Environment variables
   - Common commands
   - Troubleshooting

**Constitution Check**: ✅ PASSED (with noted auth library variance documented in ADR-001)

**Plan Phases**: 14 phases defined (A-N) with clear deliverables and validation criteria

## Outcome

- ✅ Impact: Complete engineering-grade plan for Phase 2 transformation from console to premium SaaS web application. All technical unknowns resolved with documented decisions.
- 🧪 Tests: Constitution compliance PASSED, architecture decisions validated, all research questions answered with rationale and alternatives considered
- 📁 Files: 6 files created/modified
  - specs/001-phase-2-saas/plan.md (comprehensive implementation plan)
  - specs/001-phase-2-saas/research.md (10 research decisions)
  - specs/001-phase-2-saas/data-model.md (database schema)
  - specs/001-phase-2-saas/contracts/openapi.json (API specification)
  - specs/001-phase-2-saas/contracts/frontend-api.md (integration guide)
  - specs/001-phase-2-saas/quickstart.md (developer setup)
- 🔁 Next prompts: `/sp.tasks` (generate 50-80 atomic implementation tasks), `/sp.implement` (execute implementation)
- 🧠 Reflection: Plan successfully balances comprehensiveness with clarity. All 14 phases build incrementally from foundation through deployment. Technical decisions are well-documented with rationale and alternatives. The research phase resolved all open questions before design began, following the spec-driven methodology. Constitution compliance verified with proper documentation for the one variance (custom JWT vs Better Auth).

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation completed successfully with all phases and artifacts
- Graders run and results (PASS/FAIL):
  - Constitution compliance: PASS (all Phase II requirements met, core principles followed)
  - Research completeness: PASS (10/10 questions resolved)
  - Data model: PASS (4 tables defined with relationships and migrations)
  - API contracts: PASS (15 endpoints documented with OpenAPI spec)
  - Quickstart: PASS (developer setup guide complete)
- Prompt variant (if applicable): N/A - first plan for Phase 2
- Next experiment (smallest change to try): Consider adding sequence diagrams for complex flows (login flow, AI request flow) in plan.md for additional clarity during implementation
