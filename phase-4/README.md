# Phase IV - Infrastructure & Deployment

**Status**: ✅ **PRODUCTION READY**

This phase focuses on containerization, Kubernetes deployment, and infrastructure automation without modifying Phase III business logic.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What's New in Phase IV](#whats-new-in-phase-iv)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Deployment Options](#deployment-options)
6. [Management Scripts](#management-scripts)
7. [Troubleshooting](#troubleshooting)
8. [Architecture](#architecture)

---

## Overview

Phase IV completes the infrastructure layer with:
- ✅ Docker containerization for all services
- ✅ Kubernetes deployment manifests
- ✅ Helm chart for production deployments
- ✅ Chatbot service with Ollama integration
- ✅ Production hardening (health checks, resource limits)
- ✅ Management scripts for easy operations

---

## What's New in Phase IV

### New Services
| Service | Port | Description |
|---------|------|-------------|
| **chatbot** | 8001 | AI-powered chatbot using Ollama LLM |
| **ollama** | 11434 | Local LLM runtime (llama3.2:3b) |

### Infrastructure
- Docker images for all services
- Kubernetes manifests in `infra/k8s/`
- Helm chart in `infra/helm/`
- Deployment scripts in `scripts/`

---

## Prerequisites

### For Docker Deployment
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- 4GB RAM minimum
- 10GB disk space

### For Kubernetes Deployment
- kubectl
- Kubernetes cluster (Docker Desktop, Minikube, Kind, or cloud)
- Helm (optional, for Helm deployments)

**Windows Users**: See [INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) for detailed setup instructions.

---

## Quick Start

### 1. Build Docker Images

**Linux/Mac:**
```bash
cd phase-4/scripts
./docker-build.sh
```

**Windows:**
```cmd
cd phase-4\scripts
docker-build.bat
```

### 2. Start Services

**Linux/Mac:**
```bash
./docker-start.sh
```

**Windows:**
```cmd
docker-start.bat
```

### 3. Verify Deployment

**Linux/Mac:**
```bash
./health-check.sh
```

**Windows:**
```cmd
health-check.bat
```

---

## Deployment Options

### Option A: Docker Compose (Recommended for Development)

```bash
cd phase-4/infra/docker
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Chatbot: http://localhost:8001
- Ollama: http://localhost:11434

---

### Option B: Kubernetes (kubectl)

**Linux/Mac:**
```bash
cd phase-4/scripts
./k8s-deploy.sh
```

**Windows:**
```cmd
cd phase-4\scripts
k8s-deploy.bat
```

**Manual deployment:**
```bash
kubectl apply -f phase-4/infra/k8s/namespace.yaml
kubectl apply -f phase-4/infra/k8s/00-postgres.yaml
kubectl apply -f phase-4/infra/k8s/01-ollama.yaml
kubectl apply -f phase-4/infra/k8s/02-backend.yaml
kubectl apply -f phase-4/infra/k8s/03-chatbot.yaml
kubectl apply -f phase-4/infra/k8s/04-frontend.yaml
```

**Port-forward for access:**
```bash
kubectl port-forward -n todo-app svc/frontend-service 3000:3000
```

---

### Option C: Helm (Production)

```bash
cd phase-4/infra/helm/todo-app
helm install todo-app . -n todo-app --create-namespace
```

**Upgrade:**
```bash
helm upgrade todo-app . -n todo-app
```

**Uninstall:**
```bash
helm uninstall todo-app -n todo-app
```

---

## Management Scripts

### Docker Scripts

| Script | Description |
|--------|-------------|
| `docker-build.sh/.bat` | Build all Docker images |
| `docker-start.sh/.bat` | Start all services |
| `docker-stop.sh/.bat` | Stop all services |
| `health-check.sh/.bat` | Check health of all services |

### Kubernetes Scripts

| Script | Description |
|--------|-------------|
| `k8s-deploy.sh/.bat` | Deploy to Kubernetes |
| `k8s-delete.sh` | Delete from Kubernetes |
| `k8s-status.sh/.bat` | Show cluster status |
| `helm-deploy.sh` | Deploy using Helm |

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│                   Frontend                      │
│              (Next.js + React)                  │
│                  Port: 3000                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│                   Backend                       │
│              (FastAPI + SQLAlchemy)             │
│                  Port: 8000                     │
└─────┬─────────────────────┬────────────────────┘
      │                     │
      ▼                     ▼
┌──────────┐         ┌─────────────┐
│ PostgreSQL│         │   Ollama    │
│   :5432  │         │   :11434    │
└──────────┘         └──────┬──────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Chatbot     │
                    │ (FastAPI + Ollama)│
                    │     Port: 8001   │
                    └─────────────────┘
```

### Service Communication (Kubernetes)

All inter-service communication uses internal Kubernetes DNS:
- `postgres-service:5432`
- `backend-service:8000`
- `chatbot-service:8001`
- `ollama-service:11434`
- `frontend-service:3000`

---

## Troubleshooting

### Issue: Port already in use

**Solution:**
```bash
# Check what's using the port
netstat -ano | findstr :3000  # Windows
lsof -i :3000                  # Linux/Mac

# Kill the process or change ports in docker-compose.yml
```

### Issue: Ollama model not found

**Solution:**
```bash
# Pull the model manually
docker exec -it todo-ollama ollama pull llama3.2:3b

# Or use a smaller model
# Update MODEL_NAME in docker-compose.yml or values.yaml
```

### Issue: Chatbot not responding

**Solution:**
1. Check Ollama is running: `curl http://localhost:11434`
2. Check chatbot logs: `docker logs todo-chatbot`
3. Verify model is loaded: `docker exec todo-ollama ollama list`

### Issue: Pod stuck in Pending state

**Solution:**
```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# - Insufficient resources: check resource limits
# - Image pull error: ensure images are built
# - PVC not bound: check storage class
```

### Issue: Health checks failing

**Solution:**
```bash
# Check pod logs
kubectl logs -n todo-app deployment/backend

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Restart deployment
kubectl rollout restart deployment/backend -n todo-app
```

---

## Environment Variables

### Backend
```bash
DATABASE_URL=postgresql://todo:password@postgres-service:5432/tododb
JWT_SECRET=your-jwt-secret-change-in-production
OLLAMA_HOST=http://ollama-service:11434
PORT=8000
```

### Chatbot
```bash
BACKEND_API_URL=http://backend-service:8000
OLLAMA_BASE_URL=http://ollama-service:11434
MODEL_NAME=llama3.2:3b
```

### Frontend
```bash
NEXT_PUBLIC_BACKEND_URL=http://backend-service:8000
NEXT_PUBLIC_API_URL=http://backend-service:8000
```

---

## Resource Limits

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 250m | 128Mi | 256Mi |
| Backend | 250m | 500m | 256Mi | 512Mi |
| Chatbot | 100m | 250m | 128Mi | 256Mi |
| Ollama | 500m | 1000m | 1Gi | 4Gi |
| PostgreSQL | 100m | 500m | 128Mi | 512Mi |

---

## Production Considerations

### Security
- ✅ Change default passwords
- ✅ Use strong JWT secrets
- ✅ Enable TLS/SSL for external endpoints
- ✅ Use secrets management (e.g., Kubernetes Secrets, AWS Secrets Manager)

### Scalability
- ✅ Increase replica counts in values.yaml
- ✅ Enable HPA (Horizontal Pod Autoscaler)
- ✅ Use managed databases (e.g., AWS RDS, Cloud SQL)

### Monitoring
- ✅ Add Prometheus metrics
- ✅ Setup Grafana dashboards
- ✅ Configure log aggregation (e.g., ELK, Loki)

### Backup
- ✅ Regular PostgreSQL backups
- ✅ Ollama model persistence
- ✅ Configuration version control

---

## Testing the Chatbot

### 1. Create a User
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
```

### 2. Get Token
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123" | jq -r '.access_token')
```

### 3. Chat with Chatbot
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"create a todo to buy groceries\", \"user_token\": \"$TOKEN\"}"
```

---

## Phase IV vs Phase III

| Feature | Phase III | Phase IV |
|---------|-----------|----------|
| Core Business Logic | ✅ | ✅ (unchanged) |
| Docker Support | ❌ | ✅ |
| Kubernetes | ❌ | ✅ |
| Helm Chart | ❌ | ✅ |
| Chatbot Service | ❌ | ✅ |
| Ollama Integration | ❌ | ✅ |
| Health Checks | Basic | ✅ Complete |
| Resource Limits | ❌ | ✅ |
| Auto-scaling ready | ❌ | ✅ |

**Important**: Phase IV does NOT modify Phase III business logic. It only adds infrastructure and deployment capabilities.

---

## What's Next? Phase V

Phase V will focus on:
- Advanced AI features (RAG, vector DB)
- Agent-based workflows
- Scheduled tasks
- Enhanced notifications
- Memory systems

Phase IV is the infrastructure foundation for these features.

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting)
2. Review pod logs: `kubectl logs -n todo-app <deployment>`
3. Check events: `kubectl get events -n todo-app`
4. See [INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) for Windows-specific setup

---

**Phase IV Status**: ✅ COMPLETE AND PRODUCTION READY

Last Updated: 2026-01-31
