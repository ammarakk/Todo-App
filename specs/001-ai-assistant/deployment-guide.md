# Phase 3 AI Assistant - Deployment Guide

**Branch**: 001-ai-chatbot
**Deployment Target**: Vercel (Frontend) + Hugging Face (Backend)
**Date**: 2026-01-28

---

## 📋 Pre-Deployment Checklist

### ✅ Code Quality
- [x] All Python files compile successfully
- [x] Frontend builds without errors (`npm run build`)
- [x] TypeScript type checking passes
- [x] No blocking console errors
- [x] All imports resolved

### ✅ Features Implemented
- [x] AI chat endpoint: `/api/ai-chat/command`
- [x] JWT authentication on all endpoints
- [x] Input sanitization (HTML/SQL injection prevention)
- [x] MCP tools: 7 tools (create, list, update, delete, complete, search, bulk_complete)
- [x] Frontend: Floating AI chat panel integrated in Dashboard
- [x] Conversation history persistence
- [x] Real-time state sync (AI → UI)

### ✅ Security
- [x] JWT required on all AI endpoints
- [x] User isolation enforced (user_id from token, not input)
- [x] Input sanitization implemented
- [x] No direct database access from AI
- [x] MCP tools call existing Todo APIs

---

## 🚀 Deployment Steps

### Step 1: Create Feature Branch (T052)

```bash
# Ensure we're on the correct branch
git checkout 001-ai-chatbot

# Pull latest changes
git pull origin 001-ai-chatbot

# Verify branch status
git status
```

### Step 2: Review Changes Before Commit

```bash
# View staged changes
git diff --cached

# View all changes
git diff

# View commit history
git log --oneline -10
```

### Step 3: Commit Frontend Changes (T053)

```bash
cd frontend

# Stage frontend changes
git add src/components/ai-assistant/
git add src/app/dashboard/page.tsx
git add src/app/layout.tsx
git add src/lib/api.ts
git add src/components/ChatWidgetProvider.tsx  # deleted
git add src/components/FloatingChatWidget.tsx  # deleted

# Commit frontend changes
git commit -m "feat: integrate AI chat into Dashboard

- Add floating AI chat button and panel
- Implement useAIChat hook with state management
- Add ChatMessage component with task list display
- Add ChatInput component with send functionality
- Integrate AI chat into Dashboard page
- Add conversation history persistence (localStorage)
- Add AI command API methods (sendCommand, loadConversation)
- Remove unused Phase 2 chat widget files
- Fix export naming conflicts

Phase 3: AI Assistant Integration
Tasks: T019-T029 (11 frontend tasks)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 4: Commit Backend Changes (T054)

```bash
cd ../backend

# Stage backend changes
git add src/api/chat.py
git add src/main.py
git add src/mcp/tools.py
git add src/repositories/todo_repository.py

# Commit backend changes
git commit -m "feat: add AI command endpoint with advanced MCP tools

- Add POST /api/ai-chat/command endpoint
- Implement input sanitization (HTML/SQL injection prevention)
- Add AI command request/response schemas
- Integrate Qwen client with conversation history
- Add action mapping for all Todo operations
- Add performance logging
- Add search_tasks MCP tool (keyword search)
- Add bulk_complete MCP tool (batch operations)
- Add search and bulk_complete methods to TodoRepository
- Update tool_to_action mapping with new actions

Phase 3: AI Assistant Integration
Tasks: T005-T018, T030-T041 (backend tasks)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 5: Push Branch to Remote (T055)

```bash
# Push both frontend and backend commits
git push origin 001-ai-chatbot

# Verify push succeeded
git log --oneline -5
```

---

## 🌐 Frontend Deployment (T056-T058)

### Step 6: Build Frontend for Production

```bash
cd frontend

# Install dependencies (if needed)
npm install

# Build for production
npm run build

# Verify build output
ls -la .next/
```

**Expected Output:**
```
✓ Compiled successfully
✓ Generating static pages (9/9)
✓ Finalizing page optimization
Route (app)                    Size     First Load JS
┌ ○ /dashboard                19.6 kB    184 kB
```

### Step 7: Deploy to Vercel

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login to Vercel (if not logged in)
vercel login

# Deploy to production
vercel --prod

# Note the deployment URL
```

**Or use Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select project: `todo-app-new`
3. Click "Deploy"
4. Connect GitHub repository
5. Select branch: `001-ai-chatbot`
6. Deploy

### Step 8: Verify Frontend Deployment (T058)

```bash
# Test the deployed URL
curl -I https://your-app.vercel.app

# Open in browser
# Expected: Login page loads, no console errors
```

**Manual Checks:**
- [ ] Homepage loads without errors
- [ ] Login page works
- [ ] Dashboard loads after login
- [ ] AI chat button visible (bottom-right)
- [ ] Click AI chat button → Panel opens
- [ ] No console errors (F12 → Console)
- [ ] Network requests succeed (F12 → Network)

---

## 🔧 Backend Deployment (T059-T060)

### Step 9: Update Backend on Hugging Face

**Option A: Git Push (Recommended)**

```bash
# Hugging Face Space should be connected to this branch
# Just push and Hugging Face will auto-redeploy

