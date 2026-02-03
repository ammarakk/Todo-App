---
id: 002
title: Phase IV Infrastructure Implementation Plan
stage: plan
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-phase4-infra
branch: 005-phase4-infra
user: User
command: /sp.plan
labels: ["phase4","infrastructure","plan","kubernetes","docker","ollama","workstreams"]
links:
  spec: specs/005-phase4-infra/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase4-infra/plan.md
tests:
  - Constitution validation (PASSED - all Phase III and IV principles followed)
  - Technical context completeness (PASSED - all 6 research tasks defined)
  - Project structure definition (PASSED - /phase-4 folder layout documented)
  - Phase 0-2 planning breakdown (PASSED - research, design, implementation phases defined)
---

## Prompt

Good. This is where projects usually fall apart — planning is either too vague or too technical. We'll keep it execution-ready.

Below is /sp.plan for Phase IV from both Full-Stack and DevOps perspectives.


---

/sp.plan — Phase IV Execution Plan

Goal:
Turn Phase III app into a containerized, Kubernetes-orchestrated system with chatbot interface, without touching business logic.


---

1. Phase IV Workstreams

Stream    Owner    What It Covers

App Containerization    DevOps    Docker images for all services
Service Integration    Full-Stack    Safe connection between services
AI Runtime Setup    DevOps    Ollama container
Chatbot Layer    Full-Stack    Chat → API bridge
Kubernetes Orchestration    DevOps    Deployments, Services, Helm
Cluster Optimization    DevOps    Scaling, resources
System Validation    Both    End-to-end testing



---

2. Step-by-Step Plan


---

STEP 1 — Freeze Phase III (Protection Step)

Owner: Full-Stack
Purpose: Prevent accidental logic changes.

Tasks:

Copy Phase III into:

/phase-4/apps/todo-frontend
/phase-4/apps/todo-backend

Remove dev-only configs

Move secrets to .env variables


✅ Output: Apps run locally exactly like Phase III.


---

STEP 2 — Containerize Applications

Owner: DevOps

Create Docker image for each:

App    What Dockerfile Must Do

Frontend    Build UI and serve production build
Backend    Run API server
Chatbot    Run chatbot middleware server
Ollama    Use official Ollama image


Rules:

No hardcoded URLs

Use environment variables:

BACKEND_URL

OLLAMA_HOST

DB_URL



✅ Output: Each service runs independently via Docker.


---

STEP 3 — Build Chatbot Service

Owner: Full-Stack

This is NOT AI logic — it's translation.

Tasks:

1. Receive user message


2. Send to Ollama


3. Extract intent (create, update, delete, read)


4. Convert to API request


5. Call backend API


6. Return result to user



Chatbot responsibilities:

Natural language → JSON

JSON → REST API call


🚫 No business rules.

✅ Output: Chatbot can CRUD tasks through backend.


---

STEP 4 — Setup Kubernetes (Minikube)

Owner: DevOps

Tasks:

1. Start cluster


2. Configure Docker driver


3. Enable ingress if needed



This becomes the local cloud.


---

STEP 5 — Create Kubernetes Deployments

Owner: DevOps

Each service gets:

Resource    Purpose

Deployment    Pods
Service    Internal networking


Replica plan:

Service    Replicas

Frontend    2
Backend    2
Chatbot    1
Ollama    1


✅ Output: All services running as pods.


---

STEP 6 — Service Networking

Owner: Full-Stack + DevOps

Update apps to use:

Caller    Target

Frontend →    backend-service
Chatbot →    backend-service
Chatbot →    ollama-service


No localhost between containers.


---

STEP 7 — Helm Chart Creation

Owner: DevOps

Helm manages:

Deployments

Services

Replica counts

Environment variables

Resource limits


One Helm release:

helm install todo-app ./helm


---

STEP 8 — Resource Optimization

Owner: DevOps (kagent)

Set limits:

Service    CPU    Memory

Backend    Medium    Medium
Frontend    Low    Low
Ollama    High    High


Prevent cluster crashes.


---

STEP 9 — Scaling Test

Owner: DevOps

Test:

Scale backend to 3 replicas

Verify app still works

Confirm load balancing works



---

STEP 10 — End-to-End Validation

Owner: Both

Checklist:

Test    Expected

UI loads    Yes
Create task via UI    Works
Create task via chatbot    Works
Delete via chatbot    Works
Ollama responding    Yes
Pods stable    Yes



---

3. Responsibility Split Summary

Area    Full-Stack    DevOps

Business Logic    ❌    ❌
API Integration    ✅    ❌
Chatbot Bridge    ✅    ❌
Docker    ❌    ✅
Kubernetes    ❌    ✅
Helm    ❌    ✅
Scaling    ❌    ✅



---

4. Deployment Flow (High Level)

Code → Docker Images → Kubernetes Pods → Services Networked → Helm Manages → Chatbot Uses Ollama → Backend APIs → DB


---

5. What Happens After This Plan

Next logical command in spec-driven workflow:

/sp.tasks

That will break this plan into atomic implementation tasks for AI or engineers.


---

Brutal reality check

If someone:

Adds new API routes

Changes database schema

Adds smart automation


They broke Phase IV discipline.

This phase is about running the system like real infrastructure, not making it smarter.


---

Say the word and we go to /sp.tasks (the executable task list).

## Response snapshot

Successfully created comprehensive Phase IV implementation plan with execution-ready workstreams and technical decisions:

**Constitution Check**: ✅ PASSED
- All 6 Phase III principles (AI-Native, Stateless, Persistence, Security, Multi-Language, MCP) preserved
- All 5 Phase IV principles (Immutability, Spec-Driven, Ollama-First, Kubernetes-Native, AI DevOps) followed

