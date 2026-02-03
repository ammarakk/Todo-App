# Implementation Plan: Phase 5 - Advanced Cloud Deployment & Agentic Integration

**Branch**: `007-advanced-cloud-deployment` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-advanced-cloud-deployment/spec.md`

## Summary

Phase 5 transforms the Phase IV todo application into a **production-ready, event-driven AI system** with reusable skill agents, microservices architecture, and cloud-native deployment. The system upgrades from direct CRUD to an AI-orchestrated backend using Dapr + Kafka for event-driven communication, implements four reusable AI skill agents (Task, Reminder, Recurring, Audit), and deploys via automated CI/CD to Kubernetes with production reliability standards.

**Technical Approach**:
- **Frontend**: Next.js (Phase IV copy, read-only) with Dapr sidecar for service invocation
- **Backend**: FastAPI with AI orchestrator pattern, MCP tool integration, and event publishing
- **AI Agents**: Four reusable skill agents with dedicated prompts and structured JSON outputs
- **Event Bus**: Kafka (Redpanda for dev) with Dapr Pub/Sub abstraction
- **Microservices**: Notification, Recurring Task, and Audit services consuming Kafka events
- **State**: PostgreSQL/Neon via Dapr State Management
- **Deployment**: Kubernetes (Minikube local, AKS/GKE/DO cloud) with Helm charts
- **CI/CD**: GitHub Actions pipeline with automated build, test, scan, deploy, verify stages

## Technical Context

**Language/Version**:
- Frontend: Node.js 18+ (Next.js from Phase IV, read-only)
- Backend: Python 3.11+ (FastAPI from Phase IV + orchestrator enhancements)
- Microservices: Python 3.11+ (FastAPI)
- AI Runtime: Ollama for local inference (from Phase IV)

**Primary Dependencies**:
- **Dapr 1.12+**: Pub/Sub, State Management, Secrets, Service Invocation
- **Kafka 3.x+** / Redpanda: Event bus for task-events, reminders, task-updates
- **PostgreSQL 14+** / Neon: Task storage, conversation state, audit logs
- **FastAPI**: Backend and microservices framework
- **Next.js**: Frontend framework (Phase IV, unchanged)
- **Ollama**: Local LLM runtime for chatbot
- **Prometheus**: Metrics collection
- **Kubernetes 1.25+**: Container orchestration
- **Helm 3.x+**: Package management

**Storage**:
- **PostgreSQL/Neon**: Primary database for tasks, conversations, reminders, audit logs
- **Dapr State Store**: Conversation state caching, user preferences
- **Kafka Topics**: Event streaming (task-events, reminders, task-updates, audit-events)

**Testing**:
- **pytest**: Python unit and integration tests
- **Jest**: Frontend component tests (from Phase IV)
- **Contract Tests**: API contract validation
- **End-to-End Tests**: Full workflow automation

**Target Platform**:
- **Local Development**: Minikube with port-forwarding
- **Cloud Production**: AKS/GKE/DigitalOcean Kubernetes with managed Kafka

**Project Type**: Microservices web application (event-driven)

**Performance Goals**:
- Task creation: < 30s end-to-end (user perspective)
- API response time: p95 < 500ms for all endpoints
- Throughput: 100 task creation requests per second
- Real-time updates: < 2 seconds across all clients
- Reminder delivery: 95% within 10 seconds of scheduled time
- CI/CD pipeline: < 10 minutes from commit to deployment

**Constraints**:
- No hardcoded secrets (use Dapr Secrets or Kubernetes Secrets)
- All inter-service communication via Dapr (no direct HTTP calls)
- Event-driven microservices only (no synchronous cross-service calls)
- Phase IV frontend code remains read-only (no modifications)
- Phase IV backend CRUD logic preserved (only add orchestrator)
- All AI skills must be reusable (no hardcoded business logic)
- At-least-once message delivery with idempotent operations

**Scale/Scope**:
- Users: 500 concurrent users (SC-009)
- Services: 6 pods (frontend, backend, chatbot, notification, recurring, audit)
- Kafka Topics: 4 topics (task-events, reminders, task-updates, audit-events)
- Skill Agents: 4 reusable agents (Task, Reminder, Recurring, Audit)
- System Prompts: 3 global prompts (behavior, clarification, error handling)
- Uptime: 99.5% over 30 days (SC-007)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Phase V Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **XII. Skills & Agents Architecture** | ✅ PASS | Four skill agents planned (Task, Reminder, Recurring, Audit) with dedicated prompts in `/agents/skills/prompts/` and structured JSON outputs |
| **XIII. System Prompts Layer** | ✅ PASS | Global prompts planned in `/system_prompts/` for behavior control, clarification logic, and error handling |
| **XIV. Backend as AI Orchestrator** | ✅ PASS | Backend implements orchestrator flow: receive → load prompt → detect intent → call skill → validate → execute → publish event → return |
| **XV. Event-Driven Microservices** | ✅ PASS | Three microservices (Notification, Recurring, Audit) consuming Kafka events via Dapr Pub/Sub |
| **XVI. Dapr Integration** | ✅ PASS | Dapr used for Pub/Sub, State Management, Secrets, and Service Invocation throughout |
| **XVII. CI/CD Automation** | ✅ PASS | GitHub Actions pipeline with 7 stages (code → test → build → scan → push → deploy → verify) |
| **XVIII. Production Reliability** | ✅ PASS | Health/ready endpoints, resource limits, structured JSON logs, correlation IDs, retry logic, circuit breakers |

### Phase III & IV Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. AI-Native Interaction** | ✅ PASS | Chatbot remains primary interface, now with skill agents for better intent understanding |
| **II. Stateless Server Architecture** | ✅ PASS | Backend remains stateless; conversation state persisted in PostgreSQL via Dapr State |
| **III. Persistence of Intelligence** | ✅ PASS | All conversations stored in Conversation and Message tables (from Phase III) |
| **IV. Strict Security & User Isolation** | ✅ PASS | JWT auth from Phase II maintained; user_id filters in all queries |
| **V. Multi-Language Support** | ✅ PASS | English and Urdu support preserved (from Phase III) |
| **VI. MCP-First Tool Design** | ✅ PASS | All task operations via MCP tools (from Phase III) |
| **VII. Immutable Phase III Logic** | ✅ PASS | Phase IV/III business logic unchanged; only adding orchestrator and microservices |
| **VIII. Spec-Driven Infrastructure** | ✅ PASS | All Docker, Kubernetes, Helm generated via spec-driven workflow |
| **IX. Ollama-First LLM Runtime** | ✅ PASS | Ollama used for local inference (from Phase IV) |
| **X. Kubernetes-Native Deployment** | ✅ PASS | Deployed to Kubernetes with Helm charts (from Phase IV) |
| **XI. AI-Powered DevOps Automation** | ✅ PASS | kubectl-ai, kagent, Gordon used for operational tasks |

**GATE STATUS**: ✅ **ALL PASS** - No constitution violations. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/007-advanced-cloud-deployment/
├── spec.md              # Feature specification (/sp.specify output)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entity schemas)
├── quickstart.md        # Phase 1 output (dev setup guide)
├── contracts/           # Phase 1 output (API/event schemas)
│   ├── backend-api.yaml # OpenAPI specification
│   ├── kafka-events.yaml # Kafka event schemas
│   └── dapr-components.yaml # Dapr component configs
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase-5/
├── frontend/              # Phase IV copy (READ-ONLY - no modifications)
│   ├── src/
│   │   ├── app/           # Next.js app pages
│   │   ├── components/    # React components
│   │   └── services/      # API clients
│   ├── Dockerfile         # Container definition
│   └── helm/              # Helm chart
│
├── backend/               # Phase IV copy + AI orchestrator logic
│   ├── src/
│   │   ├── models/        # SQLAlchemy models (from Phase IV)
│   │   ├── services/      # Business logic (from Phase IV)
│   │   ├── api/           # FastAPI endpoints (from Phase IV)
│   │   ├── orchestrator/  # NEW: AI orchestrator flow
│   │   │   ├── intent_detector.py # Detect user intent
│   │   │   ├── skill_dispatcher.py # Call appropriate skill
│   │   │   └── event_publisher.py # Publish Kafka events
│   │   └── mcp_tools/     # MCP tool integrations (from Phase IV)
│   ├── tests/
│   │   ├── unit/          # Orchestrator unit tests
│   │   ├── integration/   # End-to-end workflow tests
│   │   └── contract/      # API contract tests
│   ├── Dockerfile
│   └── helm/
│
├── chatbot/               # NEW: Chatbot service with MCP agents
│   ├── src/
│   │   ├── agents/        # MCP agent integrations
│   │   └── api/           # Chat endpoints
│   ├── Dockerfile
│   └── helm/
│
├── agents/                # NEW: Reusable AI skill modules
│   ├── skills/
│   │   ├── task_agent.py           # Extract task data from text
│   │   ├── reminder_agent.py       # Extract time/date from text
│   │   ├── recurring_agent.py      # Calculate next occurrence
│   │   └── audit_agent.py          # Log system actions
│   └── prompts/                     # Skill-specific prompts
│       ├── task_prompt.txt
│       ├── reminder_prompt.txt
│       ├── recurring_prompt.txt
│       └── audit_prompt.txt
│
├── system_prompts/        # NEW: Global behavior control
│   ├── global_behavior.txt       # Overall AI personality
│   ├── clarification_logic.txt   # How to ask for missing info
│   └── error_handling.txt        # How to present errors
│
├── microservices/         # NEW: Event-driven services
│   ├── notification/       # Reminder notification service
│   │   ├── src/
│   │   │   ├── consumers.py # Subscribe to reminders topic
│   │   │   ├── email_service.py # Send email notifications
│   │   │   └── push_service.py  # Send push notifications (optional)
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── helm/
│   │
│   ├── recurring/          # Auto-generate recurring tasks
│   │   ├── src/
│   │   │   ├── consumers.py # Subscribe to task.completed events
│   │   │   ├── recurrence_calculator.py # Calculate next date
│   │   │   └── task_generator.py # Create next instance
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── helm/
│   │
│   └── audit/              # Audit logging service
│       ├── src/
│       │   ├── consumers.py # Subscribe to all events
│       │   └── audit_logger.py # Log to audit database
│       ├── tests/
│       ├── Dockerfile
│       └── helm/
│
├── kafka/                 # NEW: Kafka configuration
│   ├── docker-compose.yml # Local Redpanda setup
│   ├── topics.yaml        # Topic definitions
│   └── producers/         # Kafka producer utilities
│
├── dapr/                  # NEW: Dapr components and configuration
│   ├── components/
│   │   ├── pubsub.yaml    # Kafka Pub/Sub component
│   │   ├── statestore.yaml # PostgreSQL state component
│   │   ├── secrets.yaml   # Kubernetes secret store
│   │   └── jobs.yaml      # Dapr Jobs scheduler (optional)
│   └── configuration/
│       ├── config.yaml    # Dapr configuration
│       └── metrics.yaml   # Prometheus metrics config
│
├── helm/                  # NEW: Helm charts for full stack
│   ├── todo-app/          # Parent chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml    # Environment-specific configs
│   │   └── charts/        # Sub-charts
│   │       ├── frontend/
│   │       ├── backend/
│   │       ├── chatbot/
│   │       ├── notification/
│   │       ├── recurring/
│   │       └── audit/
│   └── overlays/          # Kustomize overlays for environments
│       ├── local/
│       └── production/
│
├── tests/                 # NEW: Comprehensive test suite
│   ├── unit/              # Skill agent unit tests
│   ├── integration/       # End-to-end workflow tests
│   ├── contract/          # API contract tests
│   └── performance/       # Load testing scripts
│
└── docs/                  # NEW: Phase V documentation
    ├── architecture.md    # System architecture diagrams
    ├── deployment.md      # Deployment guide
    └── operations.md      # Runbook for common tasks
```

