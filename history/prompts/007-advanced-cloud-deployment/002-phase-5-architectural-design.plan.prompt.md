---
id: 002
title: Phase 5 architectural design
stage: plan
date: 2026-02-04
surface: agent
model: claude-sonnet-4-5
feature: 007-advanced-cloud-deployment
branch: 007-advanced-cloud-deployment
user: User
command: /sp.plan
labels: ["phase-5","architecture","dapr","kafka","microservices"]
links:
  spec: specs/007-advanced-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-advanced-cloud-deployment/plan.md
  - specs/007-advanced-cloud-deployment/research.md
  - specs/007-advanced-cloud-deployment/data-model.md
  - specs/007-advanced-cloud-deployment/contracts/backend-api.yaml
  - specs/007-advanced-cloud-deployment/contracts/kafka-events.yaml
  - specs/007-advanced-cloud-deployment/contracts/dapr-components.yaml
  - specs/007-advanced-cloud-deployment/quickstart.md
tests:
  - Constitution compliance check (PASS - all 18 principles satisfied)
  - Research validation (PASS - all technology decisions documented)
  - Data model completeness (PASS - 7 entities with relationships and indexes)
  - API contracts validation (PASS - OpenAPI spec with all endpoints)
  - Event schemas validation (PASS - 4 topics with event envelopes)
---

## Prompt

Perfect. Now we'll create Phase 5 /sp.plan. This will be fully aligned with /sp.constitution and /sp.specify, detailing architecture, components, APIs, Dapr/Kafka interactions, service boundaries, and deployment plan. Every agent will have a clear roadmap to break tasks and implement Phase 5.


---

/sp.plan – Phase 5 (Advanced Cloud Deployment & Agentic Integration)

1. Purpose

Phase 5 Plan defines HOW the system will be implemented. This includes architecture diagrams, service breakdown, API contracts, Kafka/Dapr integration, and deployment strategies. It builds upon Phase 4, upgrading it to cloud-ready, agent-driven, fully event-based architecture.


---

2. High-Level Architecture

┌─────────────────────────────────────────┐
            │          Kubernetes Cluster             │
            │                                         │
            │  ┌───────────────┐   ┌───────────────┐ │
            │  │ Frontend Pod  │   │ Backend Pod   │ │
            │  │ Next.js + Dapr│   │ FastAPI + Dapr│ │
            │  └─────┬─────────┘   └─────┬─────────┘ │
            │        │                   │           │
            │        ▼                   ▼           │
            │  ┌───────────────┐   ┌───────────────┐ │
            │  │ Chatbot Pod   │   │ Notification  │ │
            │  │ MCP Agents    │   │ Pod + Dapr    │ │
            │  └───────────────┘   └───────────────┘ │
            │          │                   │         │
            │          ▼                   ▼         │
            │   ┌───────────────┐   ┌───────────────┐│
            │   │ Dapr Pub/Sub  │   │ Dapr State    ││
            │   │ Kafka Cluster │   │ PostgreSQL    ││
            │   └───────────────┘   └───────────────┘│
            └─────────────────────────────────────────┘

Frontend Pod – Next.js app with Dapr sidecar. Receives user interactions (chat, task view).

Backend Pod – FastAPI + MCP Tools, exposes REST endpoints via Dapr Service Invocation.

Chatbot Pod – MCP-controlled AI agents (Claude, Gemini, etc.) handle task creation, updates, and queries.

Notification Pod – Sends task reminders, consumes Kafka topics.

Dapr Components – Pub/Sub, State Store, Scheduler, Secrets.

Kafka Cluster – Handles task-events, reminders, task-updates.



---

3. Component Breakdown

Component    Responsibilities    Interactions

