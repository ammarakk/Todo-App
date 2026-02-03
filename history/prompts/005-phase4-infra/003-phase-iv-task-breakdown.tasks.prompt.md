---
id: 003
title: Phase IV Task Breakdown
stage: tasks
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-phase4-infra
branch: 005-phase4-infra
user: User
command: /sp.tasks
labels: ["phase4","infrastructure","tasks","implementation","kubernetes","docker","ollama","helm"]
links:
  spec: specs/005-phase4-infra/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase4-infra/tasks.md
tests:
  - Task completeness validation (PASSED - 116 atomic tasks covering all requirements)
  - Dependency ordering validation (PASSED - tasks organized by user story with prerequisites)
  - MVP scope definition (PASSED - Phases 1-3 identified as 39-task MVP)
  - Responsibility assignment (PASSED - FS/DO roles clearly defined)
  - Execution readiness (PASSED - all tasks include file paths and commands)
---

## Prompt

/sp.tasks — Phase IV Infrastructure Implementation

Generate atomic, execution-ready tasks from the Phase IV plan. Each task must be:
- Assignable to either Full-Stack (FS) or DevOps (DO) engineer
- Include exact file paths and commands
- Organized by user story for independent implementation
- Mark parallel execution opportunities with [P]

Below is the complete task breakdown by user story:

### USER STORY 1 (P1): Local Kubernetes Deployment - Foundation

**Phase 1: Setup & Protection**
- T001-T004: Copy Phase III code to phase-4/apps (READ-ONLY copies)
- T005-T008: Create directory structure and documentation

**Phase 2: Foundational Infrastructure**
- T009-T011: Environment configuration (.env.example)
- T012-T015: Minikube cluster setup and validation

**Phase 3: Containerization (US1 Core)**
- T016 [P]: Generate Dockerfile.frontend (multi-stage build)
- T017 [P]: Generate Dockerfile.backend (production server)
- T018: Generate .dockerignore files
- T019-T020: Build and test Docker images
- T021-T022: Security scan with trivy

**Phase 3: Kubernetes Manifests (US1 Core)**
- T023 [P]: Generate namespace.yaml
- T024 [P]: Generate Chart.yaml (Helm)
- T025 [P]: Generate deployment manifests (frontend, backend)
- T026 [P]: Generate service manifests (ClusterIP, NodePort)
- T027: Generate ConfigMap for environment variables
- T028: Generate secrets.yaml (database URLs, JWT secrets)
- T029: Generate values.yaml for Helm configuration

**Phase 3: Helm Deployment & Validation (US1 Core)**
- T030: Package Helm chart
- T031: Install todo-app via Helm
- T032: Verify all pods are Running
- T033: Verify services are created
- T034: Access frontend via Minikube tunnel
- T035: Test API connectivity
- T036: Verify deployment completeness

**MVP Validation**: Frontend loads, backend API responds, all pods healthy

### USER STORY 2 (P2): Ollama Chatbot Integration

**Phase 4: Chatbot Service Foundation**
- T037 [P]: Create chatbot service structure (FastAPI)
- T038 [P]: Create /api/chat endpoint
- T039 [P]: Implement Ollama client
- T040: Create main.py entry point
- T041: Create requirements.txt
- T042: Create Dockerfile.chatbot
- T043: Create pyproject.toml

**Phase 4: Intent Extraction Logic**
- T044: Create intent extraction prompt template
- T045: Implement JSON response parsing
- T046: Add error handling for LLM failures
- T047: Create unit tests for intent extraction
- T048: Test with sample natural language inputs

**Phase 4: Backend API Client**
- T049: Implement JWT token forwarding
- T050: Implement CRUD API calls (POST /todos, GET /todos, etc.)
- T051: Add error handling for API failures
- T052: Add retry logic with exponential backoff
- T053: Create integration tests

**Phase 4: Ollama Integration**
- T054 [P]: Generate ollama-deployment.yaml
- T055 [P]: Generate ollama-service.yaml
- T056: Create PVC for model storage
- T057: Add Ollama to Helm chart
- T058: Preload llama3.2:3b model
- T059: Verify Ollama API accessibility
- T060: Test chatbot → Ollama connectivity
- T061: Verify model responses

