---
title: Todo Backend API
emoji: 🔧
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# Todo Backend API - Phase 4

## FastAPI Backend Service with Qwen AI Integration

### Features
- ✅ JWT Authentication
- ✅ Todo CRUD operations
- ✅ Qwen AI chatbot integration
- ✅ PostgreSQL database
- ✅ MCP (Model Context Protocol) tools
- ✅ Email notifications
- ✅ Reminder system

### API Endpoints

**Health Check:**
```bash
GET /health
```

**Authentication:**
```bash
POST /api/auth/register
POST /api/auth/login
POST /api/auth/verify-token
```

**Todos:**
```bash
GET    /api/todos
POST   /api/todos
GET    /api/todos/{id}
PUT    /api/todos/{id}
DELETE /api/todos/{id}
```

**Chat:**
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "add a todo to buy milk",
  "user_id": 1
}
```

### Environment Variables (Required Secrets)
- `DATABASE_URL` - PostgreSQL connection string (Neon Tech)
- `JWT_SECRET` - JWT signing secret (min 32 chars)
- `DASHSCOPE_API_KEY` - Qwen AI API key from Alibaba Cloud DashScope
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)
- `ENVIRONMENT` - Environment mode (development/production)

### Tech Stack
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Alembic (Database migrations)
- Qwen API (AI integration)
- PostgreSQL (Database)
- Docker (Containerization)

### Deployed on
- Backend: https://ammaraak-todo-api.hf.space
- Chatbot: https://ammaraak-todo-app-backend.hf.space
- Database: Neon PostgreSQL

### Author
Ammar Ak - Phase 4 Infrastructure Project

---
**Note:** This is the backend API service. For the chatbot service, visit the chatbot Space.
