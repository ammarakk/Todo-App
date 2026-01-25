# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot
**Phase**: Phase 1 - Design & Contracts
**Date**: 2025-01-25

## Overview

This guide will help you set up and run the Phase III AI-Powered Todo Chatbot locally. The chatbot enables task management through natural language in English and Urdu.

---

## Prerequisites

Before you begin, ensure you have the following:

### Required Accounts

1. **Neon PostgreSQL Account**
   - Sign up at: https://neon.tech
   - Create a free project
   - Save the connection string (format: `postgresql://user:password@host/database`)

2. **Hugging Face Account**
   - Sign up at: https://huggingface.co
   - Get API key from: https://huggingface.co/settings/tokens
   - Ensure access to Qwen model (public access available)

### Required Software

- **Python 3.11+** - Download from: https://www.python.org/downloads/
- **Node.js 18+** - Download from: https://nodejs.org/
- **Git** - Download from: https://git-scm.com/

### Existing System

- **Phase II Todo App** running locally or deployed
- **JWT Authentication** from Phase II configured

---

## Setup Instructions

### Step 1: Clone Repository and Checkout Branch

```bash
# Clone the repository
git clone https://github.com/ammarakk/Todo-App.git
cd Todo-App

# Checkout Phase III feature branch
git checkout 001-ai-chatbot

# Verify branch
git branch
# Output: * 001-ai-chatbot
```

---

### Step 2: Backend Setup

#### 2.1 Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary huggingface_hub mcp python-jose[cryptography] passlib[bcrypt]

# Return to project root
cd ..
```

#### 2.2 Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file

# Neon PostgreSQL Database
NEON_DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Hugging Face API
HUGGINGFACE_API_KEY=hf_your_api_key_here

# JWT Secret (from Phase II)
JWT_SECRET=your_jwt_secret_here

# Qwen Model Settings
QWEN_MODEL=Qwen/Qwen-14B-Chat
HF_INFERENCE_TIMEOUT=8

# Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

**Replace placeholder values**:
- `NEON_DATABASE_URL`: Your Neon connection string
- `HUGGINGFACE_API_KEY`: Your Hugging Face API token
- `JWT_SECRET`: Your JWT secret from Phase II

#### 2.3 Run Database Migrations

```bash
# From project root
python backend/scripts/migrate_ai_tables.py

# Expected output:
# ✅ Checking database connection...
# ✅ Creating conversation table...
# ✅ Creating message table...
# ✅ Migration complete!
```

If the script doesn't exist, create it manually:

```python
# backend/scripts/migrate_ai_tables.py
import os
from sqlmodel import SQLModel, create_engine
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate():
    print("✅ Checking database connection...")
    with engine.connect() as conn:
        pass

    print("✅ Creating tables...")
    SQLModel.metadata.create_all(engine)

    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
```

---

### Step 3: Frontend Setup (Next.js)

#### 3.1 Install Node.js Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Additional dependencies for Phase III
npm install @ai-sdk/openai ai  # For AI integration (if needed)
npm install axios              # For HTTP requests

# Return to project root
cd ..
```

#### 3.2 Configure Frontend Environment

Create `frontend/.env.local`:

```bash
# Frontend API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket endpoint (for streaming, Phase IV)
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

### Step 4: Start the Application

#### 4.1 Start Backend Server

```bash
# From project root
cd backend

# Activate virtual environment (if not already active)
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Verify Backend**:
- Open browser: http://localhost:8000/docs
- You should see FastAPI auto-generated documentation
- Look for `/api/chat` endpoint in the list

#### 4.2 Start Frontend Server

```bash
# Open new terminal window
# Navigate to frontend directory
cd frontend

# Start Next.js development server
npm run dev

# Expected output:
#   - Local:        http://localhost:3000
#   - Network:      http://192.168.1.100:3000
#
#   ✓ Ready in 2.3s
```

**Verify Frontend**:
- Open browser: http://localhost:3000
- You should see the Phase II Todo application
- Navigate to: http://localhost:3000/chat (or click "Chat" link in navigation)

---

## Testing the Chatbot

### Test 1: Create Task (English)

1. Open http://localhost:3000/chat
2. Log in with your Phase II account (or create new account)
3. In chat interface, type:
   ```
   Add a task to buy milk
   ```
4. Press Enter or click Send
5. **Expected Response**:
   ```
   ✅ Task 'Buy milk' has been added.
   ```
6. Verify task appears in Todo list

### Test 2: Create Task (Urdu)

1. In chat interface, type:
   ```
   دودھ لینے کا ٹاسک شامل کرو
   ```
   (Roman Urdu: "Doodh lene ka task add karo")
2. Press Enter or click Send
3. **Expected Response** (in Urdu):
   ```
   ✅ 'دودھ لینا' ٹاسک شامل ہو گیا ہے۔
   ```
4. Verify task appears in Todo list

### Test 3: List Tasks (English)

1. In chat interface, type:
   ```
   Show my tasks
   ```
2. **Expected Response**:
   ```
   Here are your tasks:
   1. Buy milk
   2. دودھ لینا
   ```

### Test 4: List Tasks (Urdu)

1. In chat interface, type:
   ```
   میرے ٹاسک دکھاؤ
   ```
2. **Expected Response** (in Urdu):
   ```
   آپ کے ٹاسک یہ ہیں:
   ۱. Buy milk
   ۲. دودھ لینا
   ```

