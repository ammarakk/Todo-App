---
id: 005
title: Spec Update - JWT Auth and Data Isolation Refinement
stage: spec
date: 2026-01-24
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-2-saas
branch: 001-phase-2-saas
user: User
command: /sp.specify
labels: [specification, jwt, authentication, data-isolation, phase-2]
links:
  spec: specs/001-phase-2-saas/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-2-saas/spec.md
  - specs/001-phase-2-saas/checklists/requirements.md
tests:
  - Specification quality validation (all checks passed)
  - Technology-agnostic requirements validation
  - Testable requirements validation
  - Success criteria measurability validation
---

## Prompt

SpecKit Specification — Phase 2 (Cloud‑Native Todo App)

1. Purpose

This specification defines Phase 2 of the Todo application. The goal is to evolve the system from a basic implementation into a secure, cloud‑native, production‑grade application using Spec‑Driven Development.

Phase 2 focuses strictly on:

Authentication

Secure CRUD operations

Premium‑baseline UI/UX


Anything not explicitly defined here is out of scope.


---

2. Scope Definition

In Scope

Signup & Login

JWT‑based authentication

User‑isolated task management (CRUD)

Responsive dashboard UI


Out of Scope

AI / Agents

MCP server

Voice or chat interfaces

Third‑party integrations



---

3. Authentication & Security Requirements

3.1 Authentication Model

The system MUST support user signup and login

Authentication MUST be based on JWT (JSON Web Tokens)


3.2 JWT Rules (STRICT)

Every protected API request MUST include:

Authorization: Bearer <JWT>

Backend MUST:

Verify JWT signature

Verify token expiration

Extract user_id from token


If token is missing, invalid, or expired:

Request MUST be rejected with 401 Unauthorized



3.3 Session Rules

User MUST remain logged in after page refresh

Logout MUST invalidate client‑side session



---

4. User Data Isolation (NON‑NEGOTIABLE)

Every task MUST belong to exactly one authenticated user

Backend MUST scope all database queries by user_id

A user MUST NOT be able to:

View other users' tasks

Edit other users' tasks

Delete other users' tasks



Any violation is considered a critical security failure.


---

5. Task Domain Model

Each task MUST contain the following fields:

id (unique identifier)

title (string, required)

completed (boolean)

priority (low | medium | high)

tags (array of strings)

created_at (timestamp)

user_id (owner reference)



---

6. Functional Requirements (CRUD)

6.1 Create Task

Authenticated users can create tasks

title is required

Default values:

completed = false

priority = medium



6.2 Read Tasks

Users can only view their own tasks

Tasks MUST be displayed in a list or card format


6.3 Update Task

Users can:

Edit task title

Update priority

Toggle completed status


Only the task owner can update a task


6.4 Delete Task

Users can delete their own tasks only



---

7. UI / UX Requirements (Premium + Advanced)

Phase 2 UI/UX MUST meet modern SaaS-level standards. Basic layouts are NOT acceptable.

7.1 Global UI Standards

Application MUST support Light Mode and Dark Mode

Theme toggle MUST be available on login, signup, and dashboard

Theme preference MUST persist across refresh

Layout MUST be fully responsive (mobile, tablet, desktop)

No horizontal scroll on any screen

UI MUST fit screen height without overflow issues



---

7.2 Authentication Pages (Login & Signup)

Login and Signup pages MUST be modern, accessible, and production-ready.

Mandatory Requirements:

Password visibility toggle (eye icon)

Inline field validation (required, min length, format)

Clear error messages below fields (not alerts)

Toast notification on authentication failure

Loading spinner / disabled button during submit

Proper spacing and alignment (no cramped UI)


UX Rules:

Enter key submits form

Focus state visible on inputs

Error state visually distinct



---

7.3 Dashboard UI (Advanced)

The dashboard MUST:

Use a responsive sidebar layout

Collapse sidebar on small screens

Highlight active navigation item


User Profile Section (Mandatory):

Dashboard MUST display authenticated user information

Show either:

User full name (preferred), OR

User email (fallback if name not available)


Profile info MUST be sourced from authenticated JWT / user session

Profile section MUST be visible in the sidebar or top header


Task Display:

Display task cards with:

Title

Priority badge (color-coded)

Tags



Productivity Controls:

Include search bar (search by title)

Include filters:

by status (completed / pending)

by priority


Include sort options:

by priority

by title




---

8. Error Handling

All API errors MUST return meaningful HTTP status codes

UI MUST display user‑friendly error messages

Silent failures are NOT allowed



---

9. Acceptance Criteria (PHASE 2 IS COMPLETE ONLY IF)

User can signup → login → reach dashboard

Page refresh does NOT log user out

User only sees their own tasks

Create / Read / Update / Delete works correctly

Unauthorized access is blocked

No console errors in production build


If any item fails, Phase 2 is considered incomplete.


---

10. Compliance Rule

Implementation MUST follow this specification exactly

No features may be added unless specified here

Fixes MUST be done by updating this spec, not manual hacking



---

✅ PHASE 2 COMPLETION CRITERIA (MANDATORY 💯)

Phase 2 will ONLY be considered complete when ALL conditions below are fully working — not visually, but functionally.

🔐 Authentication

Signup creates a real user in database

Login returns valid JWT

Token stored securely and used in all protected API calls

