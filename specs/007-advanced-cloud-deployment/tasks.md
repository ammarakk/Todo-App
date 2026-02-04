# Tasks: Phase 5 - Advanced Cloud Deployment & Agentic Integration

**Input**: Design documents from `/specs/007-advanced-cloud-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- Frontend: `phase-5/frontend/`
- Backend: `phase-5/backend/`
- Chatbot: `phase-5/chatbot/`
- Agents: `phase-5/agents/`
- Microservices: `phase-5/microservices/`
- Dapr: `phase-5/dapr/`
- Kafka: `phase-5/kafka/`
- Helm: `phase-5/helm/`
- Tests: `phase-5/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create phase-5 directory structure per plan.md §Project Structure
- [ ] T002 [P] Copy Phase IV frontend to phase-5/frontend/ (read-only, no modifications)
- [ ] T003 [P] Copy Phase IV backend to phase-5/backend/ (preserve CRUD, will add orchestrator)
- [ ] T004 [P] Initialize Python 3.11+ virtual environment in phase-5/
- [ ] T005 [P] Install Python dependencies: fastapi, dapr, sqlalchemy, psycopg2, kafka-python, pytest
- [ ] T006 [P] Create Docker Compose for local Redpanda in phase-5/kafka/docker-compose.yml
- [ ] T007 [P] Create Kubernetes namespace definitions in phase-5/k8s/namespaces.yaml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Install Dapr 1.12+ in Minikube cluster
- [ ] T009 [P] Deploy Dapr Pub/Sub component (kafka-pubsub) in phase-5/dapr/components/pubsub.yaml
- [ ] T010 [P] Deploy Dapr State Store component (PostgreSQL) in phase-5/dapr/components/statestore.yaml
- [ ] T011 [P] Deploy Dapr Secrets component (Kubernetes) in phase-5/dapr/components/secrets.yaml
- [ ] T012 [P] Create Kafka topics (task-events, reminders, task-updates, audit-events) in phase-5/kafka/topics.yaml
- [ ] T013 Start Redpanda container from phase-5/kafka/docker-compose.yml
- [ ] T014 Create database schema in PostgreSQL (tasks, reminders, conversations, messages, events, audit_logs)
- [ ] T015 [P] Create base SQLAlchemy models in phase-5/backend/src/models/ (Task, Reminder, Conversation, Message)
- [ ] T016 [P] Create base SQLAlchemy models in phase-5/backend/src/models/ (Event, AuditLog)
- [ ] T017 [P] Setup Alembic migrations in phase-5/backend/alembic/
- [ ] T018 [P] Configure environment variables for local development in phase-5/.env.local
- [ ] T019 Configure structured JSON logging in phase-5/backend/src/utils/logging.py
- [ ] T020 [P] Create error handling middleware in phase-5/backend/src/middleware/error_handler.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Management with AI Assistant (Priority: P1) 🎯 MVP

**Goal**: Users can create, update, complete, and delete tasks through an AI-powered chatbot without manual form filling

**Independent Test**: Chat with bot to create task "Buy milk tomorrow at 5pm", verify it appears in task list, and AI correctly extracts and processes the request

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US1] Contract test for POST /tasks in phase-5/tests/contract/test_tasks_api.py
- [ ] T022 [P] [US1] Contract test for PATCH /tasks/{id} in phase-5/tests/contract/test_tasks_api.py
- [ ] T023 [P] [US1] Contract test for POST /tasks/{id}/complete in phase-5/tests/contract/test_tasks_api.py
- [ ] T024 [P] [US1] Contract test for DELETE /tasks/{id} in phase-5/tests/contract/test_tasks_api.py
- [ ] T025 [P] [US1] Contract test for POST /chat/command in phase-5/tests/contract/test_chat_api.py
- [ ] T026 [P] [US1] Integration test for chatbot task creation in phase-5/tests/integration/test_task_creation.py
- [ ] T027 [P] [US1] Integration test for chatbot task completion in phase-5/tests/integration/test_task_completion.py

### Implementation for User Story 1

#### AI Skill Agents