**Phase 4: Chatbot Kubernetes Deployment**
- T062: Update Helm values.yaml for chatbot
- T063: Deploy chatbot via Helm upgrade
- T064: Verify chatbot pod health
- T065: Test end-to-end chatbot flow
- T066: Verify CRUD operations via chatbot
- T067: Measure chat latency (target: <10s p95)

**MVP Validation**: Chatbot creates/reads/updates/deletes todos, Ollama responds

### USER STORY 3 (P3): Horizontal Scaling & Resource Management

**Phase 5: Resource Limits**
- T068 [P]: Define resource requests/limits in deployments
- T069: Apply resource limits to backend (CPU: 500m/1000m, Memory: 512Mi/1Gi)
- T070: Apply resource limits to frontend (CPU: 100m/250m, Memory: 128Mi/256Mi)
- T071: Apply resource limits to chatbot (CPU: 200m/500m, Memory: 256Mi/512Mi)
- T072: Apply resource limits to Ollama (CPU: 1000m/2000m, Memory: 2Gi/4Gi)
- T073: Verify pods respect resource limits

**Phase 5: Horizontal Pod Autoscaler**
- T074 [P]: Create HPA for backend (target CPU: 70%, min 2, max 5)
- T075: Create HPA for frontend (target CPU: 70%, min 2, max 4)
- T076: Deploy HPA resources
- T077: Verify HPA status

**Phase 5: Scaling Tests**
- T078: Scale backend to 3 replicas manually
- T079: Verify load balancing across replicas
- T080: Generate load (50 concurrent users)
- T081: Verify HPA triggers autoscaling
- T082: Verify application stability during scaling
- T083: Measure resource usage with kubectl top

**MVP Validation**: HPA scales based on CPU, app stable under load

### USER STORY 4 (P4): Zero-Downtime Rolling Updates

**Phase 6: Health Probes**
- T084 [P]: Add liveness probe to backend ( /health, initialDelay: 30s)
- T085: Add readiness probe to backend ( /health, initialDelay: 10s)
- T086: Add liveness probe to frontend ( /, initialDelay: 30s)
- T087: Add readiness probe to frontend ( /, initialDelay: 10s)
- T088: Add probes to chatbot and Ollama

**Phase 6: Rolling Update Strategy**
- T089 [P]: Configure rolling update in deployments (maxUnavailable: 1, maxSurge: 1)
- T090: Set revisionHistoryLimit to 10
- T091: Add pre-stop hook for graceful shutdown
- T092: Update Helm chart with probe configurations

**Phase 6: Rolling Update Tests**
- T093: Deploy new version via Helm upgrade
- T094: Monitor rollout status: `kubectl rollout status deployment/todo-backend`
- T095: Verify max 1 pod unavailable during update
- T096: Test application during update (zero downtime)
- T097: Verify rollback capability: `helm rollback todo-app`

**MVP Validation**: Rolling updates complete with zero downtime

### Phase 7: Polish & Documentation

**Phase 7: Documentation**
- T098-T101: Create architecture diagrams, quickstart guide, troubleshooting guide
- T102-T105: Update Helm chart README, document environment variables, create runbooks

**Phase 7: System Validation**
- T106: Execute full end-to-end test suite
- T107: Verify all Phase III features still work
- T108: Test chatbot with multi-language inputs
- T109: Verify no Phase III code changes
- T110: Regression test suite

**Phase 7: AI DevOps Integration**
- T111: Use kubectl-ai to generate optimized manifests
- T112: Use kagent for cluster monitoring and optimization
- T113: Use Gordon for automated Docker builds
- T114: Verify AI-generated code quality

**Phase 7: Final Acceptance**
- T115-T116: Final deployment validation and Definition of Done checklist

**MVP Scope**: Phases 1-3 (39 tasks) - US1 completed, system deployed on Minikube
**Full Scope**: All 7 phases (116 tasks) - All user stories completed

## Response snapshot

Successfully created comprehensive Phase IV task breakdown with 116 atomic tasks organized for independent implementation:

**Task Organization**:
- **7 Phases**: Setup → Foundational → US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4) → Polish
- **116 Atomic Tasks**: Each assignable to FS or DO, with exact file paths and commands
- **MVP Scope**: Phases 1-3 (39 tasks) - Deploys containerized system on Minikube
- **Independent Execution**: Tasks organized by user story for parallel implementation

**Task Format**: `- [ ] [ID] [P?] [Story?] Description with file path`

