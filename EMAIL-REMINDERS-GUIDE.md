# 📧 Email Reminder System - Setup Guide

## ✅ Feature Complete!

Email reminders have been successfully added to your Todo App. Here's how to set them up.

---

## 🎯 What This Feature Does

- **Automatically sends reminder emails** to users 1 day before their task's due date
- **Sends to user's login email** (the email they used to sign up)
- **Only for tasks with due dates** set
- **Includes full task details** in the email:
  - Task title
  - Task description
  - Due date and time
  - Priority level (High/Medium/Low)
  - Tags
  - Time remaining

---

## 📧 How to Setup Gmail SMTP

### Step 1: Enable 2-Step Verification

1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification" and enable it (if not already enabled)
3. Follow the prompts to set it up

### Step 2: Generate App Password

1. On the same security page, search for "App Passwords"
2. Click on it (you may need to sign in again)
3. Select:
   - **App**: Select "Mail"
   - **Device**: Select "Other (Custom name)"
4. Enter "Todo App" as the name
5. Click **Generate**
6. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
7. **Save it securely** - you won't see it again!

### Step 3: Add to Backend Environment Variables

**For Local Development:**

Edit `backend/.env` and add:
```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

**For Hugging Face Space (Production):**

Add these secrets via Hugging Face API or web UI:
```bash
# Via Hugging Face CLI
huggingface-cli login
# Then add secrets via web UI at:
# https://huggingface.co/spaces/ammaraak/todo-app/settings
```

Add these two secrets:
- `GMAIL_EMAIL`: Your Gmail address
- `GMAIL_APP_PASSWORD`: The 16-character app password

---

## 🗄️ Database Migration

### Apply Migration to Add `reminder_sent` Column

**For Local Database:**
```bash
cd backend
python -m alembic upgrade head
```

**For Hugging Face Production Database:**
The migration will run automatically when the space rebuilds.

**What this does:**
- Adds `reminder_sent` column to `todos` table
- Sets default value to `False` for existing tasks
- Tracks whether reminder email has been sent for each task

---

## 🚀 How to Run

### Local Development

1. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables in `.env`:**
   ```bash
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   NEON_DATABASE_URL=your-database-url
   JWT_SECRET=your-jwt-secret
   # ... other env vars
   ```

3. **Apply database migration:**
   ```bash
   python -m alembic upgrade head
   ```

4. **Run the backend:**
   ```bash
   python -m uvicorn src.main:app --reload --port 8801
   ```

5. **Check startup logs:**
   Look for:
   ```
   ✅ Reminder scheduler started (runs every hour)
   ```

   If you see:
   ```
   ⚠️  Reminder scheduler disabled (Gmail not configured)
   ```
   Then your Gmail credentials are missing or incorrect.

### Production (Hugging Face Space)

1. **Add secrets to Hugging Face Space:**
   - `GMAIL_EMAIL`
   - `GMAIL_APP_PASSWORD`
   - `NEON_DATABASE_URL`
   - `JWT_SECRET`
   - `QWEN_API_KEY`

2. **Push to Hugging Face:**
   ```bash
   cd hf-space
   git add .
   git commit -m "feat: add email reminder system"
   git push
   ```

3. **Wait for rebuild** (~5 minutes)

4. **Check logs:**
   - Go to https://huggingface.co/spaces/ammaraak/todo-app
   - Click "Logs" or "Settings"
   - Look for "✅ Reminder scheduler started"

---

## 📱 How to Use

### For Users

1. **Create a task with a due date:**
   - Login to the app
   - Click "Create New Todo"
   - Fill in title, description
   - **Select a due date**
   - You'll see: "🔔 Reminder email will be sent 1 day before"

2. **The reminder indicator:**
   - In the todo list, tasks with due dates show a 🔔 icon
   - This means reminder is scheduled
   - After reminder is sent, the icon disappears

3. **Receive the email:**
   - 1 day before the due date, check your email
   - You'll get a beautiful HTML email with:
     - Task title
     - Full description
     - Due date and time
     - Priority level
     - Tags
     - Time remaining

---

## 🧪 Testing

### Test 1: Manual Email Test

Create a test script `backend/test_email.py`:

```python
from src.services.email_service import email_service
from datetime import datetime, timedelta

# Test email sending
test_due_date = datetime.utcnow() + timedelta(hours=24)