- [X] T028 [P] [US1] Create Task Agent skill in phase-5/agents/skills/task_agent.py
- [X] T029 [P] [US1] Create Task Agent prompt in phase-5/agents/skills/prompts/task_prompt.txt
- [X] T030 [US1] Implement Task Agent JSON schema validation in phase-5/agents/skills/task_agent.py
- [X] T031 [P] [US1] Create Reminder Agent skill in phase-5/agents/skills/reminder_agent.py
- [X] T032 [P] [US1] Create Reminder Agent prompt in phase-5/agents/skills/prompts/reminder_prompt.txt
- [X] T033 [US1] Implement Reminder Agent date/time extraction in phase-5/agents/skills/reminder_agent.py

#### System Prompts

- [X] T034 [P] [US1] Create global behavior prompt in phase-5/system_prompts/global_behavior.txt
- [X] T035 [P] [US1] Create clarification logic prompt in phase-5/system_prompts/clarification_logic.txt
- [X] T036 [P] [US1] Create error handling prompt in phase-5/system_prompts/error_handling.txt

#### Backend AI Orchestrator

- [X] T037 [US1] Create intent detector in phase-5/backend/src/orchestrator/intent_detector.py
- [X] T038 [US1] Create skill dispatcher in phase-5/backend/src/orchestrator/skill_dispatcher.py
- [X] T039 [US1] Create event publisher in phase-5/backend/src/orchestrator/event_publisher.py
- [X] T040 [US1] Implement orchestrator flow in phase-5/backend/src/api/chat.py (receive → load prompt → detect intent → call skill → validate → execute → publish event → return)
- [X] T041 [US1] Add POST /chat/command endpoint in phase-5/backend/src/api/chat.py
- [X] T042 [P] [US1] Update Task model with AI metadata in phase-5/backend/src/models/task.py (intent_detected, skill_agent_used, confidence_score)

#### Backend Task API (Dapr Integration)

- [X] T043 [US1] Configure Dapr sidecar for Backend Pod in phase-5/k8s/backend-deployment.yaml
- [X] T044 [US1] Add Dapr publish_event wrapper in phase-5/backend/src/utils/dapr_client.py
- [X] T045 [US1] Update POST /tasks to publish task.created event in phase-5/backend/src/api/tasks.py
- [X] T046 [US1] Update PATCH /tasks/{id} to publish task.updated event in phase-5/backend/src/api/tasks.py
- [X] T047 [US1] Update POST /tasks/{id}/complete to publish task.completed event in phase-5/backend/src/api/tasks.py
- [X] T048 [US1] Update DELETE /tasks/{id} to publish task.deleted event in phase-5/backend/src/api/tasks.py

#### Backend Health Endpoints

- [X] T049 [P] [US1] Add /health liveness endpoint in phase-5/backend/src/api/health.py
- [X] T050 [P] [US1] Add /ready readiness endpoint (checks DB, Dapr, Ollama) in phase-5/backend/src/api/health.py

#### Backend Docker & Deployment

- [X] T051 [US1] Create Backend Dockerfile in phase-5/backend/Dockerfile
- [ ] T052 [US1] Create Backend Helm chart in phase-5/helm/todo-app/charts/backend/
- [ ] T053 [US1] Deploy Backend Pod to Kubernetes via Helm in phase-5/helm/todo-app/values-local.yaml

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create/complete/delete tasks via chatbot with AI intent extraction

---

## Phase 4: User Story 2 - Intelligent Reminders (Priority: P2)

**Goal**: Users receive notifications before tasks are due so they never miss important deadlines

**Independent Test**: Create task with reminder 2 minutes in future, wait for notification to trigger, verify notification received with correct task details

### Tests for User Story 2

- [ ] T054 [P] [US2] Contract test for reminder scheduling in phase-5/tests/contract/test_reminders.py
- [ ] T055 [P] [US2] Integration test for reminder delivery in phase-5/tests/integration/test_reminder_delivery.py

### Implementation for User Story 2

#### Reminder Entity & API