Frontend Pod    UI display, task listing, chat interface    Service Invocation → Backend Pod
Backend Pod    Task API, CRUD logic, MCP integration    Publishes to task-events, invokes Dapr state
Chatbot Pod    Handles chat requests, generates commands for tasks    Uses Dapr State, Pub/Sub, Service Invocation
Notification Pod    Listens for reminders, sends notifications    Subscribes to reminders topic
Recurring Task Service    Auto-generates recurring tasks    Subscribes to task-events
Dapr Pub/Sub (Kafka)    Event-driven messaging    Producers/Consumers: Backend, Chatbot, Notif
Dapr State Store (Postgres)    Conversation state, caching, task persistence    Backend, Chatbot
Dapr Jobs Scheduler    Executes reminders at exact times    Notification Pod, Recurring Task Service
Dapr Secrets    Store API keys, DB credentials securely    All pods
CI/CD Pipeline    Build, test, deploy to cloud    GitHub Actions



---

4. Service Boundaries

Frontend → Backend: Service Invocation via Dapr sidecar (no direct REST calls).

Backend → Chatbot: Service Invocation for task commands.

Backend/Chatbot → Kafka: Publish task events, reminders, updates.

Notification → Kafka: Subscribes to reminders, pushes notifications.

Recurring Task Service → Kafka: Consumes completed tasks, creates next instance.



---

5. API & Event Contracts

5.1 Backend REST API (via Dapr Invocation)

Endpoint    Method    Request    Response

/tasks    POST    {title, description, due_date, priority}    task_id, status
/tasks/{id}    PATCH    {title?, description?, due_date?, priority?}    Updated task object
/tasks/{id}/complete    POST    {}    Completed task object
/tasks/{id}    DELETE    {}    Status
/tasks    GET    {filter?, sort?, tags?}    List of tasks
/chat/command    POST    {user_input, conversation_id}    Agent response


5.2 Kafka Topics

Topic    Producer    Consumer    Schema Example

task-events    Backend/Chatbot    Recurring Task, Audit    {event_type, task_id, user_id, timestamp}
reminders    Backend    Notification Service    {task_id, user_id, due_at, remind_at}
task-updates    Backend    Frontend WebSocket Service    {task_id, field_changed, new_value}



---

6. Dapr Component Configuration

Pub/Sub


apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "todo-service"

State Store


apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=neon.db user=XXX password=XXX dbname=todo"

Jobs (Scheduler)


apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: dapr-jobs
spec:
  type: jobs.cron
  version: v1

Secrets


apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1


---

7. Deployment Strategy

7.1 Local (Minikube)

Deploy all pods with Dapr sidecars.

Run Kafka (Redpanda Docker) in cluster.

Validate Pub/Sub events and reminder jobs.

Use port-forwarding for Frontend + Backend APIs.


7.2 Cloud (AKS/GKE/DigitalOcean)

Use Helm charts for Frontend, Backend, Chatbot, Notification Pods.

Deploy Strimzi Kafka cluster or Redpanda Cloud.

Configure Dapr components for cloud state, jobs, secrets.

CI/CD pipeline automatically builds Docker images, pushes to registry, deploys to Kubernetes.

Monitoring via Prometheus/Grafana + Dapr metrics.



---

8. Task Flow Example

1. User creates task via Frontend or Chatbot.


2. Backend validates and persists task via Dapr State.


3. Backend publishes task-events to Kafka.


4. Recurring Task Service consumes task-events → generates next task if needed.


5. Backend schedules reminder via Dapr Jobs → Notification Pod consumes reminders.


6. Frontend WebSocket service broadcasts task-updates to all clients.


7. Chatbot stores conversation state in Dapr State, generating events for multi-client sync.




---

9. Phase 5 Enhancements Over Phase 4

All Phase 4 functionality reused and improved.

Cloud-ready deployment with CI/CD.

Event-driven architecture fully implemented via Dapr + Kafka.

Chatbot integrated with MCP agents (Claude, Gemini).

Reminders, recurring tasks, and audit logs are production-ready.

Security, secrets, monitoring, and scalability enforced.



---

✅ Bottom Line:
This /sp.plan gives agents a complete blueprint for Phase 5: component layout, API contracts, Dapr/Kafka integration, task flows, and deployment strategy. Every task now has a clear traceable HOW, ready for /sp.tasks generation.


