# Email Reminder System for Todo App

## Overview
Add email reminder functionality that sends notifications to users 1 day before their task's due date.

## Requirements (from user)
- Send reminder to user's login email
- Trigger: 1 day before due date/time
- Only for tasks with due dates set
- Email service: Gmail SMTP
- Email content: Task title, description, due date/time

---

## Architecture

### Components to Add

1. **Database Schema Changes**
   - Add `reminder_sent` boolean column to `todos` table
   - Tracks whether reminder has been sent for each task

2. **Email Service Module**
   - New module: `backend/src/services/email_service.py`
   - Handles SMTP connection and email sending
   - Uses Gmail SMTP with app-specific password

3. **Background Scheduler**
   - Add APScheduler to FastAPI lifespan
   - Runs every hour to check for tasks needing reminders
   - Finds tasks due in ~24 hours that haven't had reminders sent

4. **Frontend UI Updates**
   - Add reminder indicator in CreateTodoModal
   - Show reminder status in TodoList
   - Display "Reminder will be sent 1 day before" message

---

## Implementation Plan

### Phase 1: Database & Backend Core

#### 1.1 Update Todo Model
**File**: `backend/src/models/todo.py`

Add field:
```python
reminder_sent: Optional[bool] = Field(
    default=False,
    description='Whether reminder email has been sent',
)
```

#### 1.2 Create Database Migration
**Command**: From `backend/` directory
```bash
alembic revision --autogenerate -m "add reminder_sent to todos"
```

**Migration will add**:
```sql
ALTER TABLE todos ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;
```

**Apply migration**:
```bash
alembic upgrade head
```

#### 1.3 Update Todo Schemas
**File**: `backend/src/schemas/todo.py`

Update `TodoCreateRequest` and `TodoResponse` to include `reminder_sent` field

---

### Phase 2: Email Service

#### 2.1 Create Email Service Module
**New File**: `backend/src/services/email_service.py`

Handles SMTP connection to Gmail and sends HTML email reminders.

#### 2.2 Update Configuration
**File**: `backend/src/core/config.py`

Add environment variables:
```python
gmail_email: Optional[str] = Field(None, env="GMAIL_EMAIL")
gmail_app_password: Optional[str] = Field(None, env="GMAIL_APP_PASSWORD")
```

#### 2.3 Update requirements.txt
**File**: `backend/requirements.txt`

```
apscheduler>=3.10.0
```

---

### Phase 3: Reminder Scheduler

#### 3.1 Create Reminder Service
**New File**: `backend/src/services/reminder_service.py`

Function `check_and_send_reminders(session)` that:
- Finds tasks due within 25 hours
- Filters out completed tasks
- Filters out tasks that already had reminders sent
- Sends email for each eligible task
- Marks task as `reminder_sent = True`

#### 3.2 Integrate Scheduler into FastAPI
**File**: `backend/src/main.py`

Update lifespan function to:
- Initialize APScheduler on startup
- Add job to run `check_and_send_reminders` every hour
- Shutdown scheduler on app shutdown
- Only start if Gmail credentials are configured

---

### Phase 4: Frontend Updates

#### 4.1 Update CreateTodoModal
**File**: `frontend/src/components/dashboard/CreateTodoModal.tsx`

Add info message after due date field showing:
"🔔 Reminder email will be sent 1 day before due date"

#### 4.2 Update TodoList (Optional)
**File**: `frontend/src/components/dashboard/TodoList.tsx`

Add reminder icon (🔔) next to tasks with due dates

---

### Phase 5: Environment Configuration

#### 5.1 Backend Environment Variables
**File**: `backend/.env`

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password
```

#### 5.2 Generate Gmail App Password
Instructions:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Search for "App Passwords"
4. Create app password: "Mail" + "Other (Custom name)" = "Todo App"
5. Copy 16-character password
6. Add to `.env`

---

## Implementation Files Summary

### New Files to Create
1. `backend/src/services/email_service.py` - Email sending logic
2. `backend/src/services/reminder_service.py` - Reminder checking logic

### Files to Modify
1. `backend/src/models/todo.py` - Add `reminder_sent` field
2. `backend/src/schemas/todo.py` - Update schemas
3. `backend/src/core/config.py` - Add Gmail config
4. `backend/src/main.py` - Add scheduler to lifespan
5. `backend/requirements.txt` - Add APScheduler
6. `frontend/src/components/dashboard/CreateTodoModal.tsx` - Show reminder info
7. `frontend/src/components/dashboard/TodoList.tsx` - Add reminder indicator (optional)

### Database
1. Run: `alembic revision --autogenerate -m "add reminder_sent to todos"`
2. Run: `alembic upgrade head`

---

## Testing Plan

### Backend Testing
1. Run migration to add `reminder_sent` column
2. Test email service with sample email
3. Create task due in ~24 hours
4. Manually trigger reminder check
5. Verify email received and `reminder_sent = True`

### Frontend Testing
1. Open Create Todo modal
2. Set due date
3. Verify reminder message appears
4. Create task and verify indicator shows in list

### End-to-End Testing
1. Create task with due date = tomorrow
2. Wait for hourly check (or trigger manually)
3. Check email arrives
4. Verify no duplicate emails for same task

---

## Deployment Checklist

### Hugging Face Space Secrets
Add to your Hugging Face Space:
- `GMAIL_EMAIL`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail app-specific password

### Migration on Production
```bash
cd hf-space/backend
alembic upgrade head
```

### Verification
1. Check logs for "✅ Reminder scheduler started"
2. Monitor `/health` endpoint
3. Check error logs for email failures

---

## Security Considerations

1. **Gmail App Password**: Never commit to git, always use env vars
2. **Rate Limiting**: Hourly checks minimize Gmail API usage
3. **Error Handling**: Email failures don't crash the app
4. **User Privacy**: Only user's own email receives their reminders

---

## Future Enhancements (Optional)

1. Customizable reminder timing (1 day, 1 hour, etc.)
2. Snooze functionality
3. Overdue task reminders
4. Email preferences in user profile
5. Multiple reminders per task
6. Unsubscribe link in emails

---

## Rollback Plan

If issues arise:
1. Disable scheduler: Remove Gmail env vars
2. Revert migration: `alembic downgrade -1`
3. Remove `reminder_sent` handling from code