git push origin 001-ai-chatbot
git push hf main  # If Hugging Face remote is named 'hf'
```

**Option B: Manual Upload**

1. Go to Hugging Face Space: `https://huggingface.co/spaces/your-space`
2. Click "Files" → "Upload files"
3. Upload backend files:
   - `src/api/chat.py`
   - `src/main.py`
   - `src/mcp/tools.py`
   - `src/repositories/todo_repository.py`

**Option C: Via Space UI**

1. Go to Settings → Git
2. Update branch to `001-ai-chatbot`
3. Click "Update and Restart"

### Step 10: Verify Backend Deployment (T060)

```bash
# Test health endpoint
curl https://your-space.huggingface.co/health

# Expected output:
# {"status":"healthy","api":"Todo App API","version":"0.1.0"}

# Test AI chat endpoint (requires JWT)
curl -X POST https://your-space.huggingface.co/api/ai-chat/command \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message":"Show my tasks","conversationId":"new"}'
```

**Manual Checks:**
- [ ] Health endpoint returns 200
- [ ] API docs accessible at `/docs`
- [ ] AI endpoint requires JWT (401 without token)
- [ ] AI endpoint processes commands
- [ ] Logs show no errors (Hugging Face Logs tab)

---

## ✅ Post-Deployment Verification (Phase 8)

### Step 11: Full Integration Test (T061-T068)

**Test 1: Todo via UI (T061)**
```bash
1. Login to dashboard
2. Create task: "Test task via UI"
3. Verify task appears in list
4. Edit task → Verify changes
5. Delete task → Verify removed
```

**Test 2: Todo via AI (T062)**
```bash
1. Open AI chat
2. Type: "Create task AI test"
3. Type: "Show my tasks"
4. Verify "AI test" task appears
5. Type: "Mark task 1 complete"
6. Type: "Delete task 1"
7. Verify all operations work
```

**Test 3: Auth Stability (T063)**
```bash
1. Login
2. Wait 10 minutes
3. Use AI chat
4. Verify still authenticated
5. Check JWT not expired
```

**Test 4: Security Enforcement (T064)**
```bash
1. Open DevTools → Network
2. Call API without JWT
3. Expected: 401 Unauthorized
4. Try to access other user's tasks
5. Expected: User isolation enforced
```

**Test 5: Runtime Errors (T065)**
```bash
1. Open DevTools → Console
2. Use AI chat for 5 minutes
3. Create/edit/delete tasks
4. Expected: No red errors
5. Expected: No uncaught exceptions
```

**Test 6: Performance (T066)**
```bash
1. Open DevTools → Network
2. Send AI command: "Show my tasks"
3. Measure response time
4. Expected: <3 seconds
5. Create task via AI
6. Expected: Appears in UI within 10 seconds
```

**Test 7: Documentation (T067-T068)**
```bash
1. Check README.md updated with AI commands
2. Check API docs at /docs include /api/ai-chat/command
3. Verify examples are accurate
```

---

## 📝 Environment Variables

### Frontend (.env.local / .env.production)
```bash
NEXT_PUBLIC_API_URL=https://your-space.huggingface.co
```

### Backend (Hugging Face Secrets)
```bash
NEON_DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
HF_API_KEY=your-huggingface-key
QWEN_API_KEY=your-qwen-key
```

---

## 🔄 Rollback Plan

If deployment fails:

### Frontend Rollback
```bash
# Revert to previous commit
git revert HEAD

# Or checkout previous deployment
vercel rollback --to=<deployment-url>
```

### Backend Rollback
```bash
# Revert backend commits
git revert HEAD

# Push to Hugging Face
git push hf main
```

---

## 📊 Deployment Summary

**Files Modified:**
- Frontend: 6 files (5 added, 1 removed)
- Backend: 4 files (all modified)

**New Components:**
- AIChatButton, AIChatPanel, ChatMessage, ChatInput, useAIChat

**New Endpoints:**
- POST /api/ai-chat/command

**New MCP Tools:**
- search_tasks, bulk_complete

**Total Lines Changed:**
- Frontend: ~800 lines added
- Backend: ~300 lines added

**Deployment Status:** ⏳ Ready for deployment

---

## ✅ Final Checklist

Before going live, ensure:

- [ ] All automated tests pass
- [ ] Manual browser testing complete (Phase 6)
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Hugging Face
- [ ] Health checks pass
- [ ] AI commands work end-to-end
- [ ] No console errors
- [ ] Performance targets met
- [ ] Documentation updated
- [ ] Rollback plan tested

**Once all checked:**
```
🎉 Phase 3 AI Assistant Integration COMPLETE!
```
