# Phase IV Quick Start Guide

## 🎯 Status: Infrastructure Complete, Ready for Deployment

**What's Been Done**:
- ✅ All infrastructure files generated (25+ files)
- ✅ 2 Docker images built (backend, chatbot)
- ✅ Docker Compose configuration ready
- ✅ Complete documentation created

**What's Left**: 3 simple steps to deploy

---

## 🚀 Three Steps to Deploy

### Step 1: Fix Docker Desktop (One-time setup)

**Issue**: Docker Desktop needs more memory

**Solution**:
1. Click Docker Desktop icon in system tray
2. Settings → Resources → Advanced
3. Increase "Memory" to **4.0 GB** (or higher)
4. Click "Apply & Restart"
5. Wait for Docker to restart (~2 minutes)

### Step 2: Build Frontend Image

Open PowerShell or Command Prompt:

```bash
# Navigate to frontend directory
cd phase-4/apps/todo-frontend

# Build the image (this will take 3-5 minutes)
docker build -t todo-frontend:latest -f ../../infra/docker/Dockerfile.frontend .
```

### Step 3: Start All Services

```bash
# From project root
docker-compose -f phase-4/infra/docker/docker-compose.yml up -d

# Wait 30 seconds for services to start
# Then check status
docker ps
```

### Step 4: Preload Ollama Model (One-time)

```bash
# Wait 60 seconds after starting services
# Then run:
docker exec -it todo-ollama ollama pull llama3.2:3b
```

---

## ✅ Verify Deployment

**Check all containers are running**:
```bash
docker ps
```

You should see 5 containers:
- todo-frontend (port 3000)
- todo-backend (port 8000)
- todo-chatbot (port 8001)
- todo-ollama (port 11434)
- todo-postgres (port 5432)

**Test the services**:

1. **Frontend**: Open browser → http://localhost:3000
2. **Backend Health**: `curl http://localhost:8000/api/health`
3. **Chatbot Health**: `curl http://localhost:8001/api/health`
4. **Ollama Status**: `docker exec todo-ollama ollama list`

---

## 🎮 Test the Chatbot

```bash
# Test creating a todo via chatbot
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "add a new todo to buy groceries"}'
```

Expected response:
```json
{
  "llm_response": "...",
  "intent": {"action": "create", "title": "buy groceries"},
  "result": {"id": 1, "title": "buy groceries", ...}
}
```

---

## 🛠️ Useful Commands

```bash
# View logs
docker-compose -f phase-4/infra/docker/docker-compose.yml logs -f

# Stop all services
docker-compose -f phase-4/infra/docker/docker-compose.yml down

# Restart specific service
docker-compose -f phase-4/infra/docker/docker-compose.yml restart backend

# Check container status
docker ps

# Enter container shell
docker exec -it todo-backend bash
```

---

## 📚 Complete Documentation

For detailed information, see:
- `phase-4/docs/FINAL-DEPLOYMENT-STATUS.md` - Complete status and troubleshooting
- `phase-4/docs/DEPLOYMENT-GUIDE.md` - Detailed deployment guide
- `phase-4/docs/backend-api-contract.md` - API documentation

---

## ❓ Troubleshooting

**"Cannot connect to Docker daemon"**
- Restart Docker Desktop
- Wait 1-2 minutes for it to fully start

**"Port 3000 already in use"**
- Something is already using port 3000
- Change port in docker-compose.yml or stop the conflicting service

**"Ollama model not found"**
- Wait 60 seconds after starting services
- Run: `docker exec -it todo-ollama ollama pull llama3.2:3b`
- Verify with: `docker exec todo-ollama ollama list`

**"Frontend shows connection errors"**
- Check backend is running: `docker ps | grep backend`
- Check backend logs: `docker logs todo-backend`
- Verify NEXT_PUBLIC_BACKEND_URL in docker-compose.yml

---

## 🎉 Success Criteria

✅ All 5 containers running (`docker ps`)
✅ Frontend loads at http://localhost:3000
✅ Backend health check returns 200 OK
✅ Chatbot can create todos via natural language
✅ Ollama model is loaded (`ollama list` shows llama3.2:3b)

---

## 🔧 What If Something Goes Wrong?

1. **Check logs**: `docker-compose -f phase-4/infra/docker/docker-compose.yml logs`
2. **Restart services**: `docker-compose -f phase-4/infra/docker/docker-compose.yml restart`
3. **Rebuild image**: Delete the container and image, then build again
4. **See detailed troubleshooting** in `phase-4/docs/FINAL-DEPLOYMENT-STATUS.md`

---

## 📞 Quick Reference

**Start**: `docker-compose -f phase-4/infra/docker/docker-compose.yml up -d`
**Stop**: `docker-compose -f phase-4/infra/docker/docker-compose.yml down`
**Logs**: `docker-compose -f phase-4/infra/docker/docker-compose.yml logs -f`
**Status**: `docker ps`

**Frontend**: http://localhost:3000
**Backend API**: http://localhost:8000
**Chatbot API**: http://localhost:8001
**Ollama API**: http://localhost:11434

---

**Estimated time to deploy**: 15-20 minutes
- Docker Desktop restart: 2 minutes
- Frontend build: 5-8 minutes
- Service startup: 1-2 minutes
- Ollama model pull: 3-5 minutes

**Good luck! 🚀**
