# 🚀 Deploy Phase 2 to HuggingFace Spaces

## Quick Deployment (3 steps)

### Step 1: Add HuggingFace Remote

Replace `YOUR_USERNAME` with your HuggingFace username:

```bash
cd hf-space
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend
```

### Step 2: Push to HuggingFace

```bash
git push space master
```

### Step 3: Configure Environment Variables

Go to your Space Settings → Variables and add:

```bash
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=your-jwt-secret-key-here
```

## That's it! Your Phase 2 backend will be live!

**Space URL:** `https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend`

**API Endpoints:**
- Health: `{space_url}/health`
- Auth: `{space_url}/api/auth/*`
- Todos: `{space_url}/api/todos/*`
- Users: `{space_url}/api/users/*`

## Notes:
- Code is ready in `hf-space/` directory
- Phase 2 commit: `0e4d4a2` (fix: add email-validator for pydantic)
- Dockerfile is configured
- Requirements.txt is complete
