# Phase III Deployment Guide
## AI-Powered Todo Chatbot

**Status:** ✅ 100% Complete
**Last Updated:** 2026-01-25
**Branch:** `phase-2`

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Setup](#database-setup)
6. [Testing & Verification](#testing--verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services

1. **Neon PostgreSQL** (Database)
   - Get free account at https://neon.tech/
   - Create a project
   - Copy connection string

2. **Hugging Face Account** (Qwen AI Model)
   - Get free account at https://huggingface.co/
   - Generate API token
   - Token format: `hf_xxxxxxxxxxxxxxxxxxxxxxxx`

3. **Vercel Account** (Frontend Hosting)
   - Get free account at https://vercel.com/
   - Connect GitHub repository

### Local Development

```bash
# Python 3.12+
python --version

# Node.js 18+
node --version

# Git
git --version
```

---

## Environment Setup

### Backend Environment Variables (`.env`)

```bash
# Phase III Configuration
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
HUGGINGFACE_API_KEY=hf_your_huggingface_api_key_here
QWEN_MODEL=Qwen/Qwen-14B-Chat

# JWT Configuration (from Phase II)
JWT_SECRET=your-jwt-secret-key-here

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

### Frontend Environment Variables (`.env.local`)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production deployment, use your Vercel URL:
# NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
```

---

## Backend Deployment

### Option 1: Run Locally

```bash
# 1. Navigate to project root
cd todo-app-new

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run database migration
python backend/scripts/migrate_ai_tables.py

# 4. Start backend server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Verify server is running
curl http://localhost:8000/health
```

### Option 2: Deploy to Vercel/Railway/Render

1. **Create `vercel.json`** (if using Vercel for backend):

```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/main.py"
    }
  ]
}
```

2. **Push to GitHub:**

```bash
git add .
git commit -m "feat: Phase III backend deployment"
git push origin phase-2
```

3. **Connect to Vercel:**
   - Import project in Vercel
   - Add environment variables
   - Deploy

---

## Frontend Deployment

### Deploy to Vercel

```bash
# 1. Install frontend dependencies
cd frontend
npm install

# 2. Build frontend
npm run build

# 3. Test locally
npm run start

# 4. Deploy to Vercel
vercel --prod
```

### Vercel Environment Variables

Add these in Vercel Dashboard > Project > Settings > Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## Database Setup

### Run Migration Script

```bash
# From project root
python backend/scripts/migrate_ai_tables.py
```

This creates:
- ✅ `users` table
- ✅ `conversation` table
- ✅ `message` table
- ✅ `todos` table (when using Neon)

### Verify Tables

```python
from sqlmodel import create_engine, Session, text

DATABASE_URL = "your_neon_database_url"
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    result = session.exec(text("SELECT name FROM sqlite_master WHERE type='table'"))
    print(result.fetchall())
```

---

## Testing & Verification

### 1. Test Backend Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Chat health
curl http://localhost:8000/api/chat/health

# API docs (open in browser)
open http://localhost:8000/docs
```

### 2. Test Chat API (with JWT)

```bash
# Get JWT token from Phase II login first
JWT_TOKEN="your_jwt_token_here"

# Send message to AI
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy milk"
  }'
```

Expected Response:
```json
{
  "reply": "Task 'buy milk' created successfully!",
  "conversation_id": "uuid-here",
  "tool_calls": [
    {
      "tool": "create_task",
      "success": true,
      "result": {
        "task": { ... }
      }
    }
  ]
}
```

### 3. Test Frontend

1. Open http://localhost:3000/chat
2. Login with Phase II credentials
3. Try these commands:

**English:**
- "Add a task to buy milk"
- "Show my tasks"
- "Mark task 1 as complete"

**Urdu:**
- "دودھ لینے کا ٹاسک شامل کرو"
- "میرے ٹاسک دکھاؤ"
- "پہلا ٹاسک مکمل کرو"

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
Error: NEON_DATABASE_URL not found in environment variables
```

**Solution:**
```bash
# Create .env file in project root
cp .env.example .env

# Edit .env and add your Neon database URL
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
```

#### 2. Hugging Face API Error

```
Error: Model not found or API key invalid
```

**Solution:**
- Verify Hugging Face API key is correct
- Check model name: `Qwen/Qwen-14B-Chat`
- Ensure API key has access to the model

#### 3. JWT Authentication Error

```
Error: Could not validate credentials
```

**Solution:**
- Ensure JWT_SECRET matches between Phase II and Phase III
- Verify token is not expired
- Check Authorization header format: `Bearer <token>`

#### 4. CORS Error

```
Error: CORS policy blocked request
```

**Solution:**
In `backend/main.py`, ensure CORS origins include your frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5. Unicode Encoding Error

```
Error: 'charmap' codec can't encode character
```

**Solution:**
This is fixed in the migration script. If you see it elsewhere:

```python
# Set UTF-8 encoding
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   /chat         │
└────────┬────────┘
         │ HTTP + JWT
         ▼
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
│   /api/chat     │
└────────┬────────┘
         │
    ┌────┴─────┐
    │           │
    ▼           ▼
┌───────┐  ┌─────────┐
│ Qwen  │  │  Neon   │
│  AI    │  │ Database│
└───────┘  └─────────┘
```

---

## Performance Optimization

### Backend

- **Connection Pooling:** Already implemented in SQLModel
- **Async Operations:** All MCP tools are async
- **Retry Logic:** Qwen client has exponential backoff

### Frontend

- **Message Pagination:** Only last 10 messages shown
- **Lazy Loading:** Components load on demand
- **Debouncing:** Input changes are debounced

---

## Security Checklist

✅ JWT authentication on all endpoints
✅ User isolation in all database queries
✅ SQL injection prevention (SQLModel parameterized queries)
✅ CORS configured for specific origins
✅ Input validation (message length 1-1000 chars)
✅ Error messages don't expose sensitive data
✅ Environment variables for secrets

---

## Monitoring & Logs

### Backend Logs

```bash
# View logs
tail -f backend/logs/app.log

# Check for errors
grep "ERROR" backend/logs/app.log

# Monitor chat requests
grep "Chat request" backend/logs/app.log
```

### Database Monitoring

```sql
-- Check conversation count
SELECT COUNT(*) FROM conversation;

-- Check message count per user
SELECT user_id, COUNT(*) as message_count
FROM message m
JOIN conversation c ON m.conversation_id = c.id
GROUP BY user_id;

-- Recent conversations
SELECT * FROM conversation
ORDER BY created_at DESC
LIMIT 10;
```

---

## Next Steps

### Optional Enhancements

1. **Streaming Responses:** Use WebSocket for real-time AI responses
2. **File Upload:** Allow users to upload files for AI analysis
3. **Voice Input:** Add speech-to-text for voice commands
4. **Task Reminders:** Email/push notifications for due dates
5. **Analytics Dashboard:** Track user engagement metrics

### Additional User Stories

- **User Story 2:** View Tasks via Conversation (P2)
- **User Story 3:** Delete Tasks via Natural Commands (P3)
- **User Story 4:** Mark Tasks Complete (P4)

All are already implemented via MCP tools!

---

## Support

**Documentation:**
- Spec: `specs/001-ai-chatbot/spec.md`
- Plan: `specs/001-ai-chatbot/plan.md`
- Tasks: `specs/001-ai-chatbot/tasks.md`

**Issues:** Create GitHub issue with label `phase-3`

**Contact:** Check project README for contact info

---

**Deployment Status:** ✅ READY FOR PRODUCTION

**Last Verified:** 2026-01-25