**Structure Decision**: Selected Option 2 (Web Application) with microservices extension. The `phase-5/` directory contains the full application stack, with clear separation between frontend (read-only Phase IV copy), backend (Phase IV + orchestrator), chatbot, agents, system prompts, and event-driven microservices. This structure aligns with Phase V constitution requirements for reusable skill agents, global system prompts, and decoupled microservices.

## Complexity Tracking

> **No violations** - All constitution principles satisfied. This section intentionally left empty.

## Architecture Overview

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Frontend Pod │  │ Backend Pod  │  │ Chatbot Pod  │         │
│  │ Next.js      │  │ FastAPI      │  │ FastAPI      │         │
│  │ + Dapr Sidecar│  │ + Dapr Sidecar│ │ + Dapr Sidecar│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         │ Service Inv.     │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Dapr Sidecar Interactions                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Notification  │  │  Recurring   │  │    Audit     │         │
│  │    Pod       │  │    Pod       │  │    Pod       │         │
│  │ + Dapr       │  │ + Dapr       │  │ + Dapr       │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Dapr Pub/Sub                         │   │
│  │                   (Kafka Cluster)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Dapr State Store                        │   │
│  │              (PostgreSQL / Neon)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Service Communication Flow

```
User → Frontend → Backend Orchestrator → Skill Agents → MCP Tools → Database
           ↓              ↓                         ↓
      WebSocket      Publish Events            Conversation State
           ↓              ↓                         ↓
    Real-time UI    Kafka Topics              Dapr State Store
                          ↓
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
    Notification   Recurring Task    Audit Service
     Service         Service
          ↓               ↓               ↓
    Email/Push    Next Task         Audit Log
```