success = email_service.send_reminder(
    to_email="your-test-email@gmail.com",
    task_title="Test Task - Email Reminder",
    task_description="This is a test to verify email reminders are working!",
    due_date=test_due_date,
    priority="high",
    tags=["test"],
    task_id="test-123"
)

print(f"Email sent: {success}")
```

Run it:
```bash
cd backend
python test_email.py
```

Check your inbox!

### Test 2: Full Integration Test

1. **Create a task due tomorrow:**
   - Due date: Tomorrow's date
   - Title: "Test Reminder Task"

2. **Wait for hourly check** (or manually trigger):
   ```python
   from src.services.reminder_service import check_and_send_reminders
   from src.core.database import get_session

   session = next(get_session())
   result = check_and_send_reminders(session)
   print(result)  # Should show {"sent": 1, ...}
   ```

3. **Check your email** - you should receive reminder immediately

4. **Verify in database:**
   ```python
   # Check that reminder_sent is now True
   ```

---

## 📊 Email Template Preview

Here's what the email looks like:

```
🔔 Task Reminder

Your task is due tomorrow:

┌─────────────────────────────────────┐
│ Test Reminder Task                  │
│                                     │
│ This is a test to verify email...   │
│                                     │
│ 📅 Due Date: January 29, 2026      │
│ ⏰ Time Remaining: 24 hours         │
│ 🎯 Priority: 🔴 High                │
│ 🏷️ Tags: test                       │
└─────────────────────────────────────┘

💡 Tip: Make sure to complete your task on time!

---
This is an automated reminder from your Todo App.
Task ID: test-123
```

---

## 🔍 Troubleshooting

### Scheduler Not Starting

**Problem:** `⚠️ Reminder scheduler disabled (Gmail not configured)`

**Solution:**
1. Check `.env` file has `GMAIL_EMAIL` and `GMAIL_APP_PASSWORD`
2. Restart the backend server
3. Check for typos in env var names

### Emails Not Sending

**Problem:** No emails received

**Solutions:**
1. **Check app password:**
   - Make sure you're using the 16-character app password, NOT your regular password
   - Regenerate the app password if needed

2. **Check Gmail settings:**
   - Make sure 2-Step Verification is enabled
   - Make sure "Less secure app access" is NOT blocked

3. **Check logs:**
   ```bash
   # Look for error messages in backend console
   # Common errors:
   # - "Authentication failed" → Wrong password
   # - "Connection refused" → Network/firewall issue
   ```

### Migration Failed

**Problem:** `Can't locate revision identified by '29f774bde39a'`

**Solution:**
The migration was already created manually at `backend/alembic/versions/002_add_reminder_sent.py`. Just run:
```bash
cd backend
python -m alembic upgrade head
```

---

## 📝 Summary

### Files Created/Modified

**Backend:**
- ✅ `backend/src/models/todo.py` - Added `reminder_sent` field
- ✅ `backend/src/schemas/todo.py` - Updated response schema
- ✅ `backend/src/services/email_service.py` - NEW email sending service
- ✅ `backend/src/services/reminder_service.py` - NEW reminder checker
- ✅ `backend/src/core/config.py` - Added Gmail config
- ✅ `backend/src/main.py` - Integrated scheduler
- ✅ `backend/src/api/todos.py` - Updated to return `reminder_sent`
- ✅ `backend/requirements.txt` - Added APScheduler
- ✅ `backend/alembic/versions/002_add_reminder_sent.py` - NEW migration

**Frontend:**
- ✅ `frontend/src/components/dashboard/CreateTodoModal.tsx` - Shows reminder info
- ✅ `frontend/src/components/dashboard/TodoList.tsx` - Shows reminder indicator
- ✅ `frontend/src/types/index.ts` - Added `reminder_sent` to Todo interface

---

## 🎉 You're All Set!

Once you:
1. ✅ Generate Gmail app password
2. ✅ Add to `.env` or Hugging Face secrets
3. ✅ Run database migration
4. ✅ Restart the backend

Your app will automatically send reminder emails 1 day before tasks are due!

**The scheduler runs every hour**, checking for tasks due in ~24 hours and sending reminders.

---

*Implementation Date: 2026-01-28*
*Feature: Email Reminders for Tasks*
*Trigger: 1 day before due date*
*Service: Gmail SMTP*
*Scheduler: APScheduler (hourly)*
