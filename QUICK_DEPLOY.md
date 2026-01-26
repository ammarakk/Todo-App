# 🚀 Auto-Deploy Phase 2 to HuggingFace Spaces
## Just copy and run these commands!

## Step 1: Add HuggingFace Remote

```bash
cd hf-space
```

```bash
git remote add space https://huggingface.co/spaces/ammarakk/todo-app-backend
```

*(If username is different, replace `ammarakk` with your username)*

## Step 2: Push to HuggingFace

```bash
git push space master
```

## Step 3: Open Your Space

After push completes, open:
```
https://huggingface.co/spaces/ammarakk/todo-app-backend
```

## Step 4: Configure Environment Variables

In Space Settings → Variables, add:

```bash
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
```

```bash
JWT_SECRET=your-jwt-secret-key-here
```

## Step 5: Deploy Complete!

Your backend will be live at:
```
https://ammarakk-todo-app-backend.hf.space
```

---

## ✅ What's Deployed:

**Phase 2 Backend:**
- ✅ FastAPI application
- ✅ Authentication (JWT)
- ✅ Todo CRUD API
- ✅ User management
- ✅ Database models
- ✅ PostgreSQL integration

**API Endpoints:**
- `/health` - Health check
- `/api/auth/*` - Authentication
- `/api/todos/*` - Todo management
- `/api/users/*` - User management
- `/docs` - API documentation

---

## 🎯 Done!

That's it! Your Phase 2 backend is live on HuggingFace Spaces!