### Test 5: Delete Task

1. In chat interface, type:
   ```
   Delete task 1
   ```
2. **Expected Response**:
   ```
   ✅ Task 'Buy milk' has been deleted.
   ```
3. Verify task removed from Todo list

### Test 6: Mark Task as Completed

1. In chat interface, type:
   ```
   Mark task 2 as done
   ```
2. **Expected Response**:
   ```
   ✅ Task 'دودھ لینا' marked as completed.
   ```
3. Verify task shows as completed in Todo list

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and install dependencies:
  ```bash
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

**Issue**: `connection refused` to Neon database
- **Solution**: Verify `NEON_DATABASE_URL` in `.env` file
- Check Neon project is active (not paused)

**Issue**: `401 Unauthorized` on `/api/chat`
- **Solution**: Verify JWT token is valid
- Check `JWT_SECRET` matches Phase II configuration

**Issue**: Hugging Face API timeout
- **Solution**: Verify `HUGGINGFACE_API_KEY` is valid
- Check internet connection
- Try again (API may be rate limited)

### Frontend Issues

**Issue**: Chat page shows 404
- **Solution**: Verify frontend is on branch `001-ai-chatbot`
- Check `frontend/src/pages/chat.tsx` exists

**Issue**: `CORS error` when calling `/api/chat`
- **Solution**: Verify backend CORS configuration includes frontend origin:
  ```python
  # backend/main.py
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

**Issue**: Chat not responding
- **Solution**: Open browser DevTools (F12) → Console tab
- Check for JavaScript errors
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Database Issues

**Issue**: `relation "conversation" does not exist`
- **Solution**: Run database migrations:
  ```bash
  python backend/scripts/migrate_ai_tables.py
  ```

**Issue**: Conversation not persisting
- **Solution**: Check database connection in backend logs
- Verify `NEON_DATABASE_URL` has `?sslmode=require` parameter

---

## Development Tips

### Hot Reload

- **Backend**: FastAPI auto-reloads on file changes (uvicorn `--reload` flag)
- **Frontend**: Next.js auto-reloads on file changes

### Debugging

**Backend Debugging**:
```bash
# Run with verbose logging
uvicorn main:app --reload --log-level debug

# Check logs for:
# - SQL queries
# - MCP tool calls
# - Hugging Face API requests
```

**Frontend Debugging**:
```bash
# Run Next.js in development mode
npm run dev

# Open browser DevTools (F12):
# - Console: JavaScript errors
# - Network: HTTP requests/responses
# - React DevTools: Component state
```

### Testing API Directly

**Using cURL**:
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test"}'
```

**Using FastAPI Swagger UI**:
- Open: http://localhost:8000/docs
- Find `/api/chat` endpoint
- Click "Try it out"
- Enter JWT token and message
- Click "Execute"

---

## Performance Tuning

### Backend Optimization

```python
# backend/main.py

# Increase worker count for production
workers = 4  # Adjust based on CPU cores

# Enable response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure database connection pool
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### Frontend Optimization

```javascript
// frontend/src/services/chat.ts

// Debounce user input (300ms)
import { debounce } from 'lodash';

const debouncedSendMessage = debounce(async (message) => {
  await sendMessage(message);
}, 300);
```

---

## Production Deployment

### Backend Deployment (Vercel/Render)

1. Set environment variables in deployment platform
2. Run migrations: `python backend/scripts/migrate_ai_tables.py`
3. Deploy FastAPI app
4. Verify `/api/docs` is accessible

### Frontend Deployment (Vercel)

```bash
# From frontend directory
npm run build
vercel deploy
```

### Environment Variables for Production

```bash
# Production .env
NEON_DATABASE_URL=postgresql://... (production Neon database)
HUGGINGFACE_API_KEY=hf_... (production API key)
JWT_SECRET=... (production JWT secret)
HOST=0.0.0.0
PORT=8000
RELOAD=false
```

---

## Next Steps

After successful setup:

1. **Explore the Code**:
   - `backend/src/services/chat_service.py` - Chat orchestration
   - `backend/src/services/mcp_server.py` - MCP tool server
   - `backend/src/api/chat.py` - Chat endpoint
   - `frontend/src/components/ChatInterface.tsx` - Chat UI

2. **Run Tests**:
   ```bash
   # Backend tests
   cd backend
   pytest tests/

   # Frontend tests
   cd frontend
   npm test
   ```

3. **Customize**:
   - Modify AI system prompt in `chat_service.py`
   - Add new MCP tools in `mcp_server.py`
   - Style chat UI in `ChatInterface.tsx`

4. **Contribute**:
   - Report issues on GitHub
   - Submit pull requests
   - Join discussions

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review Phase III spec: `specs/001-ai-chatbot/spec.md`
3. Check implementation plan: `specs/001-ai-chatbot/plan.md`
4. Open GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)

---

## Glossary

- **MCP**: Model Context Protocol - Standard for AI tool execution
- **JWT**: JSON Web Token - Authentication token
- **Neon**: Serverless PostgreSQL database provider
- **Qwen**: Multilingual AI model from Alibaba
- **Hugging Face**: AI model hosting platform
- **FastAPI**: Python web framework
- **Next.js**: React web framework
- **SQLModel**: Python ORM for SQLAlchemy

---

**Version**: 1.0.0
**Last Updated**: 2025-01-25
**Status**: Draft - Subject to change during implementation