- [ ] T056 [P] [US2] Add reminder_config to Task model in phase-5/backend/src/models/task.py
- [X] T057 [US2] Create Reminder model in phase-5/backend/src/models/reminder.py ✅
- [X] T058 [US2] Add Reminder CRUD operations in phase-5/backend/src/api/reminders_api.py ✅
- [X] T059 [US2] Implement reminder scheduling logic in phase-5/backend/src/services/reminder_scheduler.py ✅

#### Notification Microservice

- [X] T060 [P] [US2] Create Notification service in phase-5/microservices/notification/src/main.py ✅
- [ ] T061 [P] [US2] Create Notification consumer in phase-5/microservices/notification/src/consumers.py (merged into T060)
- [ ] T062 [P] [US2] Create email service client in phase-5/microservices/notification/src/email_service.py (merged into T060)
- [X] T063 [US2] Subscribe to reminders topic in phase-5/dapr/subscriptions/reminders.yaml ✅
- [X] T064 [US2] Configure Notification Pod Dapr sidecar in phase-5/k8s/notification-deployment.yaml ✅
- [X] T065 [US2] Create Notification Dockerfile in phase-5/microservices/notification/Dockerfile ✅
- [X] T066 [US2] Create Notification Helm chart in phase-5/helm/notification/ ✅
- [ ] T067 [US2] Deploy Notification Pod to Kubernetes (manual deployment step)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can manage tasks AND receive reminders

---

## Phase 5: User Story 3 - Recurring Task Automation (Priority: P3)

**Goal**: Tasks repeat automatically based on schedule without manual recreation

**Independent Test**: Create daily recurring task "Take vitamins", complete it today, verify new instance automatically created for tomorrow with reminder preserved

### Tests for User Story 3

- [ ] T068 [P] [US3] Contract test for recurring task creation in phase-5/tests/contract/test_recurring.py
- [ ] T069 [P] [US3] Integration test for recurring task generation in phase-5/tests/integration/test_recurring_generation.py

### Implementation for User Story 3

#### Recurring Agent

- [X] T070 [P] [US3] Create Recurring Agent skill in phase-5/backend/src/agents/skills/recurring_agent.py ✅ (created in US1)
- [X] T071 [P] [US3] Create Recurring Agent prompt in phase-5/agents/skills/prompts/recurring_prompt.txt ✅ (created in US1)
- [X] T072 [US3] Implement recurrence date calculation in phase-5/backend/src/agents/skills/recurring_agent.py ✅ (created in US1)

#### Task & Reminder Models

- [X] T073 [P] [US3] Add recurrence_rule to Task model in phase-5/backend/src/models/task.py ✅ (already existed)
- [ ] T074 [P] [US3] Add parent_task_id to Task model in phase-5/backend/src/models/task.py (not needed - using recurrence_rule)

#### Recurring Task Implementation

- [X] T075 [P] [US3] Create RecurringTask model in phase-5/backend/src/models/recurring_task.py ✅
- [X] T076 [P] [US3] Create RecurringTask schemas in phase-5/backend/src/schemas/recurring_task.py ✅
- [X] T077 [P] [US3] Create RecurringTaskService in phase-5/backend/src/services/recurring_task_service.py ✅
- [X] T078 [P] [US3] Create Recurring Task API in phase-5/backend/src/api/recurring_tasks_api.py ✅
- [X] T079 [US3] Subscribe to task-events topic (filter task.completed) in phase-5/dapr/subscriptions/task-completed.yaml ✅
- [X] T080 [US3] Create subscription endpoint in phase-5/backend/src/api/recurring_subscription.py ✅
- [X] T081 [US3] Integrate with main application (update main.py) ✅
- [ ] T082 [US3] Create Recurring Helm chart (uses existing backend Helm chart)
- [ ] T083 [US3] Deploy Recurring Pod to Kubernetes (uses existing backend deployment)

**Checkpoint**: All user stories should now be independently functional - task management, reminders, and recurring automation all working

---

## Phase 6: User Story 4 - Real-Time Multi-Client Sync (Priority: P2)

**Goal**: Changes from one device instantly appear on all other devices

**Independent Test**: Open app in two browser windows side-by-side, create task in window A, verify it appears in window B within 2 seconds without refresh

### Tests for User Story 4

