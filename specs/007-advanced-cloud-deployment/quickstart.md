# Phase 5 Quickstart Guide

**Last Updated**: 2026-02-04
**Target Audience**: Developers setting up Phase 5 for local development

---

## Prerequisites

Install the following tools:

```bash
# Kubernetes (local)
brew install minikube  # macOS
choco install minikube  # Windows

# Dapr CLI
brew install dapr/tap/dapr-cli  # macOS
# Download from https://dapr.io/install/  # Windows

# Helm
brew install helm  # macOS
choco install kubernetes-helm  # Windows

# kubectl
brew install kubectl  # macOS
choco install kubectl  # Windows

# Python 3.11+
brew install python@3.11  # macOS

# Node.js 18+ (for frontend)
brew install node  # macOS
```

Verify installations:

```bash
minikube version
dapr version
helm version
kubectl version
python --version
node --version
```

---

## Step 1: Start Local Kubernetes

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify
kubectl get nodes
```

---

## Step 2: Install Dapr

```bash
# Initialize Dapr in Minikube
dapr init --runtime-version 1.12 --helm-chart

# Verify Dapr installed
kubectl get pods -n dapr-system
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
dapr-dashboard-7b8f7b5c9-xabc2          1/1     Running   0          2m
dapr-operator-7d9f8d6c5-yxyz3           1/1     Running   0          2m
dapr-placement-server-9c8d7d6d5-zabc4   1/1     Running   0          2m
dapr-sidecar-injector-8b7f7b5c9-xabc2   1/1     Running   0          2m
dapr-sentry-7b8f7b5c9-xabc2             1/1     Running   0          2m
```

---

## Step 3: Start Kafka (Redpanda)

```bash
cd phase-5/kafka
docker-compose up -d

# Verify Redpanda running
docker ps | grep redpanda
```

---

## Step 4: Create Kubernetes Secrets

```bash
# Database credentials (use Neon or local PostgreSQL)
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=secretpass \
  --from-literal=host=neon.db \
  --from-literal=connectionstring="host=neon.db user=postgres password=secretpass dbname=todo"

# Email service (use SendGrid or mock)
kubectl create secret generic email-credentials \
  --from-literal=api-key=SG.mock \
  --from-literal=from-email=noreply@todo-app.local

# Ollama URL (assume local)
kubectl create secret generic ollama-config \
  --from-literal url=http://host.docker.internal:11434
```

---

## Step 5: Deploy Application

```bash
cd phase-5/helm/todo-app

# Install with local values
helm install todo-app . --values values-local.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=todo-app --timeout=300s
```

Verify deployment:

```bash
kubectl get pods
```

Expected output:
```
NAME                             READY   STATUS    RESTARTS   AGE
frontend-7d9f8d6c5-xabc2         2/2     Running   0          1m
backend-7d9f8d6c5-yxyz3           2/2     Running   0          1m
chatbot-8b7f7b5c9-zabc4           2/2     Running   0          1m
notification-9c8d7d6d5-aefg5       2/2     Running   0          1m
recurring-0d8e8e6e6-bghj6          2/2     Running   0          1m
audit-1e9f9f7f7-cijk7             2/2     Running   0          1m
```

Note: `2/2` means app container + Dapr sidecar.

---

## Step 6: Port-Forward Services

```bash
# Frontend (Terminal 1)
kubectl port-forward svc/frontend 3000:3000

# Backend API (Terminal 2)
kubectl port-forward svc/backend 8000:8000

# Dapr Dashboard (Terminal 3)
kubectl port-forward svc/dapr-dashboard 8080:8080
```

---

## Step 7: Access Application

1. **Frontend**: Open http://localhost:3000

2. **Backend API**: http://localhost:8000/docs (FastAPI auto-docs)

3. **Dapr Dashboard**: http://localhost:8080

---

## Step 8: Test the System

### Test 1: Create Task via API

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task from Quickstart",
    "priority": "high"
  }'
```

Expected response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Test Task from Quickstart",
  "status": "active",
  "priority": "high",
  "created_at": "2026-02-04T10:00:00Z"
}
```

### Test 2: Create Task via Chatbot

```bash
curl -X POST http://localhost:8000/chat/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Create a task to buy milk tomorrow at 5pm",
    "conversation_id": "test-conversation-1"
  }'
```

Expected response:
```json
{
  "response": "I've created a task 'buy milk' due tomorrow at 5pm.",
  "intent_detected": "create_task",
  "skill_agent_used": "TaskAgent",
  "confidence_score": 0.95,
  "task_created": {
    "task_id": "...",
    "title": "buy milk",
    "due_date": "2026-02-05T17:00:00Z"
  }
}
```

### Test 3: Verify Kafka Events

Open Redpanda Console: http://localhost:8080 (Redpanda UI, if enabled)

Or use CLI:

```bash
# List topics
docker exec -it redpanda rpk topic list

# Consume events
docker exec -it redpanda rpk topic consume task-events
```

---

## Common Issues

### Issue: Pods stuck in "Pending" state

**Solution**:
```bash
kubectl describe pod <pod-name>
# Check events section for resource issues
```

### Issue: Dapr sidecar not ready

**Solution**:
```bash
kubectl logs <pod-name> -c daprd
# Check Dapr logs for errors
```

### Issue: Can't reach backend from frontend

**Solution**:
```bash
# Verify Dapr sidecar is injected
kubectl get pod <frontend-pod> -o jsonpath='{.spec.containers[*].name}'
# Should include: frontend, daprd
```

### Issue: Kafka connection refused

**Solution**:
```bash
# Verify Redpanda is running
docker ps | grep redpanda

# Check network connectivity
kubectl exec -it backend -- curl -v kafka:9092
```

---

## Development Workflow

### 1. Make Code Changes

Edit files in `phase-5/backend/src/`, `phase-5/frontend/src/`, etc.

### 2. Rebuild Container Images

```bash
# Backend
docker build -t todo-backend:dev phase-5/backend

# Frontend
docker build -t todo-frontend:dev phase-5/frontend
```

### 3. Restart Pods

```bash
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend
```

### 4. View Logs

```bash
# App logs
kubectl logs -f deployment/backend -c backend

# Dapr logs
kubectl logs -f deployment/backend -c daprd
```

---

## Cleanup

```bash
# Delete application
helm uninstall todo-app

# Delete secrets
kubectl delete secret db-credentials email-credentials ollama-config

# Stop Redpanda
cd phase-5/kafka
docker-compose down

# Uninstall Dapr (optional)
dapr uninstall --all

# Stop Minikube (optional)
minikube stop
```

---

## Next Steps

1. **Read the architecture**: `phase-5/docs/architecture.md`
2. **Explore skill agents**: `phase-5/agents/skills/`
3. **Review API contracts**: `specs/007-advanced-cloud-deployment/contracts/`
4. **Run tests**: `cd phase-5 && pytest tests/`

---

**Quickstart Status**: ✅ Complete - Ready for local development
