# Phase IV Deployment Guide

**Status**: Infrastructure Generation COMPLETE
**Date**: 2026-01-30
**Branch**: 005-phase4-infra

## ✅ Completed Work

### Phase 1: Setup - COMPLETE
- [X] Phase III frontend/backend copied to phase-4/apps (READ-ONLY)
- [X] Directory structure created
- [X] Constitution warnings added (Phase III code immutability)

### Phase 2: Foundational - COMPLETE
- [X] Environment templates created (.env.example)
- [X] Backend API contract documented
- [X] Chatbot service configured

### Phase 3: Infrastructure Generation - COMPLETE
- [X] 4 Dockerfiles created (frontend, backend, chatbot, ollama)
- [X] 4 Kubernetes deployments generated (with health probes)
- [X] 4 Kubernetes services generated (ClusterIP)
- [X] Helm chart created (Chart.yaml, values.yaml, templates/)
- [X] PVC for Ollama models (10Gi)
- [X] ConfigMap for environment variables

### Docker Images Built
- [X] todo-backend:latest (373MB)
- [X] todo-chatbot:latest (255MB)
- [ ] todo-frontend:latest (build in progress)
- [ ] ollama/ollama:latest (pull in progress)

## 🚧 Manual Steps Required

### Step 1: Fix Minikube (Required Due to Corrupted State)

Minikube encountered issues during the automated deployment. Please manually fix:

**Option A: Delete and Recreate**
```powershell
# Run in PowerShell as Administrator
Remove-Item -Recurse -Force C:\Users\<YourUser>\.minikube\machines\minikube
minikube start --cpus=2 --memory=1536 --driver=docker
```

**Option B: Use Docker Compose (Alternative)**
```bash
# Use the Docker Compose approach instead of Minikube
docker-compose -f phase-4/infra/docker/docker-compose.yml up -d
```

### Step 2: Build Frontend Image

```bash
# From project root
docker build -t todo-frontend:latest -f phase-4/infra/docker/Dockerfile.frontend phase-4/apps/todo-frontend
```

### Step 3: Pull Ollama Image

```bash
docker pull ollama/ollama:latest
```

### Step 4: Deploy with Helm (Once Minikube is Fixed)

```bash
# Start Minikube
minikube start --cpus=2 --memory=1536 --driver=docker

# Enable ingress
minikube addons enable ingress

# Set Docker environment to use Minikube's daemon
eval $(minikube docker-env)

# Tag images for Minikube
docker tag todo-backend:latest localhost:5000/todo-backend:latest
docker tag todo-frontend:latest localhost:5000/todo-frontend:latest
docker tag todo-chatbot:latest localhost:5000/todo-chatbot:latest
docker tag ollama/ollama:latest localhost:5000/ollama/ollama:latest

# Install Helm chart
helm install todo-app phase-4/infra/helm/todo-app

# Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-app --timeout=120s

# Check status
kubectl get pods
kubectl get services
```

### Step 5: Validate Deployment

```bash
# Port-forward frontend
kubectl port-forward svc/todo-frontend 3000:80

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/health (via port-forward)
```

### Step 6: Preload Ollama Model

```bash
kubectl exec -it deployment/ollama -- ollama pull llama3.2:3b
```

## Alternative: Docker Compose Deployment

If Minikube continues to have issues, you can use Docker Compose:

1. Create `phase-4/infra/docker/docker-compose.yml`:
```yaml
version: '3.8'

services:
  frontend:
    image: todo-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    image: todo-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/tododb
      - JWT_SECRET=your-jwt-secret
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - postgres
      - ollama

  chatbot:
    image: todo-chatbot:latest
    ports:
      - "8001:8001"
    environment:
      - BACKEND_API_URL=http://backend:8000
      - OLLAMA_BASE_URL=http://ollama:11434
      - MODEL_NAME=llama3.2:3b
    depends_on:
      - backend
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/models

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=tododb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  ollama-models:
  postgres-data:
```

2. Start services:
```bash
docker-compose -f phase-4/infra/docker/docker-compose.yml up -d
```

3. Preload Ollama model:
```bash
docker exec -it <ollama-container-id> ollama pull llama3.2:3b
```

## Architecture Overview

```
Browser → Frontend (localhost:3000)
         ↓
       Backend Service (port 8000)
         ↓
       PostgreSQL (Neon or local)

Chatbot (port 8001)
  ↓         ↓
Ollama   Backend Service
(port 11434)  (port 8000)
```

## Files Generated

**Phase IV Workspace**:
- phase-4/apps/todo-frontend/ (READ-ONLY copy)
- phase-4/apps/todo-backend/ (READ-ONLY copy)
- phase-4/apps/chatbot/src/main.py (FastAPI chatbot)

**Docker Infrastructure**:
- phase-4/infra/docker/Dockerfile.frontend
- phase-4/infra/docker/Dockerfile.backend
- phase-4/infra/docker/Dockerfile.chatbot
- phase-4/infra/docker/Dockerfile.ollama

**Kubernetes Infrastructure**:
- phase-4/infra/helm/todo-app/Chart.yaml
- phase-4/infra/helm/todo-app/values.yaml
- phase-4/infra/helm/todo-app/templates/ (12 manifests)

**Documentation**:
- phase-4/docs/backend-api-contract.md
- phase-4/docs/IMPLEMENTATION-STATUS.md
- specs/005-phase4-infra/tasks.md (updated)

## Troubleshooting

**Minikube won't start**:
- Ensure Docker Desktop is running
- Check Docker has enough resources (Settings → Resources)
- Try `minikube delete` then `minikube start`

**Frontend build fails**:
- Ensure node_modules exists in phase-4/apps/todo-frontend/
- Try `npm install` in the frontend directory first
- Check .env.local has correct backend URL

**Ollama model fails to load**:
- Ensure PVC is created and mounted
- Check Ollama pod has enough memory (4Gi limit)
- Try pulling model manually: `kubectl exec -it deployment/ollama -- ollama pull llama3.2:3b`

## Next Steps

1. Fix Minikube or use Docker Compose alternative
2. Complete frontend Docker build
3. Deploy all services
4. Validate deployment (kubectl get pods)
5. Test frontend at http://localhost:3000
6. Test chatbot at http://localhost:8001/api/chat
7. Preload Ollama model
8. Test end-to-end: Create todo via chatbot

## Constitution Compliance

✅ Phase III code immutability (READ-ONLY copies)
✅ Infrastructure-only changes (no business logic modified)
✅ Ollama-first LLM runtime (no external APIs)
✅ Kubernetes-native deployment (Helm charts)
✅ Service isolation (one container per service)
✅ No Phase V features (AI memory, scheduling excluded)