---

## Response snapshot

Successfully created Phase 5 implementation plan with complete architectural design, research findings, data model, API/event contracts, and quickstart guide.

**Plan Generated**: `specs/007-advanced-cloud-deployment/plan.md` (783 lines)

**Research Completed**: `specs/007-advanced-cloud-deployment/research.md`
- 7 technology decisions documented
- Dapr Pub/Sub with Kafka integration
- Skill agent design patterns
- Event-driven microservices testing
- Redpanda vs Kafka evaluation
- State management and secrets strategies
- Real-time updates approach

**Data Model**: `specs/007-advanced-cloud-deployment/data-model.md`
- 7 entities defined (Task, Reminder, Conversation, Message, Event, AuditLog, User)
- Complete relationships and state transitions
- Validation rules and indexes specified

**API Contracts**: `specs/007-advanced-cloud-deployment/contracts/`
- `backend-api.yaml`: OpenAPI 3.0 spec with all endpoints
- `kafka-events.yaml`: 4 Kafka topics with event schemas (task-events, reminders, task-updates, audit-events)
- `dapr-components.yaml`: Dapr component configs (Pub/Sub, State Store, Secrets)

**Quickstart Guide**: `specs/007-advanced-cloud-deployment/quickstart.md`
- 8-step setup process for local development
- Prerequisites and installation instructions
- Common troubleshooting guide

**Architecture Highlights**:

1. **6 Services** (Frontend, Backend, Chatbot, Notification, Recurring, Audit)
2. **4 Kafka Topics** (task-events, reminders, task-updates, audit-events)
3. **4 Skill Agents** (Task, Reminder, Recurring, Audit)
5. **3 System Prompts** (global behavior, clarification, error handling)
6. **Dapr Integration** (Pub/Sub, State, Secrets, Service Invocation)
7. **Deployment Targets** (Minikube local, AKS/GKE/DO cloud)

**Constitution Compliance**: ✅ ALL PASS
- Phase V principles (XII-XVIII): All satisfied
- Phase III/IV principles (I-XI): All preserved
- No violations or complexity issues

## Outcome

- ✅ Impact: HIGH - Complete architectural blueprint for production-ready, event-driven AI system with microservices, Dapr, and Kafka
- 🧪 Tests: Constitution compliance PASS, research validation PASS, data model completeness PASS, contracts validation PASS
- 📁 Files:
  - plan.md (783 lines, complete architecture)
  - research.md (7 technology decisions with rationale)
  - data-model.md (7 entities with relationships and indexes)
  - contracts/backend-api.yaml (OpenAPI 3.0 spec)
  - contracts/kafka-events.yaml (4 topics, 10+ event types)
  - contracts/dapr-components.yaml (Pub/Sub, State, Secrets configs)
  - quickstart.md (8-step setup guide)
- 🔁 Next prompts: `/sp.tasks` to break down into actionable implementation tasks with dependencies and test cases
- 🧠 Reflection: This plan establishes a production-grade, judge-friendly architecture for hackathon competitions. The clear separation between skill agents, system prompts, and microservices demonstrates advanced AI engineering. All technology decisions are justified with research and alternatives considered. The comprehensive contracts (API, events, Dapr) provide implementation blueprints. Local and cloud deployment parity ensures developer productivity while enabling production readiness.

## Evaluation notes (flywheel)

- Failure modes observed: None - Plan successfully created with all phases complete, research decisions documented, contracts defined
- Graders run and results (PASS/FAIL): PASS - Constitution check (18/18), research validation (7/7), data model completeness (7/7), contracts validation (3/3)
- Prompt variant (if applicable): Base plan creation from user-provided Phase 5 architecture draft
- Next experiment (smallest change to try): Run `/sp.tasks` to generate actionable implementation tasks with dependencies, test cases, and complexity estimates for all components (backend orchestrator, skill agents, microservices, deployment, testing)