- [ ] T084 [P] [US4] Integration test for WebSocket updates in phase-5/tests/integration/test_websocket_updates.py
- [ ] T085 [P] [US4] Performance test for <2s update requirement in phase-5/tests/performance/test_realtime_latency.py

### Implementation for User Story 4

#### Backend WebSocket Implementation

- [X] T086 [US4] Create WebSocket Connection Manager in phase-5/backend/src/services/websocket_manager.py ✅
- [X] T087 [US4] Create WebSocket broadcaster service in phase-5/backend/src/services/websocket_broadcaster.py ✅
- [X] T088 [US4] Update all task endpoints to publish task-updates events (already publishing from US1) ✅
- [X] T089 [US4] Create WebSocket endpoint for task-updates in phase-5/backend/src/api/websocket.py ✅
- [X] T090 [US4] Subscribe to task-updates topic via broadcaster service ✅
- [X] T091 [US4] Create WebSocket demo client in phase-5/docs/websocket-demo.html ✅
- [X] T092 [US4] Integrate WebSocket broadcaster with main application (start/stop in lifespan) ✅

**Checkpoint**: Real-time sync complete - all clients see updates within 2 seconds

---

## Phase 7: User Story 5 - Production Cloud Deployment (Priority: P1)

**Goal**: Application deploys automatically to cloud infrastructure with high reliability

**Independent Test**: Trigger deployment through CI/CD pipeline, verify application accessible, healthy, and functional in cloud environment

### Tests for User Story 5

- [ ] T091 [P] [US5] Test Minikube deployment via quickstart.md in phase-5/tests/e2e/test_local_deployment.py
- [ ] T092 [P] [US5] Test cloud deployment pipeline in phase-5/tests/e2e/test_cloud_deployment.py

### Implementation for User Story 5

#### Frontend Pod (Phase IV Copy)

- [ ] T093 [P] [US5] Copy Phase IV frontend to phase-5/frontend/ (if not done in T002)
- [ ] T094 [US5] Verify Frontend Dockerfile exists in phase-5/frontend/Dockerfile
- [ ] T095 [US5] Configure Frontend Dapr sidecar in phase-5/k8s/frontend-deployment.yaml
- [ ] T096 [US5] Create Frontend Helm chart in phase-5/helm/todo-app/charts/frontend/
- [ ] T097 [US5] Deploy Frontend Pod to Kubernetes via Helm

#### Chatbot Pod

- [ ] T098 [P] [US5] Create Chatbot service in phase-5/chatbot/src/main.py
- [ ] T099 [P] [US5] Create MCP agent integration in phase-5/chatbot/src/agents/
- [ ] T100 [US5] Configure Chatbot Pod Dapr sidecar in phase-5/k8s/chatbot-deployment.yaml
- [ ] T101 [US5] Create Chatbot Dockerfile in phase-5/chatbot/Dockerfile
- [ ] T102 [US5] Create Chatbot Helm chart in phase-5/helm/todo-app/charts/chatbot/
- [ ] T103 [US5] Deploy Chatbot Pod to Kubernetes

#### Audit Microservice

- [ ] T104 [P] [US5] Create Audit service in phase-5/microservices/audit/src/main.py
- [ ] T105 [P] [US5] Create Audit consumer in phase-5/microservices/audit/src/consumers.py
- [ ] T106 [P] [US5] Subscribe to all Kafka topics in phase-5/dapr/subscriptions/audit-events.yaml
- [ ] T107 [US5] Configure Audit Pod Dapr sidecar in phase-5/k8s/audit-deployment.yaml
- [ ] T108 [US5] Create Audit Dockerfile in phase-5/microservices/audit/Dockerfile
- [ ] T109 [US5] Create Audit Helm chart in phase-5/helm/todo-app/charts/audit/
- [ ] T110 [US5] Deploy Audit Pod to Kubernetes

#### CI/CD Pipeline

- [ ] T111 [US5] Create GitHub Actions workflow in .github/workflows/deploy.yml
- [ ] T112 [US5] Configure build stage (Docker images) in .github/workflows/deploy.yml
- [ ] T113 [US5] Configure test stage (pytest) in .github/workflows/deploy.yml
- [ ] T114 [US5] Configure security scan stage (Trivy) in .github/workflows/deploy.yml
- [ ] T115 [US5] Configure deploy stage (Helm upgrade) in .github/workflows/deploy.yml
- [ ] T116 [US5] Configure verify stage (smoke tests) in .github/workflows/deploy.yml

