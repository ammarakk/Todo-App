# 🔑 **Quick Secrets Reference** - Phase 4

## ⚡ **5-Minute Setup**

### **Step 1: Generate JWT Secret**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output → Use for JWT_SECRET
```

### **Step 2: Get Database URL**
```bash
# Option A: Neon (Recommended - Free)
# 1. Go to https://neon.tech
# 2. Sign up → Create Project
# 3. Copy Connection String
# Format: postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Option B: Supabase (Free)
# 1. Go to https://supabase.com
# 2. New Project → Get Database URL
# Format: postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

# Option C: Railway (Free $5 Credit)
# 1. Go to https://railway.app
# 2. New Project → PostgreSQL
# 3. Copy Internal URL
```

### **Step 3: Add Secrets to Hugging Face**
```
URL: https://huggingface.co/spaces/ammaraak/todo-app-backend/settings

Add these 3 secrets:
─────────────────────────────────────────
QWEN_API_KEY      = [Your Qwen API key]
DATABASE_URL      = [Your Neon/Supabase URL]
JWT_SECRET        = [Generated from Step 1]
─────────────────────────────────────────

Click "Save and restart"
```

### **Step 4: Done!**
Wait 2-3 minutes → Your Space will restart → Ready! 🚀

---

## 📋 **Copy-Paste Secrets Template**

```
QWEN_API_KEY=0XA2TcDarwQtRtWP-uwkwY2L3PCkWHFuzQkxWyW1r2Xm58q5dR81tBuQSTAvW7AKppM8D0GRseYZb8AZ-cMtiQ
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
JWT_SECRET=[PASTE_GENERATED_SECRET_HERE]
```

---

## 🔐 **Security Checklist**

- [ ] JWT Secret generated (32+ chars)
- [ ] Database URL copied (Neon/Supabase)
- [ ] Qwen API key ready
- [ ] All 3 secrets added to Hugging Face
- [ ] Space restarted
- [ ] Test with chat message
- [ ] Check logs for errors

---

## 🆘 **Troubleshooting**

**Issue: Database connection failed**
```
Solution: Check DATABASE_URL format
Must start with: postgresql://
Must include: ?sslmode=require
```

**Issue: JWT error**
```
Solution: Generate new secret
Make sure it's 32+ characters
No special characters that need escaping
```

**Issue: Qwen API not working**
```
Solution: Check API key validity
Go to: https://dashscope.aliyuncs.com/
Verify key is active
```

---

## 📞 **Need Help?**

**Full Guide:** See `SECURITY-GUIDE.md`

**Links:**
- Neon DB: https://neon.tech
- Supabase: https://supabase.com
- Qwen Dashboard: https://dashscope.aliyuncs.com
- Hugging Face: https://huggingface.co/spaces/ammaraak/todo-app-backend

---

**⚠️ Remember: Never commit .env files!**
