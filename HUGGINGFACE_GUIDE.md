# 🚀 HuggingFace Deployment - Complete Guide
## Phase 2 Backend Deployment

---

## Method 1: Web UI (Easiest) - RECOMMENDED

### Step 1: Create Space on HuggingFace

1. **Go to:** https://huggingface.co/spaces

2. **Click:** "Create new Space"

3. **Fill in:**
   - **Owner:** ammarakk (your username)
   - **Space name:** `todo-app-backend`
   - **SDK:** Docker
   - **License:** MIT
   - **Hardware:** CPU basic (free) ⚠️
   - **Visibility:** Public

4. **Click:** "Create Space"

### Step 2: Get Git URL

After creating, you'll see a section like:
```
Git clone
git clone https://huggingface.co/spaces/ammarakk/todo-app-backend
```

### Step 3: Push Code

Open terminal in project directory:
```bash
cd hf-space
git remote add space https://huggingface.co/spaces/ammarakk/todo-app-backend
git push space master
```

### Step 4: Configure Environment Variables

1. Go to your Space page
2. Click "Settings" → "Repository secrets" or "Variables"
3. Add these secrets:

**Secret 1:**
- Name: `NEON_DATABASE_URL`
- Value: `postgresql://neondb_owner:npg_ChtFeYRd02nq@ep-lucky-meadow-abpkcyn6-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

**Secret 2:**
- Name: `JWT_SECRET`
- Value: `your-jwt-secret-key-here`

4. Click "Save" / "Update"

### Step 5: Restart Space

After adding secrets:
- Click "Settings" → "Factory restart"
- Space will rebuild with new environment variables

### Step 6: Access Your Backend!

Your backend will be live at:
```
https://huggingface.co/spaces/ammarakk/todo-app-backend
```

Or:
```
https://ammarakk-todo-app-backend.hf.space
```

**API Endpoints:**
- Health: `{space_url}/health`
- Auth: `{space_url}/api/auth/*`
- Todos: `{space_url}/api/todos/*`
- Docs: `{space_url}/docs`

---

## Method 2: CLI (If you have huggingface-cli)

### Step 1: Install CLI
```bash
pip install huggingface_hub
```

### Step 2: Login
```bash
huggingface-cli login
```
Enter token: `YOUR_HF_TOKEN_HERE`

### Step 3: Create Space
```bash
huggingface-cli space create \
  --name todo-app-backend \
  --sdk docker \
  --license mit
```

### Step 4: Push Code
```bash
cd hf-space
git remote add space https://huggingface.co/spaces/ammarakk/todo-app-backend
git push space master
```

### Step 5: Configure Secrets
Go to web UI and add environment variables (see Step 4 in Method 1)

---

## ✅ Verification Commands

After deployment, test these:

```bash
# Health check
curl https://huggingface.co/spaces/ammarakk/todo-app-backend/health

# API docs (open in browser)
# https://huggingface.co/spaces/ammarakk/todo-app-backend/docs
```

---

## 🔗 Connecting Frontend

Once backend is live, update frontend:

**In Vercel Dashboard:**
1. Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL`:
   ```bash
   NEXT_PUBLIC_API_URL=https://ammarakk-todo-app-backend.hf.space
   ```
3. Redeploy frontend

**OR Locally:**
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://ammarakk-todo-app-backend.hf.space
```

---

## 🎯 Summary

**What You Need:**
1. Create space on HuggingFace (web UI)
2. Push code (1 command)
3. Add environment variables (2 secrets)
4. Restart space

**Total Time:** 5 minutes

**Backend Live At:**
```
https://ammarakk-todo-app-backend.hf.space
```

---

## 🎉 Full-Stack Status

After completing this:

✅ **Frontend:** Vercel (LIVE)
✅ **Backend:** HuggingFace (LIVE after steps above)
✅ **Database:** Neon (Connected)
✅ **AI:** Qwen + HuggingFace (Ready)

**Your AI-Powered Todo Chatbot will be FULLY LIVE!** 🚀
