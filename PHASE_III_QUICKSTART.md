# Phase III Quick Start Guide
## AI-Powered Todo Chatbot

Get up and running in 5 minutes! ⚡

---

## 🚀 Quick Start

### Prerequisites Checklist

- [ ] Python 3.12+ installed
- [ ] Node.js 18+ installed
- [ ] Neon PostgreSQL account (free at https://neon.tech/)
- [ ] Hugging Face API key (free at https://huggingface.co/)
- [ ] Git installed

---

## Step 1: Setup Environment (2 minutes)

### Backend `.env`

```bash
# In project root, create .env file:
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
HUGGINGFACE_API_KEY=hf_your_api_key_here
QWEN_MODEL=Qwen/Qwen-14B-Chat
JWT_SECRET=your-jwt-secret-here
```

### Frontend `.env.local`

```bash
# In frontend/, create .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 2: Install Dependencies (1 minute)

```bash
# Python dependencies
pip install -r requirements.txt

# Node dependencies
cd frontend
npm install
cd ..
```

---

## Step 3: Setup Database (30 seconds)

```bash
python backend/scripts/migrate_ai_tables.py
```

Expected output:
```
[OK] Checking database connection...
[OK] Creating Conversation table...
[OK] Creating Message table...
[OK] Migration complete!
```

---

## Step 4: Start Backend (30 seconds)

```bash
# Terminal 1
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify it's running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"...}
```

---

## Step 5: Start Frontend (30 seconds)

```bash
# Terminal 2
cd frontend
npm run dev
```

Open: http://localhost:3000/chat

---

## Step 6: Test the Chat! (1 minute)

### Login First
1. Go to http://localhost:3000/login
2. Enter your Phase II credentials
3. You'll be redirected to chat

### Try These Commands

**English:**
```
Add a task to buy milk
Show my tasks
Mark task 1 as complete
```

**Urdu:**
```
دودھ لینے کا ٹاسک شامل کرو
میرے ٹاسک دکھاؤ
پہلا ٹاسک مکمل کرو
```

---

## 🎯 What's Happening?

### Architecture

```
You (Frontend)
    ↓ "Add a task to buy milk"
    ↓ (JWT + HTTP)
Backend (/api/chat)
    ↓ Extract user_id
    ↓ Detect language (English)
    ↓ Send to Qwen AI
    ↓ AI responds: TOOL_CALL create_task
    ↓ Execute MCP tool
    ↓ Create task in database
    ↓ Format response
    ↓ Return: "Task created!"
You (Frontend)
    ↓ Display response
```

### Components

**Frontend:**
- `ChatInterfaceAdvanced.tsx` - Beautiful chat UI
- `RobotAvatar.tsx` - Animated robot
- `/chat` page - Main chat interface

**Backend:**
- `/api/chat` - Main chat endpoint
- `QwenClient` - Hugging Face integration
- `MCPTools` - Task operations
- `TodoRepository` - Database access

---

## 📝 Common Commands

### Backend

```bash
# Start server
python -m uvicorn backend.main:app --reload

# Run migration
python backend/scripts/migrate_ai_tables.py

# Test chat endpoint
curl http://localhost:8000/api/chat/health

# View API docs
open http://localhost:8000/docs
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

---

## 🐛 Troubleshooting

### "Port 8000 already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### "Database connection failed"

Check your `.env` file has correct `NEON_DATABASE_URL`

### "JWT token invalid"

1. Logout from frontend
2. Login again with Phase II credentials
3. New token will be generated

### "Hugging Face API error"

Verify:
- API key is correct
- Model name: `Qwen/Qwen-14B-Chat`
- Account has API access enabled

---

## 📊 Test Cases

### Test 1: Create Task (English)

**Input:** `Add a task to finish the project with high priority`

**Expected:**
- AI responds in English
- Task created with title "finish the project"
- Priority set to "high"
- Confirmation message displayed

### Test 2: Create Task (Urdu)

**Input:** `گھر پر جا задача`

**Expected:**
- AI responds in Urdu
- Task created with Urdu title
- Confirmation in Urdu

### Test 3: View Tasks

**Input:** `Show my tasks`

**Expected:**
- AI lists all your tasks
- Shows status, priority, due dates
- Response in detected language

### Test 4: Complete Task

**Input:** `Mark task 1 as done`

**Expected:**
- Task status changed to "completed"
- Completion timestamp set
- Confirmation message

---

## 🎨 Features Available

✅ **Bilingual Support** - English & Urdu
✅ **Natural Language** - No special commands needed
✅ **Task CRUD** - Create, Read, Update, Delete
✅ **Priorities** - Low, Medium, High
✅ **Due Dates** - ISO format supported
✅ **Tags** - Categorize tasks
✅ **Animated Robot** - Cute AI avatar
✅ **Chat History** - Conversations saved
✅ **Dark Mode** - Beautiful dark theme

---

## 🚀 Next Steps

1. **Customize Prompts:** Edit `backend/src/ai/prompt_builder.py`
2. **Add More Tools:** Create new MCP tools in `backend/src/mcp/tools.py`
3. **Style Customization:** Modify `frontend/src/styles/globals.css`
4. **Deploy:** Follow `PHASE_III_DEPLOYMENT.md`

---

## 📚 Full Documentation

- **Deployment Guide:** `PHASE_III_DEPLOYMENT.md`
- **Specification:** `specs/001-ai-chatbot/spec.md`
- **Implementation Plan:** `specs/001-ai-chatbot/plan.md`
- **Task List:** `specs/001-ai-chatbot/tasks.md`

---

## 💡 Tips

1. **Start Simple:** Try basic commands first
2. **Be Specific:** More details = better AI understanding
3. **Mix Languages:** AI detects language automatically
4. **Use Conversations:** AI remembers context (10 messages)
5. **Check Logs:** Backend logs show tool executions

---

**🎉 You're ready to use the AI-Powered Todo Chatbot!**

**Time to complete:** ~5 minutes
**Difficulty:** Beginner-friendly
**Support:** Check `PHASE_III_DEPLOYMENT.md` for detailed troubleshooting