Logout clears session properly

Invalid login shows proper error message (not crash)


🎨 UI/UX Standards

Dark / Light mode fully working across entire app

Neon-accent professional theme (not plain default)

Fully responsive on mobile, tablet, desktop

No layout breaking, overflow, or cut screens

Password show/hide toggle working


📊 Dashboard

Sidebar layout stable

Active page indicator works

User profile section shows name or email dynamically

No "Page Not Found" routes


📝 Todo System (CORE OF PHASE 2)

All features must WORK with backend — not static UI.

Create Task → stored in database

Edit Task → updates in database

Delete Task → removes from database

Mark complete/incomplete works

Priority system (High / Medium / Low)

Tags system

Search tasks

Filter by status & priority

Sort by date and alphabetically


🔗 Frontend ↔ Backend Sync

No broken API calls

No dummy buttons

No console errors

Proper loading and error states


⚙ Backend Quality

JWT auth middleware working

User can only access own data

Database queries filtered by user ID

No exposed sensitive endpoints


🚀 DevOps Readiness

Frontend builds without Next.js errors

Backend runs without runtime crashes

Environment variables handled correctly

Ready for Vercel (FE) + HuggingFace (BE) deploy



---

❗ If ANY item above fails → Phase 2 is NOT complete.


---

🔁 REFINEMENT & ERROR RESOLUTION RULE (CRITICAL)

This project already has working parts. Agents must improve and upgrade the system — NOT rebuild carelessly.

🧩 EXISTING WORK PROTECTION

Previously working features must NOT be broken

Refactoring must be controlled and tested

No removal of working logic without replacement


🐞 EXISTING ERRORS MUST BE FIXED

Agents must identify and resolve earlier problems including:

Broken UI themes (dark mode, neon styling issues)

Non-working login/signup buttons

Screen responsiveness issues

"Page not found" routing problems

Todo features showing in UI but failing functionally

Basic or incomplete profile form


Fix root causes, not surface patches.

🧠 THINK BEFORE CODING

Agents must:

Analyze system before edits

Understand dependency chains

Avoid rushed code changes

Write structured, maintainable logic


🧪 STABILITY BEFORE NEXT PHASE

Phase 2 must end with:

Stable codebase

No recurring bugs

Clean architecture

Fully working Todo system

Professional UI


Only after refinement + stability → project can move to Phase 3.

Added.

Ab document mein clear hai:

Purana kaam todna mana hai

Pehle ke saare errors fix karna mandatory hai

Refactor with thinking, not random edits

Stability ke bina Phase 3 allowed nahi


Ye ab student project nahi raha — ye controlled production refinement process ban gaya.

Next bolein to agents ke execution prompt ko final lock kar dete hain.

## Response snapshot

Successfully updated Phase 2 specification with emphasis on:

1. **JWT-based Authentication**: Clear requirements for JWT token issuance, validation (signature + expiration), and inclusion in Authorization header for all protected requests
2. **User Data Isolation**: NON-NEGOTIABLE section added with 6 dedicated requirements (FR-018 through FR-023) ensuring users can only access their own data through user_id scoping in all database queries
3. **Todo Domain Model**: Fully specified with required fields (id, title, completed, priority, tags, created_at, user_id) and default values
4. **Out of Scope**: Explicitly excluded AI/Agents, MCP server, voice/chat interfaces, and third-party integrations
5. **Completion Criteria**: 38 specific checklist items organized by category (Authentication, UI/UX, Dashboard, Todo System, etc.) emphasizing functional working over visual completeness

Specification quality validation completed with all checks passing:
- 83 Functional Requirements (FR-001 through FR-083)
- 14 Success Criteria (all measurable and technology-agnostic)
- 16 Edge Cases identified
- 6 User Stories with prioritized independent test criteria
- 19 Out of Scope items clearly defined

Updated files:
- specs/001-phase-2-saas/spec.md (completely rewritten with JWT and data isolation focus)
- specs/001-phase-2-saas/checklists/requirements.md (validation completed, all checks passed)

## Outcome

- ✅ Impact: Specification now clearly defines JWT authentication requirements and user data isolation as NON-NEGOTIABLE security requirements. All 83 functional requirements are testable and unambiguous. Ready for architecture planning.
- 🧪 Tests: Specification quality validation completed - all checks passed (content quality, requirement completeness, feature readiness, technology-agnostic success criteria)
- 📁 Files: Updated spec.md with JWT authentication requirements, user data isolation section, todo domain model, and completion criteria checklist. Created requirements checklist with validation results.
- 🔁 Next prompts: /sp.plan (generate implementation architecture), /sp.tasks (create actionable task list), /sp.clarify (optional - explore requirements in detail)
- 🧠 Reflection: Specification successfully refined from previous version to emphasize JWT-based authentication and user data isolation as critical security requirements. Removed AI/Agent features from scope to align with Phase 2 focus on core authentication and CRUD operations. Completion criteria explicitly states "functionally working" requirement, not just visual completeness.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification validation passed all checks
- Graders run and results (PASS/FAIL): Specification quality checklist - PASS (12/12 items)
- Prompt variant (if applicable): N/A - direct specification update from user requirements document
- Next experiment (smallest change to try): Proceed to /sp.plan to generate architecture design for JWT authentication implementation and user data isolation enforcement
