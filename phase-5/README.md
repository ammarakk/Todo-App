# Phase 5: Advanced Cloud Deployment & Agentic Integration

**Last Updated**: 2026-02-04
**Status**: In Development
**Branch**: `007-advanced-cloud-deployment`

---

## Overview

Phase 5 transforms the Todo application into an AI-powered, cloud-native, event-driven system using:
- **Dapr** for service-to-service communication and state management
- **Kafka** (Redpanda) for event streaming
- **AI Skill Agents** for intelligent task management
- **Kubernetes** for container orchestration
- **GitHub Actions** for CI/CD automation

---

## Architecture

```
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
```

---

## Directory Structure

```
phase-5/
├── backend/          # FastAPI backend with Dapr integration
│   ├── src/
│   │   ├── api/      # FastAPI endpoints
│   │   ├── models/   # SQLAlchemy models
│   │   ├── services/ # Business logic
│   │   ├── agents/   # AI skill agents
│   │   ├── prompts/  # Agent system prompts
│   │   └── utils/    # Utilities (logging, error handling)
│   ├── tests/        # Unit, integration, contract tests
│   └── k8s/          # Kubernetes manifests
├── frontend/         # Next.js frontend (copied from Phase 4)
├── chatbot/          # MCP AI agents service
├── microservices/    # Specialized microservices
│   ├── notification/ # Reminder notifications
│   ├── recurring/    # Recurring task automation
│   └── audit/        # Audit logging service
├── kafka/            # Kafka/Redpanda docker-compose
├── dapr/             # Dapr component configurations
├── helm/             # Helm charts for deployment
├── docs/             # Architecture documentation
└── scripts/          # Deployment and utility scripts
```

---

## Quick Start

### Prerequisites

- **Kubernetes**: Minikube (local) or AKS/GKE (cloud)
- **Dapr CLI**: v1.12+
- **Helm**: v3.0+
- **Python**: 3.11+
- **Node.js**: 18+ (for frontend)

### Setup

1. **Start Kubernetes**
   ```bash
   minikube start --cpus=4 --memory=8192 --driver=docker
   ```

2. **Install Dapr**
   ```bash
   dapr init --runtime-version 1.12 --helm-chart
   ```

3. **Start Kafka**
   ```bash
   cd kafka
   docker-compose up -d
   ```

4. **Create Secrets**
   ```bash
   kubectl create secret generic db-credentials \
     --from-literal=username=postgres \
     --from-literal=password=secretpass \
     --from-literal=host=localhost
   ```

5. **Deploy Application**
   ```bash
   cd helm/todo-app
   helm install todo-app . --values values-local.yaml
   ```

6. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Dapr Dashboard: http://localhost:8080

---

## User Stories

### US1: Task Management with AI Assistant (P1 - MVP Core)
Users can create, update, complete, and delete tasks via natural language chat interface powered by AI agents.

### US2: Intelligent Reminders (P2)
Users receive proactive reminders for tasks due soon via email/push notifications.

### US3: Recurring Task Automation (P3)
System automatically generates next instance of recurring tasks after completion.

### US4: Real-Time Multi-Client Sync (P2)
Multiple clients see task updates in real-time via WebSocket connections.

### US5: Production Cloud Deployment (P1 - MVP Infrastructure)
Application deployed to cloud with CI/CD automation, monitoring, and production reliability.

---

## MVP Implementation Path

**Fast-Track MVP**: 52 tasks (Setup + Foundational + US1 core without tests)

**Full MVP**: 120 tasks (Setup + Foundational + US1 + US5)

1. **Phase 1**: Setup (T001-T007) - Directory structure, dependencies
2. **Phase 2**: Foundational (T008-T020) - Dapr, Kafka, Database
3. **Phase 3**: US1 Core (T021-T053) - AI task management
4. **Phase 7**: US5 Deployment (T093-T125) - Production infrastructure
5. **Incremental Addition**: US2, US3, US4 for full feature set

---

## Testing

```bash
# Unit tests
cd backend
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Contract tests
pytest tests/contract/

# With coverage
pytest --cov=src --cov-report=html
```

---

## Documentation

- **Specification**: `specs/007-advanced-cloud-deployment/spec.md`
- **Architecture Plan**: `specs/007-advanced-cloud-deployment/plan.md`
- **Implementation Guide**: `specs/007-advanced-cloud-deployment/implementation.md`
- **Tasks**: `specs/007-advanced-cloud-deployment/tasks.md`
- **Quickstart**: `specs/007-advanced-cloud-deployment/quickstart.md`

---

## CI/CD Pipeline

GitHub Actions workflow automatically:
1. Builds Docker images
2. Runs tests (unit, integration, contract)
3. Scans for vulnerabilities (Trivy, Bandit)
4. Pushes images to registry
5. Deploys to Kubernetes (Helm)
6. Runs smoke tests
7. Notifies on failure

---

## Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Loki**: Log aggregation
- **Dapr Dashboard**: Service mesh visualization

---

## Constitution Compliance

✅ All Phase V principles (XII-XVIII) satisfied
✅ All Phase III/IV principles (I-XI) preserved
✅ Event-driven microservices architecture
✅ AI skill agents reusable framework
✅ Dapr integration for cloud portability
✅ Production-ready CI/CD automation

---

## Next Steps

1. ✅ Complete Phase 1 Setup (T001-T007)
2. ⏳ Deploy Phase 2 Foundational (T008-T020)
3. ⏳ Implement US1 Core (T021-T053)
4. ⏳ Deploy US5 Production (T093-T125)
5. ⏳ Add US2, US3, US4 incrementally

---

**Status**: Phase 1 Setup Complete ✅
**Progress**: 7/142 tasks completed (5%)
**MVP Path**: On track for full MVP delivery