### Data Flow: Task Creation via Chatbot

1. **User Input**: User types "Create a task to buy milk tomorrow at 5pm" in frontend chat
2. **Frontend**: Sends message to backend via Dapr Service Invocation
3. **Backend Orchestrator**:
   - Loads system prompt from `/system_prompts/global_behavior.txt`
   - Detects intent: "create_task"
   - Calls Task Agent skill with user message
4. **Task Agent**: Loads prompt from `/agents/skills/prompts/task_prompt.txt`, extracts structured JSON:
   ```json
   {
     "title": "buy milk",
     "due_date": "2026-02-05T17:00:00Z",
     "priority": "medium",
     "confidence": 0.95
   }
   ```
5. **Backend**: Validates JSON, calls MCP tool to create task in database
6. **Backend**: Publishes `task.created` event to Kafka via Dapr Pub/Sub
7. **Recurring Service**: Ignores event (not a recurring task)
8. **Notification Service**: Ignores event (no reminder set yet)
9. **Audit Service**: Logs event to audit database
10. **Backend**: Returns success response to frontend
11. **Frontend**: Updates UI in real-time via WebSocket subscription to task-updates

## Component Breakdown

### Frontend Pod (Phase IV - Read-Only)

**Responsibilities**:
- Display task list with filters (tags, priority, due date)
- Provide chat interface for AI interactions
- Real-time updates via WebSocket connection
- Service Invocation to Backend Pod via Dapr

