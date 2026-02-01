# 🔐 Security Guide - Phase 4 Todo App

## ⚠️ **CRITICAL SECURITY RULES**

### ✅ **DO:**
- ✅ Use environment variables for ALL secrets
- ✅ Never commit .env files to git
- ✅ Use .env.example for documentation only
- ✅ Rotate API keys regularly
- ✅ Use different keys for dev/prod
- ✅ Enable HTTPS everywhere
- ✅ Use strong JWT secrets

### ❌ **DON'T:**
- ❌ Never hardcode API keys in code
- ❌ Never commit secrets to GitHub
- ❌ Never share .env files
- ❌ Never use production keys in development
- ❌ Never expose secrets in logs
- ❌ Never use weak passwords

---

## 🔑 **Required Secrets & Where to Add Them**

### 1. **Qwen API Key**
**Purpose:** AI chatbot intent extraction
**Where to get:** https://dashscope.aliyuncs.com/

**Add to:**
- Hugging Face: Settings → Variables → `QWEN_API_KEY`
- Local: `phase-4/apps/chatbot/.env` (gitignored)

**Format:** `sk-xxxxxxxxxxxxxxxxxxxxxxxx`

---

### 2. **Database URL (PostgreSQL)**
**Purpose:** Connect to PostgreSQL database

**Free Options:**
- Neon: https://neon.tech (recommended)
- Supabase: https://supabase.com
- Railway: https://railway.app

**Add to:**
- Hugging Face: Settings → Variables → `DATABASE_URL`
- Local: `phase-4/apps/chatbot/.env`

**Format:** `postgresql://user:password@host:5432/dbname`

---

### 3. **JWT Secret**
**Purpose:** Sign and verify JWT tokens for authentication

**Generate a strong secret:**
```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Online
# https://generate-secret.vercel.app/32
```

**Add to:**
- Hugging Face: Settings → Variables → `JWT_SECRET`
- Local: `phase-4/apps/chatbot/.env`

**Format:** Long random string (32+ chars)

---

## 🌐 **Platform-Specific Security Setup**

### **Hugging Face Spaces**
```
URL: https://huggingface.co/spaces/ammaraak/todo-app-backend/settings

Steps:
1. Go to Settings → Variables
2. Add each secret:
   - Name: QWEN_API_KEY
     Value: your-actual-key
   - Name: DATABASE_URL
     Value: postgresql://...
   - Name: JWT_SECRET
     Value: your-generated-secret

3. Make sure "Repository Visibility" is set correctly (Public/Private)
```

### **Vercel**
```
URL: https://vercel.com/ammarakk/project-name/settings/environment-variables

Steps:
1. Go to Settings → Environment Variables
2. Add:
   - NEXT_PUBLIC_BACKEND_URL (Public)
     Value: https://ammaraak-todo-app-backend.hf.space

3. DO NOT add private secrets here (frontend only)
```

### **Local Development**
```bash
# Create .env file (gitignored)
cd phase-4/apps/chatbot
cp .env.example .env

# Edit .env with your secrets
nano .env  # or use code editor

# Start services
docker-compose up
```

---

## 🔒 **Best Practices**

### 1. **Environment Variable Naming**
```bash
# ✅ Good - Clear, specific
QWEN_API_KEY
DATABASE_URL
JWT_SECRET

# ❌ Bad - Vague
API_KEY
DB
SECRET
```

### 2. **Secret Rotation**
```bash
# Rotate secrets every 90 days
# Schedule:
- Qwen API Key: Every 3 months
- JWT Secret: Every 6 months
- Database Password: Every 3 months
```

### 3. **Access Control**
```bash
# Limit who can access secrets
- Only YOU should have production keys
- Use separate keys for dev/staging/prod
- Never share .env files via chat/email
- Use password managers (1Password, Bitwarden)
```

### 4. **Monitoring**
```bash
# Regularly check:
- GitHub commits for secrets (use git-secrets)
- Hugging Face logs for API usage
- Vercel logs for errors
```

---

## 🛡️ **Security Checklist**

### **Before Deploying:**
- [ ] All .env files in .gitignore
- [ ] No secrets in code (grep -r "sk-" .)
- [ ] .env.example files updated (no real values)
- [ ] Strong JWT secret generated
- [ ] HTTPS enabled everywhere
- [ ] CORS properly configured
- [ ] Rate limiting enabled (if applicable)

### **After Deploying:**
- [ ] Secrets added to platform (HF, Vercel)
- [ ] Test API with invalid key (should fail)
- [ ] Check logs for exposed secrets
- [ ] Monitor API usage
- [ ] Set up alerts for unusual activity

---

## 🚨 **If Secrets Are Leaked**

### **Immediate Actions:**
```bash
1. Rotate the compromised key immediately
2. Check usage logs
3. Inform affected users
4. Update all platforms
5. Commit changes with new secrets
6. Force re-deployment
```

### **Rotation Commands:**
```bash
# Qwen API: Generate new key at dashboard
# JWT: Generate new secret using python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update platforms:
# - Hugging Face: Settings → Variables → Edit
# - Vercel: Settings → Environment Variables → Edit

# Re-deploy:
git commit --allow-empty -m "Rotate secrets"
git push origin phase-4
```

---

## 📚 **Resources**

### **Secrets Management:**
- 1Password: https://1password.com
- Bitwarden: https://bitwarden.com
- HashiCorp Vault: https://vaultproject.io

### **Secret Scanning:**
- git-secrets: https://github.com/awslabs/git-secrets
- TruffleHog: https://trufflesecurity.com/trufflehog

### **Security Testing:**
- OWASP ZAP: https://www.zaproxy.org
- Snyk: https://snyk.io

---

## 📞 **Contact**

If you suspect a security breach:
1. Immediately rotate all keys
2. Check logs for unauthorized access
3. Contact platform support (HF, Vercel, Qwen)

---

**Remember:** Security is ongoing, not one-time! 🔒

**Last Updated:** 2026-02-01
