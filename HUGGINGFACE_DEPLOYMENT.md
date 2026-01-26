# 🤖 HuggingFace Spaces Deployment Guide
## Phase III AI-Powered Todo Chatbot Backend

**Status:** ✅ Code ready for deployment
**Platform:** HuggingFace Spaces (Docker)
**Space Type:** Docker SDK

---

## 📋 Prerequisites

### Required:
- ✅ HuggingFace account
- ✅ GitHub repository
- ✅ HuggingFace API token: `YOUR_HF_TOKEN_HERE`
- ✅ Neon PostgreSQL database (or SQLite for testing)

---

## 🚀 Deployment Steps

### Option 1: Deploy via Web UI (Recommended)

#### Step 1: Create New Space
1. Go to: https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in details:
   - **Name:** `ai-todo-chatbot` (or your choice)
   - **License:** MIT
   - **SDK:** Docker
   - **Hardware:** CPU basic (free) ⚠️ **CPU upgrade**
   - **Visibility:** Public (recommended)

#### Step 2: Clone Repository
1. After creating space, you'll see: "Git clone" URL
2. Copy the git URL
3. In your terminal:
   ```bash
   cd hf-space
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
   git push space master
   ```

#### Step 3: Configure Environment Variables
1. Go to your Space Settings
2. Click **"Variables"** or **"Secrets"**
3. Add these variables:

```bash
# Required
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
HUGGINGFACE_API_KEY=YOUR_HF_TOKEN_HERE
JWT_SECRET=your-jwt-secret-key-here

# Optional
QWEN_MODEL=Qwen/Qwen-14B-Chat
```

#### Step 4: Deploy
- After pushing, HuggingFace will automatically:
  1. Build Docker image
  2. Deploy to container
  3. Start the server
  4. Your API will be live!

#### Step 5: Access Your Space
Your backend will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
```

API endpoints:
- **Chat API:** `{space_url}/api/chat`
- **Health:** `{space_url}/health`
- **Docs:** `{space_url}/docs`

---

### Option 2: Deploy via HuggingFace CLI

#### Step 1: Install HuggingFace CLI
```bash
pip install huggingface_hub
```

#### Step 2: Login
```bash
huggingface-cli login
```
Enter your token when prompted: `YOUR_HF_TOKEN_HERE`

#### Step 3: Create Space
```bash
huggingface-cli space create \
  --name ai-todo-chatbot \
  --sdk docker \
  --license mit
```

#### Step 4: Push Code
```bash
cd hf-space
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
git branch -M main
git push space main
```

---

## 🔧 Configuration

### Environment Variables (Required)

Add these in Space Settings:

```bash
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require
```
- Get free Neon database: https://neon.tech/
- Create project
- Copy connection string

```bash
HUGGINGFACE_API_KEY=YOUR_HF_TOKEN_HERE
```
- Your HuggingFace API token
- Has access to Qwen model

```bash
JWT_SECRET=your-jwt-secret-key-here
```
- Generate strong secret
- Example: `openssl rand -hex 32`

```bash
QWEN_MODEL=Qwen/Qwen-14B-Chat
```
- (Optional) Model to use
- Default: Qwen/Qwen-14B-Chat

---

## 📊 What's Deployed

### Backend Components:
✅ **FastAPI Application**
- Chat API endpoint (`/api/chat`)
- Health checks
- OpenAPI documentation

✅ **AI Integration**
- Qwen client (HuggingFace Inference API)
- Retry logic with exponential backoff
- Bilingual prompts (English/Urdu)

✅ **MCP Tools**
- `create_task` - Create new tasks
- `list_tasks` - List user's tasks
- `update_task` - Edit tasks
- `delete_task` - Remove tasks
- `complete_task` - Mark as done

✅ **Database Layer**
- TodoRepository (CRUD operations)
- ConversationRepository (chat history)
- User isolation enforced

✅ **Authentication**
- JWT verification middleware
- User ID extraction
- Protected routes

---

## 🧪 Testing Deployment

### 1. Check Health Endpoint
```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot/health
```

Expected response:
```json
{"status":"healthy","service":"phase-iii-chatbot","version":"1.0.0"}
```

### 2. Test Chat API
```bash
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Add a task to buy milk"
  }'
```

### 3. Check API Docs
Open in browser:
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot/docs
```

---

## 🔗 Connecting Frontend to HuggingFace Backend

### Update Frontend Environment Variable

**In Vercel Dashboard:**
1. Go to Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL`:
```bash
NEXT_PUBLIC_API_URL=https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
```
3. Redeploy frontend

**Or for local development:**
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
```

---

## 📈 Performance & Limits

### HuggingFace Spaces (Free Tier)
- **CPU:** 2 vCPUs
- **RAM:** 16 GB
- **Storage:** 20 GB
- **Bandwidth:** Unlimited (within reason)
- **Duration:** Always running
- **Cost:** $0/month

### For Better Performance:
Upgrade to:
- **CPU Basic Upgrade:** ~$0.10/hour
- **CPU Upgrade:** ~$0.60/hour
- More RAM, faster CPU

---

## 🐛 Troubleshooting

### Build Failed
- Check Dockerfile syntax
- Verify requirements.txt has all dependencies
- Check Space logs for errors

### Environment Variables Not Working
- Ensure variables are set in Space Settings
- Restart Space after adding variables
- Check variable names (no extra spaces)

### Database Connection Error
- Verify NEON_DATABASE_URL is correct
- Check database allows external connections
- Test connection string locally first

### 504 Gateway Timeout
- HuggingFace Spaces has timeout limits
- Long AI responses may timeout
- Consider upgrading hardware for better performance

### Import Errors
- Check Python version (3.12)
- Verify all files copied correctly
- Check module paths in imports

---

## 🔄 Updating Deployment

### Make Changes Locally
1. Edit code in `hf-space/`
2. Test locally
3. Commit changes
4. Push to HuggingFace:
   ```bash
   git add .
   git commit -m "update: description"
   git push space main
   ```
5. HuggingFace auto-rebuilds and redeploys

---

## 📊 Deployment Checklist

### Pre-Deployment:
- [ ] HuggingFace account created
- [ ] API token ready
- [ ] Neon database created
- [ ] JWT secret generated
- [ ] Code tested locally

### Deployment:
- [ ] Space created on HuggingFace
- [ ] Code pushed to Space
- [ ] Environment variables configured
- [ ] Docker build successful
- [ ] Server started without errors

### Post-Deployment:
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] Chat API responding
- [ ] MCP tools executing
- [ ] Frontend connected to backend

---

## 🎉 Success Metrics

✅ **Backend Live on HuggingFace**
✅ **API Accessible via HTTPS**
✅ **Health Checks Passing**
✅ **Chat Endpoint Functional**
✅ **AI Integration Working**
✅ **Database Connected**

---

## 📞 Support

### Documentation:
- HuggingFace Spaces Docs: https://huggingface.co/docs/hub/spaces
- Docker SDK Guide: https://huggingface.co/docs/hub/spaces-sdks-docker

### Space URL:
After deployment, your space will be at:
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-todo-chatbot
```

---

## 🚀 Ready to Deploy!

Your HuggingFace Space code is ready in `hf-space/` directory.

**Next Steps:**
1. Create Space on HuggingFace
2. Push code: `git push space main`
3. Configure environment variables
4. Access your live API!

---

**Status:** ✅ READY FOR DEPLOYMENT
**Platform:** HuggingFace Spaces (Docker)
**Cost:** FREE (with option to upgrade)

🤖 *Your AI-Powered Todo Chatbot backend will be live on HuggingFace!*