**Interactions**:
- **User**: Receives user interactions (chat input, task actions)
- **Backend Pod**: Calls via Dapr Service Invocation (`POST /tasks`, `GET /tasks`, `POST /chat/command`)
- **WebSocket**: Subscribes to task-updates via Dapr Pub/Sub for real-time sync

**Tech Stack**:
- Next.js 14 (from Phase IV, no modifications)
- Dapr Sidecar for service invocation and pub/sub
- React components for UI

**Health Endpoints**:
- `/health`: Liveness probe (returns 200 if service running)
- `/ready`: Readiness probe (returns 200 if can reach backend via Dapr)

### Backend Pod (Phase IV + AI Orchestrator)

**Responsibilities**:
- Task CRUD API (from Phase IV, unchanged)
- AI orchestrator flow (NEW):
  1. Receive message from frontend/chatbot
  2. Load system prompt from `/system_prompts/`
  3. Detect intent (create_task, update_task, complete_task, delete_task, query_tasks)
  4. Call appropriate skill agent via Task/Reminder/Recurring/Audit agents
  5. Validate skill output (structured JSON)
  6. Execute business logic via MCP tools
  7. Publish event to Kafka via Dapr Pub/Sub
  8. Return response to user

**Interactions**:
- **Frontend/Chatbot**: Receives requests via Dapr Service Invocation
- **Dapr State Store**: Saves/loads conversation state
- **Skill Agents**: Calls agents in `/agents/skills/` for intent extraction
- **MCP Tools**: Executes task operations via MCP tools (from Phase III)
- **Kafka**: Publishes events to task-events, reminders topics

**Tech Stack**:
- FastAPI (from Phase IV)
- Dapr Sidecar for pub/sub, state, secrets
- Ollama client for LLM inference (from Phase IV)
- MCP SDK for tool integrations (from Phase III)

**Health Endpoints**:
- `/health`: Liveness probe
- `/ready`: Readiness probe (checks DB, Dapr, Ollama connectivity)

### Chatbot Pod (NEW)

**Responsibilities**:
- Handle chat requests from frontend
- Integrate with MCP agents (Claude Code, Gemini, etc.)
- Generate commands for tasks based on user intent
- Store conversation state via Dapr State