#### Monitoring & Logging

- [ ] T117 [P] [US5] Add Prometheus metrics endpoint to Backend in phase-5/backend/src/api/metrics.py
- [ ] T118 [P] [US5] Add Prometheus metrics endpoint to all microservices in phase-5/microservices/*/src/metrics.py
- [ ] T119 [P] [US5] Create Prometheus configuration in phase-5/monitoring/prometheus.yaml
- [ ] T120 [P] [US5] Create Grafana dashboards in phase-5/monitoring/grafana-dashboards/
- [ ] T121 [P] [US5] Deploy Prometheus and Grafana via Helm in phase-5/helm/todo-app/charts/monitoring/

#### Kubernetes Resource Limits

- [ ] T122 [P] [US5] Set resource limits for Frontend Pod in phase-5/k8s/frontend-deployment.yaml
- [ ] T123 [P] [US5] Set resource limits for Backend Pod in phase-5/k8s/backend-deployment.yaml
- [ ] T124 [P] [US5] Set resource limits for all microservices in phase-5/k8s/*-deployment.yaml
- [ ] T125 [P] [US5] Configure liveness and readiness probes for all pods in phase-5/k8s/*-deployment.yaml

**Checkpoint**: Production deployment complete - CI/CD pipeline deploys automatically, monitoring active, all services healthy

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Cross-Service Testing

- [ ] T126 [P] Test Dapr State Management (conversation persistence) in phase-5/tests/integration/test_dapr_state.py
- [ ] T127 [P] Test Kafka event flow (task-events → reminders → notification) in phase-5/tests/integration/test_kafka_events.py
- [ ] T128 [P] Test Dapr Jobs/Scheduler (reminder triggers) in phase-5/tests/integration/test_dapr_jobs.py
- [ ] T129 [P] Test Frontend → Backend service invocation in phase-5/tests/integration/test_service_invocation.py
- [ ] T130 End-to-end flow test (create → event → recurring → reminder → notification → frontend update) in phase-5/tests/e2e/test_full_lifecycle.py

### Documentation & Operations

- [ ] T131 [P] Create architecture documentation in phase-5/docs/architecture.md
- [ ] T132 [P] Create deployment guide in phase-5/docs/deployment.md
- [ ] T133 [P] Create operations runbook in phase-5/docs/operations.md
- [ ] T134 [P] Update quickstart.md with actual values from phase-5/quickstart.md
- [ ] T135 Validate quickstart.md instructions work end-to-end

### Security Hardening

- [ ] T136 Verify no hardcoded secrets in phase-5/ codebase
- [ ] T137 Verify all secrets use Dapr Secrets or Kubernetes Secrets
- [ ] T138 Verify TLS/mTLS for inter-service communication
- [ ] T139 Verify input validation and sanitization on all endpoints

### Performance Optimization

- [ ] T140 Verify API p95 latency < 500ms in phase-5/tests/performance/test_api_latency.py
- [ ] T141 Verify real-time updates < 2 seconds in phase-5/tests/performance/test_realtime_latency.py
- [ ] T142 Verify 100 req/sec throughput in phase-5/tests/performance/test_throughput.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Task Management - P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (Reminders - P2)**: Can start after Foundational - Independent of US1
- **US3 (Recurring Tasks - P3)**: Can start after Foundational - Independent of US1/US2
- **US4 (Real-Time Sync - P2)**: Can start after Foundational - Depends on US1 (needs task events)
- **US5 (Cloud Deployment - P1)**: Can start after Foundational - Independent (infrastructure)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: All [P] tasks (T002, T003, T004, T005, T006, T007) can run in parallel
- **Foundational Phase**: All [P] tasks (T009-T012, T015-T016, T017-T020) can run in parallel
- **US1 Phase**: All [P] tests (T021-T027) can run in parallel, then all [P] agents (T028-T036), then orchestrator implementation
- **US2 Phase**: [P] tasks (T054-T057, T060-T063) can run in parallel
- **US3 Phase**: [P] tasks (T068-T074, T075-T078) can run in parallel
- **Across Stories**: Once Foundational is done, US1, US2, US3, US5 can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first, ensure they FAIL):
Task T021: "Contract test for POST /tasks in phase-5/tests/contract/test_tasks_api.py"
Task T022: "Contract test for PATCH /tasks/{id} in phase-5/tests/contract/test_tasks_api.py"
Task T023: "Contract test for POST /tasks/{id}/complete in phase-5/tests/contract/test_tasks_api.py"
Task T024: "Contract test for DELETE /tasks/{id} in phase-5/tests/contract/test_tasks_api.py"
Task T025: "Contract test for POST /chat/command in phase-5/tests/contract/test_chat_api.py"
Task T026: "Integration test for chatbot task creation in phase-5/tests/integration/test_task_creation.py"
Task T027: "Integration test for chatbot task completion in phase-5/tests/integration/test_task_completion.py"

# Launch all skill agents in parallel:
Task T028: "Create Task Agent skill in phase-5/agents/skills/task_agent.py"
Task T029: "Create Task Agent prompt in phase-5/agents/skills/prompts/task_prompt.txt"
Task T031: "Create Reminder Agent skill in phase-5/agents/skills/reminder_agent.py"
Task T032: "Create Reminder Agent prompt in phase-5/agents/skills/prompts/reminder_prompt.txt"

# Launch all system prompts in parallel:
Task T034: "Create global behavior prompt in phase-5/system_prompts/global_behavior.txt"
Task T035: "Create clarification logic prompt in phase-5/system_prompts/clarification_logic.txt"
Task T036: "Create error handling prompt in phase-5/system_prompts/error_handling.txt"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 5 Only)

**Minimum Viable Product**: Core task management via AI chatbot + production deployment

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T020) - CRITICAL
3. Complete Phase 3: User Story 1 - Task Management with AI Assistant (T021-T053)
4. Complete Phase 7: User Story 5 - Production Cloud Deployment (T093-T125)
5. **STOP and VALIDATE**: Test task creation via chatbot, verify cloud deployment works
6. Deploy/demo if ready

**MVP delivers**: AI-powered task management working in production cloud environment

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T020)
2. Add US1 (Task Management) → Test independently → Deploy (MVP!)
3. Add US2 (Reminders) → Test independently → Deploy
4. Add US3 (Recurring Tasks) → Test independently → Deploy
5. Add US4 (Real-Time Sync) → Test independently → Deploy
6. Polish (Phase 8) → Production hardening → Deploy

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers (after Foundational phase):

1. Team completes Setup + Foundational together (T001-T020)
2. Once Foundational is done:
   - **Developer A**: US1 Task Management (T021-T053)
   - **Developer B**: US2 Reminders + US3 Recurring (T054-T083)
   - **Developer C**: US5 Cloud Deployment + US4 Real-Time Sync (T084-T125)
3. Stories complete and integrate independently

---

## Notes

- **[P] tasks** = different files, no dependencies, safe to parallelize
- **[Story] label** = maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence
- **User-provided tasks** (T501-T515 from input) are integrated into appropriate user story phases

---

**Task Count Summary**:
- Total Tasks: 142
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 13 tasks (BLOCKS all user stories)
- Phase 3 (US1 - Task Management): 27 tasks (P1 - MVP Core)
- Phase 4 (US2 - Reminders): 14 tasks (P2)
- Phase 5 (US3 - Recurring): 16 tasks (P3)
- Phase 6 (US4 - Real-Time Sync): 7 tasks (P2)
- Phase 7 (US5 - Cloud Deployment): 33 tasks (P1 - MVP Infrastructure)
- Phase 8 (Polish): 25 tasks

**Parallel Opportunities**: 78 tasks marked [P] can run in parallel (55% of all tasks)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 7 (US5) = 120 tasks for full production deployment with AI task management

**Suggested Fast-Track MVP**: Setup (T001-T007) + Foundational (T008-T020) + US1 Core (T028-T053, skip tests for speed) = 52 tasks for basic AI task management
