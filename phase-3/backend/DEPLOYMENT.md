# 🚀 Hugging Face Spaces Deployment Guide

Complete guide to deploy your Todo App Backend to Hugging Face Spaces.

## 📋 Prerequisites

- Hugging Face account (free at [huggingface.co](https://huggingface.co))
- Neon PostgreSQL database (free at [neon.tech](https://neon.tech))
- (Optional) Cloudinary account for avatar uploads

## 🔑 Step 1: Get Your Hugging Face API Token

This token allows your app to use Hugging Face AI models:

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Fill in:
   - **Token name**: `todo-app-backend`
   - **Token type**: Select **"Read"** (for accessing public AI models)
4. Click **"Generate token"**
5. **Copy the token immediately** (starts with `hf_`)
   - Example: `hf_abc123xyz456def789ghi012`

⚠️ **Save this token** - you won't see it again!

## 🗄️ Step 2: Setup Neon PostgreSQL Database

1. Go to [https://neon.tech](https://neon.tech)
2. Sign up/login (free tier is sufficient)
3. Click **"Create a project"**
4. Choose a name (e.g., `todo-app-db`)
5. Select the closest region
6. Click **"Create project"**
7. Copy the **Connection string** from the dashboard
   - Format: `postgresql+psycopg://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require`

## 🌐 Step 3: Create Hugging Face Space

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `todo-app-backend` (or your preferred name)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU basic (free tier)
4. Click **"Create Space"**

## 📦 Step 4: Upload Your Code

### Option A: Using Git (Recommended)

```bash
# Navigate to backend directory
cd backend

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit for Hugging Face Spaces"

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend

# Push to Hugging Face
git push hf main
```

Replace `YOUR_USERNAME` with your Hugging Face username.

### Option B: Using Web Interface

1. Go to your Space page
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload these files:
   - `Dockerfile`
   - `README.md`
   - `requirements.txt`
   - `src/` folder (entire directory)
   - `alembic/` folder (for migrations)

## 🔐 Step 5: Configure Environment Variables

1. Go to your Space page
2. Click **"Settings"** tab
3. Scroll to **"Variables"** section
4. Click **"New variable"** for each:

| Variable Name | Value |
|---------------|-------|
| `DATABASE_URL` | Your Neon connection string |
| `JWT_SECRET` | Generate a secure random string (min 32 chars) |
| `HUGGINGFACE_API_KEY` | The token you got in Step 1 |
| `CLOUDINARY_CLOUD_NAME` | Your Cloudinary cloud name (optional) |
| `CLOUDINARY_API_KEY` | Your Cloudinary API key (optional) |
| `CLOUDINARY_API_SECRET` | Your Cloudinary API secret (optional) |
| `FRONTEND_URL` | Your Vercel frontend URL |
| `CORS_ORIGINS` | `["https://your-frontend.vercel.app"]` |
| `ENV` | `production` |
| `PORT` | `7860` |
| `LOG_LEVEL` | `info` |

### Generate JWT_SECRET

Run this in Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use any online random string generator (min 32 characters).

## 🔄 Step 6: Deploy and Monitor

1. After adding variables, Hugging Face will automatically rebuild
2. Click **"Logs"** tab to see deployment progress
3. Wait for "Space is building" to change to "Space is running"
4. Your API will be available at: `https://YOUR_USERNAME-todo-app-backend.hf.space`

## ✅ Step 7: Test Your Deployment

### Health Check
```bash
curl https://YOUR_USERNAME-todo-app-backend.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "api": "Todo App API",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected"
}
```

### API Documentation
Visit: `https://YOUR_USERNAME-todo-app-backend.hf.space/docs`

## 🔧 Troubleshooting

### Build Fails
- Check **Logs** tab for specific errors
- Ensure all files are uploaded (especially `Dockerfile`)
- Verify environment variables are set correctly

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Ensure IP allowlisting (if Neon requires)
- Check SSL mode: add `?sslmode=require` if needed

### Port Issues
- Ensure `PORT` variable is set to `7860`
- Dockerfile must expose port 7860

### AI Features Not Working
- Verify `HUGGINGFACE_API_KEY` starts with `hf_`
- Check token has **Read** permissions
- Test token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## 📊 Monitoring

- **Logs**: Real-time build and runtime logs
- **Settings**: Update variables without rebuilding
- **SDK Info**: View resource usage and status

## 🎉 Success!

Your backend is now live on Hugging Face Spaces! 🚀

Next steps:
- Connect your frontend (update API base URL)
- Set up custom domain (optional)
- Configure monitoring alerts

## 📝 Useful URLs

- Your Space: `https://huggingface.co/spaces/YOUR_USERNAME/todo-app-backend`
- Live API: `https://YOUR_USERNAME-todo-app-backend.hf.space`
- API Docs: `https://YOUR_USERNAME-todo-app-backend.hf.space/docs`
- Health: `https://YOUR_USERNAME-todo-app-backend.hf.space/health`

---

**Need help?** Check [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
