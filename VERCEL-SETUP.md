# Vercel Environment Configuration Guide

## Required Environment Variables

### For Vercel Project (Frontend)

Use this code to configure:
```
vercel env add NEXT_PUBLIC_API_URL production
```

**Value:**
```
https://ammaraak/todo-app.hf.space
```

---

## Manual Setup Steps

### 1. Open Vercel Dashboard
```
https://vercel.com/ammar-ahmed-khans-projects-6b1515e7/frontend
```

### 2. Go to Settings → Environment Variables

### 3. Add/Edit Variable:
- **Name:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://ammaraak/todo-app.hf.space`
- **Environments:** Production, Preview, Development

### 4. Redeploy
After adding the variable, trigger a new deployment:
```
vercel --prod
```

Or click "Redeploy" in Vercel dashboard.

---

## Verification

After deployment, check the frontend:

1. Open browser DevTools (F12)
2. Run in console:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```

Expected output:
```
https://ammaraak/todo-app.hf.space
```

---

## Current Status

- ✅ Frontend code: Updated
- ✅ Backend: Deployed to HuggingFace
- ⚠️ Vercel Env Var: Needs manual update

---

*Last updated: 2026-01-29*
*Issue: Chatbot "not found" error*