**Interactions**:
- **Frontend**: Receives chat messages via Dapr Service Invocation
- **Backend Orchestrator**: Forwards processed intents for execution
- **Dapr State Store**: Manages conversation history and context
- **MCP Agents**: Calls external AI agents for complex reasoning

**Tech Stack**:
- FastAPI
- Dapr Sidecar
- MCP Agent SDK

**Health Endpoints**:
- `/health`: Liveness probe
- `/ready`: Readiness probe (checks Dapr, MCP agent connectivity)

### Notification Pod (NEW)

**Responsibilities**:
- Subscribe to `reminders` Kafka topic via Dapr Pub/Sub
- Send email notifications when reminders trigger
- Retry failed deliveries up to 3 times with exponential backoff
- Log delivery results to audit-events topic

**Interactions**:
- **Kafka**: Consumes from `reminders` topic
- **Email Service**: Sends notifications via SendGrid/AWS SES/Mailgun
- **Dapr Secrets**: Fetches email API keys

**Tech Stack**:
- FastAPI
- Dapr Sidecar (Kafka consumer)
- Email client (SendGrid/AWS SES)

**Health Endpoints**:
- `/health`: Liveness probe
- `/ready`: Readiness probe (checks Kafka connectivity, email service)

### Recurring Task Pod (NEW)

**Responsibilities**:
- Subscribe to `task-events` Kafka topic (filter for `task.completed`)
- When a recurring task is completed, calculate next occurrence
- Create next task instance via Backend API
- Set reminder for new task if original had reminder
- Log generation to audit-events topic

**Interactions**:
- **Kafka**: Consumes from `task-events` topic
- **Backend API**: Creates next task via Dapr Service Invocation
- **Recurring Agent**: Calls skill agent to calculate next date

**Tech Stack**:
- FastAPI
- Dapr Sidecar (Kafka consumer)
- Date calculation library (dateutil/pendulum)

**Health Endpoints**:
- `/health`: Liveness probe
- `/ready`: Readiness probe (checks Kafka connectivity, backend API)

### Audit Pod (NEW)

**Responsibilities**:
- Subscribe to all Kafka topics (task-events, reminders, task-updates)
- Log all events to audit database
- Maintain immutable audit trail
- Provide audit query API

**Interactions**:
- **Kafka**: Consumes from all topics
- **Audit Database**: Writes audit records (PostgreSQL separate schema)

**Tech Stack**:
- FastAPI
- Dapr Sidecar (Kafka consumer)

**Health Endpoints**:
- `/health`: Liveness probe
- `/ready`: Readiness probe (checks Kafka connectivity, audit DB)

## Service Boundaries

### Inter-Service Communication Rules

1. **Frontend → Backend**: Dapr Service Invocation only (no direct REST)
   - Frontend calls `http://localhost:3500/v1.0/invoke/backend-app/method/tasks`
   - Dapr sidecar handles retries, timeouts, service discovery

2. **Backend → Chatbot**: Dapr Service Invocation only
   - Backend calls `http://localhost:3500/v1.0/invoke/chatbot-app/method/chat/process`

3. **Backend/Chatbot → Kafka**: Dapr Pub/Sub only (no direct Kafka client)
   - Publish via `http://localhost:3500/v1.0/publish/pubsub/task-events`
   - Dapr handles serialization, retries, dead-letter queues

4. **Microservices → Kafka**: Dapr Pub/Sub subscriptions only
   - Subscribe via HTTP endpoint (Dapr pushes to service)
   - No direct Kafka consumer groups

5. **All Services → Database**: Direct connections allowed (same trusted network)
   - Use connection pooling (SQLAlchemy)
   - Encrypt with TLS (cloud deployments)

6. **All Services → Secrets**: Dapr Secret Store only
   - Fetch via `http://localhost:3500/v1.0/secrets/kubernetes-secrets/secret-name`
   - No hardcoded secrets in code or config files

### Synchronous vs. Asynchronous Boundaries

| Operation | Pattern | Rationale |
|-----------|---------|-----------|
| User creates task | Sync (Frontend → Backend) | User needs immediate confirmation |
| Task created event | Async (Backend → Kafka) | Microservices process independently |
| Reminder delivery | Async (Kafka → Notification) | Don't block task creation on email send |
| Recurring task generation | Async (Kafka → Recurring) | Background processing, no user impact |
| Real-time updates | Async (Kafka → Frontend WebSocket) | Broadcast to all clients without blocking |
| Audit logging | Async (Kafka → Audit) | Don't block main flow on audit writes |