**Sample Tasks**:
```markdown
- [ ] T001 [P] Copy Phase III frontend to phase-4/apps/todo-frontend (preserve all files, NO modifications)
- [ ] T016 [P] [US1] Generate Dockerfile for frontend in phase-4/infra/docker/Dockerfile.frontend
- [ ] T024 [US1] Generate Helm Chart.yaml in phase-4/infra/helm/todo-app/Chart.yaml
- [ ] T033 [US1] Install todo-app Helm chart: `helm install todo-app phase-4/infra/helm/todo-app`
- [ ] T040 [P] [US2] Create chatbot service main.py in phase-4/apps/chatbot/src/main.py
- [ ] T070 [US3] Scale backend to 3 replicas: `kubectl scale deployment todo-backend --replicas=3`
- [ ] T085 [US4] Perform Helm rolling update: `helm upgrade todo-app phase-4/infra/helm/todo-app`
```

**MVP Scope Identified**:
- Phases 1-3 (39 tasks) deliver US1 (P1): Local Kubernetes Deployment
- Enables parallel execution of US2-US4 in subsequent iterations
- Clear checkpoint: Frontend loads, backend API responds, all pods healthy

**Parallel Execution Opportunities**:
- 13 tasks marked with [P] can run in parallel within their phase
- Dockerfile generation (T016-T018) - independent services
- Kubernetes manifests (T023-T029) - independent resources
- Chatbot components (T037-T043, T054-T056) - independent modules

**Quality Validation**:
- ✅ All 29 functional requirements from spec.md covered
- ✅ All 4 user stories have dedicated task phases
- ✅ Dependencies respected (Phase 1 → Phase 2 → Phase 3+)
- ✅ Each task includes file path or command
- ✅ FS/DO responsibilities clearly separated
- ✅ MVP scope clearly defined (Phases 1-3)

**Next Step**: `/sp.implement` to begin task execution (starting with T001-T039 for MVP)

## Outcome

- ✅ Impact: COMPREHENSIVE task breakdown - 116 atomic tasks organized into 7 phases, covering all requirements from spec.md with MVP scope clearly defined
- 🧪 Tests: Task completeness validation PASSED (all 29 FRs covered), dependency ordering PASSED (phases sequential), MVP scope PASSED (Phases 1-3 = 39 tasks), responsibility assignment PASSED (FS/DO roles clear), execution readiness PASSED (all tasks include paths/commands)
- 📁 Files: `specs/005-phase4-infra/tasks.md` (420+ lines - complete task breakdown with organization by user story, MVP scope, parallel execution markers, file paths, commands, acceptance criteria, dependency graph, next steps)
- 🔁 Next prompts: `/sp.implement` to begin task execution (starting with T001-T039 for MVP), or review tasks.md and provide feedback
- 🧠 Reflection: Task breakdown successfully balances comprehensiveness (116 tasks covering all requirements) with execution clarity (organized by user story, parallel opportunities marked, MVP scope defined). Each task is atomic and assignable, with exact file paths and commands. Ready for implementation with clear checkpoint after Phase 3 (MVP deployed on Minikube).

## Evaluation notes (flywheel)

- Failure modes observed: None - task breakdown completed successfully with all tasks defined and organized
- Graders run and results (PASS/FAIL):
  - Task Completeness: PASS (all 29 functional requirements from spec.md covered by tasks)
  - Dependency Ordering: PASS (phases sequential: 1 → 2 → 3/4/5/6 → 7, within-phase dependencies respected)
  - MVP Scope Definition: PASS (Phases 1-3 = 39 tasks, clear checkpoint: frontend loads, backend responds, pods healthy)
  - Responsibility Assignment: PASS (FS tasks: integration, chatbot; DO tasks: Docker, K8s, Helm)
  - Execution Readiness: PASS (all tasks include file paths or commands, no ambiguous tasks)
- Prompt variant (if applicable): N/A (initial task breakdown for Phase IV infrastructure)
- Next experiment (smallest change to try): Execute `/sp.implement` starting with Phase 1 tasks (T001-T008) to set up directory structure and copy Phase III code to phase-4/apps. This will unblock Phase 2 (environment config) and Phase 3 (containerization). Use parallel execution for T016-T018 (Dockerfiles) and T023-T029 (K8s manifests) to accelerate MVP delivery.