**Technical Context Defined**:
- Languages: TypeScript/JavaScript (Next.js frontend), Python 3.11+ (FastAPI backend/chatbot), YAML (K8s manifests)
- Dependencies: Docker, Minikube, Helm 3.x, kubectl-ai, kagent, Gordon, Ollama (llama3.2/qwen2.5)
- Storage: Neon PostgreSQL (external), Ollama models in PVC
- Performance Goals: 5-min deploy, 60-sec pod startup, 10-sec chat latency, 50 concurrent users
- Constraints: 8GB RAM cluster, Phase III immutability, AI-generated infra only

**Project Structure**:
```
phase-4/
  apps/ (frontend, backend READ-ONLY, chatbot NEW)
  infra/ (docker/, helm/, k8s/ - ALL AI-GENERATED)
  ai/ollama/ (models, configs)
  docs/ (architecture, guides)
  scripts/ (setup, deploy, teardown)
```

**Phase 0: Research & Technology Decisions** (6 tasks):
- R-001: Docker multi-stage build strategy
- R-002: Kubernetes resource limits (CPU/memory per service)
- R-003: Helm chart structure (monolithic vs micro-charts)
- R-004: Ollama model selection (llama3.2:3b vs 7b vs qwen2.5:7b)
- R-005: Service discovery configuration (env vars vs ConfigMap)
- R-006: Minikube driver selection (Docker vs Hyperkit vs Podman)

**Phase 1: Design & Contracts**:
- Data model: NO changes (Phase III schemas locked)
- Contracts: Chatbot service API (NEW - /api/chat endpoint, JWT auth, intent extraction)
- Quickstart: 30-minute local setup guide (8 steps with troubleshooting)
- Agent context: Update with Kubernetes, Helm, Ollama, Minikube

**Phase 2: Implementation Planning** (7 workstreams):
1. App Containerization (DevOps) - Dockerfiles, env vars, security scanning
2. Service Integration (Full-Stack) - Service networking, JWT forwarding
3. AI Runtime Setup (DevOps) - Ollama image, model preloading, PVC
4. Chatbot Layer (Full-Stack) - FastAPI middleware, Ollama client, intent extraction
5. Kubernetes Orchestration (DevOps) - Minikube, manifests, deployments
6. Cluster Optimization (DevOps) - Resource limits, HPA, kagent monitoring
7. System Validation (Both) - E2E tests, scaling, rolling updates, regression

**Step-by-Step Execution Plan**:
1. Freeze Phase III (READ-ONLY copies in /apps)
2. Containerize Applications (Dockerfiles via Gordon)
3. Build Chatbot Service (FastAPI + Ollama client)
4. Setup Minikube (local cluster)
5. Create Kubernetes Deployments (Deployments + Services)
6. Service Networking (Kubernetes DNS, no IPs)
7. Helm Chart Creation (atomic deployment via helm install)
8. Resource Optimization (limits via kagent)
9. Scaling Test (2→5 replicas)
10. End-to-End Validation (UI, chatbot, CRUD, Ollama)

**Responsibility Matrix**:
- Full-Stack: API integration, chatbot bridge (NO business logic, NO Docker/K8s)
- DevOps: Docker, Kubernetes, Helm, scaling (NO application code changes)
- Both: System validation

**Deliverables**:
- Phase 0: research.md (6 technical decisions justified)
- Phase 1: data-model.md, contracts/chatbot-api.yaml, quickstart.md, agent context update
- Phase 2: tasks.md (via /sp.tasks - atomic implementation tasks)

## Outcome

- ✅ Impact: COMPREHENSIVE implementation plan - 10 execution steps, 7 workstreams, 6 research tasks, 3 design phases with clear deliverables and ownership
- 🧪 Tests: Constitution validation PASSED (11 principles validated), technical context completeness PASSED, project structure definition PASSED, phase breakdown PASSED
- 📁 Files: specs/005-phase4-infra/plan.md (912 lines - complete execution plan with research tasks, design phases, workstreams, responsibility matrix, step-by-step guide, next steps)
- 🔁 Next prompts: Phase 0 research execution (resolve 6 research tasks in research.md), then /sp.tasks to generate atomic implementation tasks, then /sp.implement to build infrastructure
- 🧠 Reflection: Plan successfully balances technical depth (6 research tasks with alternatives and decision criteria) with execution clarity (10 steps with owners, inputs, outputs). Constitution validation ensures no scope creep (Phase III locked, infra-only changes). Responsibility matrix prevents confusion (Full-Stack: integration/bridge, DevOps: infra/orchestration). Ready for Phase 0 research to resolve technical unknowns before task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation completed successfully with all sections filled
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all 11 principles validated, no violations)
  - Technical Context: PASS (all sections complete: languages, dependencies, storage, testing, platform, performance, constraints, scale)
  - Project Structure: PASS (complete /phase-4 layout with /apps, /infra, /ai, /docs, /scripts defined)
  - Phase 0 Research: PASS (6 research tasks defined with questions, alternatives, decision criteria)
  - Phase 1 Design: PASS (data model, contracts, quickstart, agent context update outlined)
  - Phase 2 Planning: PASS (7 workstreams defined with task breakdown and responsibility matrix)
- Prompt variant (if applicable): N/A (initial plan creation for Phase IV infrastructure)
- Next experiment (smallest change to try): Execute Phase 0 research tasks starting with R-001 (Docker multi-stage builds) and R-004 (Ollama model selection). These two decisions will unblock subsequent tasks (Dockerfiles and resource limits). Use kubectl-ai to generate sample Helm chart structure to validate R-003 decision. Use kagent to benchmark resource usage for R-002 after Minikube cluster is running.