## Deployment Strategy

### Local Development (Minikube)

**Prerequisites**:
- Minikube installed and running (`minikube start`)
- kubectl configured to use Minikube
- Dapr CLI installed (`dapr init`)
- Helm 3.x installed

**Setup Steps**:

1. **Start Local Kafka (Redpanda)**:
   ```bash
   cd phase-5/kafka
   docker-compose up -d
   ```

2. **Install Dapr in Minikube**:
   ```bash
   dapr init --runtime-version 1.12 --helm-chart
   ```

3. **Deploy Application**:
   ```bash
   cd phase-5/helm/todo-app
   helm install todo-app . --values values-local.yaml
   ```

4. **Port-Forward Services**:
   ```bash
   kubectl port-forward svc/frontend 3000:3000
   kubectl port-forward svc/backend 8000:8000
   ```

5. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Dapr Dashboard: http://localhost:8080

**Validation**:
- ✅ All pods running (`kubectl get pods`)
- ✅ Frontend loads in browser
- ✅ Can create task via chatbot
- ✅ Task appears in list
- ✅ Kafka events visible in Redpanda console

### Cloud Deployment (AKS/GKE/DigitalOcean)

**Prerequisites**:
- Kubernetes cluster created (AKS/GKE/DO)
- kubectl configured for cloud cluster
- Container registry access (Docker Hub/GHCR)
- Domain name and TLS certificates configured
- Managed Kafka service (Redpanda Cloud/Confluent/MSK)
- Cloud PostgreSQL (Neon/RDS/Cloud SQL)

**Setup Steps**:

1. **Configure Cloud Secrets**:
   ```bash
   kubectl create secret generic db-credentials \
     --from-literal=username=<user> \
     --from-literal=password=<pass> \
     --from-literal=host=<neon-db-host>

   kubectl create secret generic email-credentials \
     --from-literal=api-key=<sendgrid-api-key>

   kubectl create secret generic ollama-url \
     --from-literal=url=<ollama-service-url>
   ```

2. **Install Dapr in Cloud Cluster**:
   ```bash
   dapr init --runtime-version 1.12 --helm-chart --install
   ```

3. **Deploy Kafka**:
   - Option A: Redpanda Cloud (recommended for simplicity)
   - Option B: Strimzi Kafka Operator on Kubernetes
   - Option C: Confluent Cloud (managed service)

4. **Deploy Application**:
   ```bash
   cd phase-5/helm/todo-app
   helm install todo-app . --values values-production.yaml
   ```

5. **Configure DNS**:
   - Create A records for frontend domain pointing to frontend load balancer
   - Create A records for backend domain pointing to backend load balancer

6. **Verify Deployment**:
   ```bash
   kubectl get pods -w
   kubectl get services
   helm status todo-app
   ```

**CI/CD Pipeline** (GitHub Actions):

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Tests
        run: |
          cd phase-5
          pytest tests/

      - name: Build Docker Images
        run: |
          docker build -t myreg/frontend:${{ github.sha }} phase-5/frontend
          docker build -t myreg/backend:${{ github.sha }} phase-5/backend
          # ... build all services

      - name: Push to Registry
        run: |
          docker push myreg/frontend:${{ github.sha }}
          # ... push all images

      - name: Security Scan
        run: |
          trivy image myreg/frontend:${{ github.sha }}

      - name: Deploy via Helm
        run: |
          helm upgrade todo-app phase-5/helm/todo-app \
            --install \
            --set image.tag=${{ github.sha }} \
            --values values-production.yaml

      - name: Smoke Tests
        run: |
          ./tests/smoke.sh https://todo-app.example.com
  ```

### Environment Parity

| Component | Local | Cloud | Notes |
|-----------|-------|-------|-------|
| Frontend | Minikube NodePort | LoadBalancer + DNS | Same container image |
| Backend | Minikube NodePort | LoadBalancer + DNS | Same container image |
| Kafka | Docker Compose Redpanda | Redpanda Cloud/Strimzi | Same topic schemas |
| PostgreSQL | Docker Compose | Neon/RDS | Same schema |
| Dapr | Local mode | Kubernetes mode | Same component configs |
| Secrets | Kubernetes Secrets | Kubernetes Secrets | Same secret names |

**Key Principle**: Local and cloud deployments use **identical container images** and **Helm charts**. Only `values.yaml` differs (resource limits, replicas, URLs).

## Technology Decisions

### Why Dapr?

**Decision**: Use Dapr 1.12+ for all cross-service communication.

**Rationale**:
- **Vendor neutrality**: Easy migration from local (Docker Compose) to cloud (Kubernetes)
- **Abstraction**: No hardcoded Kafka, Redis, or gRPC dependencies
- **Best practices**: Built-in retries, circuit breakers, observability
- **Judge appeal**: Demonstrates "production-grade" cloud-native architecture

**Alternatives Considered**:
- **Direct Kafka**: Rejected due to vendor lock-in and complex error handling
- **AWS SDK**: Rejected due to AWS lock-in
- **gRPC**: Rejected due to lack of pub/sub abstraction

### Why Kafka (not Redis)?

**Decision**: Use Kafka 3.x+ (Redpanda for dev) as event bus.

**Rationale**:
- **Event sourcing**: Immutable log of all events (required for audit)
- **Replay capability**: Can replay events for debugging/testing
- **Scalability**: Handles high throughput (100 req/sec requirement)
- **Microservices standard**: Industry standard for event-driven architecture

**Alternatives Considered**:
- **Redis Streams**: Rejected due to limited replay and retention
- **RabbitMQ**: Rejected due to complex setup and lack of replay
- **AWS SQS**: Rejected due to AWS lock-in

### Why Microservices (not Monolith)?

**Decision**: Split into 6 services (frontend, backend, chatbot, notification, recurring, audit).

**Rationale**:
- **Independent scaling**: Notification service can scale independently of backend
- **Fault isolation**: Crash in notification service doesn't affect task creation
- **Technology flexibility**: Could use different languages for different services (future)
- **Judge appeal**: Demonstrates microservices architecture

**Alternatives Considered**:
- **Monolithic backend**: Rejected due to tight coupling and scaling limits
- **Modular monolith**: Rejected due to lack of independent deployment

### Why Skill Agents (not Hardcoded Chatbot)?

**Decision**: Implement 4 reusable skill agents with dedicated prompts.

**Rationale**:
- **Reusability**: Skills can be copied to future hackathon projects
- **Testability**: Each skill can be unit tested independently
- **Maintainability**: Changes to one skill don't break others
- **Judge appeal**: Demonstrates professional AI engineering

**Alternatives Considered**:
- **Hardcoded chatbot logic**: Rejected due to unmaintainability
- **Single monolithic agent**: Rejected due to complexity and lack of reusability

## Implementation Phases

This plan defines **HOW** the system will be implemented. The next step (`/sp.tasks`) will break this down into **actionable tasks** with dependencies and test cases.

**Phase 0: Research & Technology Decisions** → Generates `research.md`
- [ ] Research Dapr Pub/Sub best practices for Kafka integration
- [ ] Research skill agent design patterns for reusable AI modules
- [ ] Research event-driven microservices testing strategies
- [ ] Evaluate Redpanda vs Kafka for local development
- [ ] Document all decisions in research.md

**Phase 1: Design & Contracts** → Generates `data-model.md`, `contracts/`, `quickstart.md`
- [ ] Extract entities from spec and define schemas (data-model.md)
- [ ] Design API contracts (OpenAPI spec)
- [ ] Design Kafka event schemas (task-events, reminders, task-updates, audit-events)
- [ ] Design Dapr component configurations (pubsub, statestore, secrets)
- [ ] Write quickstart guide for developers

**Phase 2: Task Breakdown** → Generates `tasks.md` (via `/sp.tasks` command)
- [ ] Break down into actionable tasks with dependencies
- [ ] Assign tasks to phases (infrastructure, agents, microservices, testing)
- [ ] Define test cases for each task
- [ ] Estimate complexity and dependencies

**Phase 3-8: Implementation** → Executed via `/sp.implement` command (NOT planned here)

## Next Steps

1. **Execute Phase 0**: Generate `research.md` by researching technology decisions
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Run `/sp.tasks`**: Break down implementation into actionable tasks
4. **Run `/sp.implement`**: Execute tasks and build the system

---

**Plan Status**: ✅ Complete - Ready for Phase 0 research and Phase 1 design generation
