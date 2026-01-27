# Implementation Plan: AI Assistant Integration

**Branch**: `001-ai-assistant` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-assistant/spec.md`

## Summary

**Objective**: Integrate AI Assistant as a floating control panel within the existing Dashboard, replacing the standalone chatbot page while preserving all Phase 2 Todo functionality.

**Technical Approach**:
- Reuse existing Phase 2 Todo CRUD APIs and database (no duplication)
- Add floating chat panel to Dashboard (not separate route)
- Leverage existing Qwen AI integration and MCP tools from Phase III
- Remove standalone chatbot page and route
- Maintain JWT authentication and user isolation

**Key Constraint**: AI is a **control interface layer**, not a separate application. Must extend Phase 2, not rebuild it.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, Next.js 13+ (App Router)
- Backend: Python 3.11+, FastAPI 0.104+

**Primary Dependencies**:
- Frontend: React 18, Tailwind CSS, Framer Motion
- Backend: FastAPI, SQLModel, Qwen (Hugging Face), MCP SDK
- Auth: JWT with Bcrypt

**Storage**: PostgreSQL (Neon Serverless)
- Existing tables: `Todo`, `User`, `Conversation`, `Message`
- No new tables required

**Testing**: pytest (backend), React Testing Library (frontend)
**Target Platform**: Vercel (frontend), Hugging Face Spaces (backend)
**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- AI command processing: <3 seconds (p95) per SC-003
- Task creation via AI: <10 seconds end-to-end per SC-001
- Support 100 concurrent AI requests per SC-007

**Constraints**:
- Zero regression in Phase 2 functionality per SC-004
- No duplicate CRUD logic per FR-012
- AI must use existing Todo APIs per FR-012
- 100% authentication enforcement per SC-006

**Scale/Scope**:
- Single unified application (not multi-tenant SaaS for this phase)
- Existing user base from Phase 2
- AI features for all authenticated users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: AI-Native Interaction
**Status**: ✅ PASS (with adaptation)
- Constitution requires chatbot as PRIMARY interface
- **Constitution Compliance**: This plan makes AI assistant PRIMARY by embedding in Dashboard (main workspace)
- Standalone chatbot page violates "integration layer" principle
- Floating panel in Dashboard ensures AI is always accessible

### Principle II: Stateless Server Architecture
**Status**: ✅ PASS
- Existing Phase III chat implementation is stateless
- Conversation history loaded from database per request
- No server-side session state maintained

### Principle III: Persistence of Intelligence
**Status**: ✅ PASS
- Existing `Conversation` and `Message` tables already implemented
- All chat sessions persisted to PostgreSQL
- No changes required to persistence layer

### Principle IV: Strict Security & User Isolation
**Status**: ✅ PASS
- Existing JWT authentication system enforced
- All database queries include `user_id` filters
- MCP tools already validate user_id before operations
- Zero changes to auth layer (maintain Phase II security)

### Principle V: Multi-Language Support
**Status**: ✅ PASS
- Existing Qwen integration supports English and Urdu
- Language auto-detection already implemented
- No changes needed to language handling

### Principle VI: MCP-First Tool Design
**Status**: ✅ PASS
- Existing MCP tools already exposed (create_todo, delete_todo, etc.)
- AI agent interacts ONLY through MCP tools
- Direct database access already prohibited
- Zero changes to MCP layer required

### Technical Stack Constraints
**Status**: ✅ PASS
- ✅ Qwen via Hugging Face SDK (already implemented)
- ✅ Official MCP SDK (already implemented)
- ✅ Neon PostgreSQL (already implemented)
- ✅ FastAPI + SQLModel stack (already implemented)
- ✅ Next.js frontend (already implemented)

### Architectural Principles
**Status**: ✅ PASS
- ✅ Separation of Concerns: MCP Server → Chat Service → FastAPI → Database (maintained)
- ✅ Error Handling: All tools catch and translate errors (maintained)
- ✅ Observability: Tool calls logged with user_id (maintained)
- ✅ Performance: p95 <10 seconds target (maintained)

### Security & User Isolation
**Status**: ✅ PASS
- ✅ JWT enforcement on all chat endpoints
- ✅ Database isolation with user_id filters
- ✅ Input sanitization before AI inference
- ✅ SQL injection protection via SQLModel

### Development Workflow (SDD)
**Status**: ✅ PASS
- ✅ No code generation without Task ID (will follow in `/sp.tasks`)
- ✅ Hierarchy of Truth: Constitution → Spec → Plan → Tasks
- ✅ Manual Coding Ban: All changes via Claude Code
- ✅ Reusable Intelligence: Leverage existing MCP tools and services

**Overall Constitution Compliance**: ✅ PASS

**Gate Result**: PROCEED to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-assistant/
├── spec.md              # Feature specification ✅
├── plan.md              # This file ✅
├── research.md          # Phase 0 output (pending)
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   └── ai-api.yaml      # OpenAPI spec for AI endpoint
├── tasks.md             # Phase 2 output (to be created by /sp.tasks)
└── checklists/
    └── requirements.md  # Spec quality checklist ✅
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx          # MODIFY: Add floating AI button
│   │   ├── chat/
│   │   │   └── page.tsx          # DELETE: Remove standalone chatbot page
│   │   └── ai/
│   │       └── page.tsx          # KEEP: AI todo features page
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── TodoStats.tsx     # KEEP: Existing
│   │   │   ├── TodoList.tsx      # KEEP: Existing
│   │   │   ├── TodoFilters.tsx   # KEEP: Existing
│   │   │   └── CreateTodoModal.tsx # KEEP: Existing
│   │   └── ai-assistant/         # NEW: Floating chat components
│   │       ├── AIChatButton.tsx  # Floating action button
│   │       ├── AIChatPanel.tsx   # Chat modal/panel
│   │       ├── ChatMessage.tsx   # Message display component
│   │       ├── ChatInput.tsx     # Input field with send button
│   │       └── useAIChat.ts      # Chat state management hook
│   ├── lib/
│   │   └── api.ts                # MODIFY: Add AI command API client
│   └── hooks/
│       └── useAuth.ts            # KEEP: Existing auth hook
└── tests/
    └── integration/
        └── ai-chat.test.tsx      # NEW: AI chat integration tests

backend/
├── src/
│   ├── main.py                   # MODIFY: Remove standalone chatbot route
│   ├── api/
│   │   ├── auth.py               # KEEP: Existing
│   │   ├── todos.py              # KEEP: Existing (AI calls this)
│   │   ├── users.py              # KEEP: Existing
│   │   ├── ai.py                 # KEEP: Existing (AI todo features)
│   │   └── chat.py               # MODIFY: Refactor for dashboard integration
│   ├── models/
│   │   ├── user.py               # KEEP: Existing
│   │   ├── todo.py               # KEEP: Existing (no changes)
│   │   ├── conversation.py       # KEEP: Existing
│   │   └── message.py            # KEEP: Existing
│   ├── ai/
│   │   ├── qwen_client.py        # KEEP: Existing
│   │   └── prompt_builder.py     # KEEP: Existing
│   └── mcp/
│       └── tools.py              # KEEP: Existing MCP tools
└── tests/
    ├── integration/
    │   └── ai_integration.test.py # NEW: Full system AI tests
    └── unit/
        └── chat.test.py          # MODIFY: Add dashboard integration tests
```

**Structure Decision**: Web application with frontend/backend separation.
- **Frontend**: Next.js with TypeScript in `frontend/` directory
- **Backend**: FastAPI with Python in `backend/` directory
- **Key Change**: Remove standalone `/chat` route, integrate AI into `/dashboard`
- **Database**: No changes to existing PostgreSQL schema

## Complexity Tracking

> No constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | All gates passed |

## Phase 0: Research & Decisions

**Objective**: Resolve all technical unknowns before design phase.

### Research Tasks

1. **Frontend Chat UI Pattern**
   - **Decision Needed**: Which chat UI pattern to use for floating panel?
   - **Options**: Modal dialog, Slide-over panel, Fixed bottom-right widget
   - **Research**: Best practices for embedded chat interfaces in productivity apps
   - **Output**: UI component specification with accessibility considerations

2. **Real-time Communication**
   - **Decision Needed**: Should AI responses stream in real-time or show as complete?
   - **Options**: Server-Sent Events (SSE), WebSocket, Polling, Simple HTTP response
   - **Research**: Performance and user experience implications
   - **Output**: Communication protocol decision

3. **Session Management**
   - **Decision Needed**: How to handle chat session lifecycle in floating panel?
   - **Options**: Single persistent session, New session per panel open, User-selectable
   - **Research**: User behavior patterns for task management assistants
   - **Output**: Session management strategy

4. **Error Recovery**
   - **Decision Needed**: How to handle AI service failures in integrated UI?
   - **Options**: Graceful degradation with retry, Queue commands for later, Show manual UI fallback
   - **Research**: Error handling patterns for AI-powered features
   - **Output**: Error handling UX specification

5. **Dashboard State Synchronization**
   - **Decision Needed**: How to sync AI-made changes with Dashboard UI?
   - **Options**: Polling, WebSocket updates, React Context re-fetch, Server push
   - **Research**: Real-time data sync patterns in Next.js
   - **Output**: State synchronization architecture

**Output**: `research.md` with decisions, rationale, and alternatives considered.

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### 1.1 Data Model (`data-model.md`)

**No New Database Entities Required**

The AI Assistant operates on existing Phase 2 and Phase III entities:

```yaml
Existing Entities (No Changes):
  - Todo:
      user_id: UUID (FK)
      title: TEXT
      description: TEXT
      status: ENUM (pending, completed)
      priority: ENUM (low, medium, high)
      tags: TEXT[]
      due_date: TIMESTAMP
      created_at: TIMESTAMP
      updated_at: TIMESTAMP

  - User:
      id: UUID (PK)
      email: TEXT
      password_hash: TEXT
      created_at: TIMESTAMP

  - Conversation:
      id: UUID (PK)
      user_id: UUID (FK)
      created_at: TIMESTAMP
      updated_at: TIMESTAMP
      title: TEXT
      language: VARCHAR(5)

  - Message:
      id: UUID (PK)
      conversation_id: UUID (FK)
      role: TEXT (user, assistant, system)
      content: TEXT
      created_at: TIMESTAMP
      tool_calls: JSONB
```

**Transient State (Frontend-only)**:
```typescript
interface AIChatSession {
  conversationId: string;  // From existing Conversation entity
  messages: ChatMessage[]; // Loaded from Message entity
  isPanelOpen: boolean;    // UI state (not persisted)
  isLoading: boolean;      // UI state (not persisted)
}
```

### 1.2 API Contracts (`contracts/ai-api.yaml`)

**OpenAPI Specification for AI Command Endpoint**

```yaml
openapi: 3.0.0
info:
  title: Todo AI Assistant API
  version: 1.0.0

paths:
  /api/ai-command:
    post:
      summary: Execute natural language command via AI
      description: |
        Accepts natural language text, processes with AI model,
        executes action via existing Todo APIs, returns result.
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [message, conversationId]
              properties:
                message:
                  type: string
                  description: Natural language command from user
                  example: "Create a task called 'Buy groceries'"
                conversationId:
                  type: string
                  format: uuid
                  description: |
                    Existing conversation ID or 'new' to start new conversation
                  example: "123e4567-e89b-12d3-a456-426614174000"
      responses:
        '200':
          description: Command executed successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: true
                  action:
                    type: string
                    enum: [create_task, list_tasks, update_task, delete_task, complete_task, clarify]
                    example: "create_task"
                  message:
                    type: string
                    description: Human-readable response from AI
                    example: "✅ Task 'Buy groceries' has been added."
                  data:
                    type: object
                    description: |
                      Action-specific data (e.g., created task, task list)
                    example:
                      task:
                        id: "123e4567-e89b-12d3-a456-426614174000"
                        title: "Buy groceries"
                        status: "pending"
        '400':
          description: Invalid request (malformed message, missing fields)
        '401':
          description: Unauthorized (invalid or missing JWT token)
        '500':
          description: AI service error or database error
        '503':
          description: AI service temporarily unavailable

  /api/conversations/{conversationId}/messages:
    get:
      summary: Load conversation history
      description: |
        Retrieves all messages for a conversation to build chat context.
      security:
        - BearerAuth: []
      parameters:
        - name: conversationId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Conversation history retrieved
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                        role:
                          type: string
                          enum: [user, assistant, system]
                        content:
                          type: string
                        created_at:
                          type: string
                          format: date-time
                        tool_calls:
                          type: array
                          items:
                            type: object
        '401':
          description: Unauthorized
        '404':
          description: Conversation not found

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 1.3 Component Contracts (`contracts/components.md`)

**Frontend Component Specifications**

```typescript
// AIChatButton.tsx
interface AIChatButtonProps {
  onClick: () => void;
  unreadCount?: number;  // Optional: Show notification badge
}

// AIChatPanel.tsx
interface AIChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  conversationId: string;
}

// ChatMessage.tsx
interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  tool_calls?: ToolCall[];
}

// ChatInput.tsx
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  placeholder: string;
}

// useAIChat.ts (Hook)
interface AIChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string;
}

interface UseAIChatReturn {
  state: AIChatState;
  actions: {
    sendMessage: (message: string) => Promise<void>;
    loadHistory: (conversationId: string) => Promise<void>;
    clearError: () => void;
  };
}
```

### 1.4 Quickstart Guide (`quickstart.md`)

**Development Setup for AI Integration**

```markdown
# AI Assistant Integration - Quickstart

## Prerequisites
- Phase 2 system fully functional
- Qwen API key configured in backend `.env`
- PostgreSQL database running

## Development Workflow

1. **Start Backend**
   \`\`\`bash
   cd backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   \`\`\`

2. **Start Frontend**
   \`\`\`bash
   cd frontend
   npm install
   npm run dev
   \`\`\`

3. **Test AI Integration**
   - Open http://localhost:3000/dashboard
   - Click floating AI button (bottom-right)
   - Type: "Create a task called 'Test AI integration'"
   - Verify task appears in Todo list

## API Testing

Test AI command endpoint directly:
\`\`\`bash
curl -X POST http://localhost:8000/api/ai-command \\
  -H "Authorization: Bearer <JWT_TOKEN>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Show me my tasks",
    "conversationId": "new"
  }'
\`\`\`

## Key Files to Modify

### Frontend
- `frontend/src/app/dashboard/page.tsx` - Add AI chat button
- `frontend/src/components/ai-assistant/` - Create chat components
- `frontend/src/lib/api.ts` - Add AI API client functions

### Backend
- `backend/src/api/chat.py` - Refactor for dashboard integration
- `backend/src/main.py` - Remove standalone `/chat` route

## Testing

Run integration tests:
\`\`\`bash
# Backend
cd backend
pytest tests/integration/ai_integration.test.py

# Frontend
cd frontend
npm test -- ai-chat.test.tsx
\`\`\`

## Deployment

See Deployment Section below for Vercel and Hugging Face instructions.
```

## Phase 2: Architecture Decisions

### 2.1 Frontend Architecture

**Chat Panel Integration Pattern**

**Decision**: Fixed bottom-right floating panel that expands into modal

**Rationale**:
- Always accessible but not intrusive
- Follows pattern of successful productivity apps (Intercom, Crisp)
- Allows viewing Dashboard while chatting
- Simplest implementation with existing Tailwind CSS

**Component Hierarchy**:
```
Dashboard (page.tsx)
├── Existing Todo components (unchanged)
└── AIChatButton (fixed bottom-right)
    └── AIChatPanel (modal when opened)
        ├── ChatHeader (close button, title)
        ├── MessageList (scrollable message area)
        │   └── ChatMessage (individual message)
        └── ChatInput (text field + send button)
```

**State Management**:
- Use React Context for chat state (`AIChatContext`)
- Persist conversation ID in localStorage
- Load messages from API on panel open
- Real-time updates via polling (1-second interval) or re-fetch after action

**Dashboard Synchronization**:
- After AI executes task action, trigger re-fetch of Todo list
- Use existing `useAuth` and todo fetching hooks
- No direct state manipulation - always source of truth from API

### 2.2 Backend Architecture

**AI Command Flow**

```
User Message (Dashboard)
    ↓
POST /api/ai-command (JWT validated)
    ↓
chat.py handler
    ↓
Load conversation history from DB
    ↓
Build message array (Qwen format)
    ↓
Call Qwen API via qwen_client.py
    ↓
Parse AI response (action + parameters)
    ↓
Validate action
    ↓
Execute via MCP tools (which call existing Todo APIs)
    ↓
Save user message + AI response to Message table
    ↓
Return formatted response to Dashboard
```

**Key Design Decisions**:

1. **Reuse Existing Chat Infrastructure**
   - Leverage `chat.py` handler already implemented
   - Modify to support dashboard integration mode
   - Keep existing MCP tools and Qwen integration

2. **No Direct Database Access**
   - AI only interacts through MCP tools
   - MCP tools call existing Todo APIs (`todos.py`)
   - Maintains security and validation layers

3. **Session Management**
   - One active conversation per user (auto-resume)
   - Conversation ID stored in localStorage
   - User can start new conversation (clear history)

4. **Error Handling**
   - AI service failure: Return friendly error, suggest manual UI
   - Invalid action: AI asks clarifying question
   - Database error: Log and return error message
   - Timeout: Return "AI unavailable" message

### 2.3 Security Architecture

**Authentication Enforcement**:
```python
# All AI endpoints require JWT
async def ai_command_endpoint(
    request: AICommandRequest,
    current_user: User = Depends(get_current_user)  # JWT validation
):
    # current_user.id used for all operations
    pass
```

**User Isolation**:
```python
# MCP tools already validate user_id
async def create_todo_tool(
    title: str,
    user_id: UUID  # From JWT, not from AI
):
    # Query always includes user_id filter
    todo = Todo(title=title, user_id=user_id)
    # ...
```

**Input Sanitization**:
```python
# Before sending to Qwen
sanitized_message = sanitize_input(request.message)
# Remove HTML, SQL injection patterns, etc.
```

### 2.4 Performance Architecture

**Optimization Strategies**:

1. **Conversation History Pagination**
   - Load last 50 messages on panel open
   - Older messages loaded on scroll up

2. **Caching**
   - Cache user's active conversation in memory
   - Invalidate on new message

3. **Async Processing**
   - AI request is async (non-blocking)
   - Show loading indicator during processing

4. **Response Time Targets**:
   - p50: <2 seconds
   - p95: <3 seconds (per SC-003)
   - p99: <5 seconds

## Phase 3: Migration & Replacement Strategy

### 3.1 Removal of Standalone Chatbot

**Files to Delete**:
```text
frontend/src/app/chat/page.tsx           # Delete standalone chatbot page
frontend/src/components/chatbot/         # Delete if exists
```

**Routes to Remove**:
```python
# backend/src/main.py
# REMOVE this line:
app.include_router(chat.router, tags=['Chat'])  # Standalone route

# REPLACE with:
app.include_router(chat.router, prefix='/api/ai-chat', tags=['AI Chat'])
```

**Database Migration**: None (re-use existing Conversation/Message tables)

### 3.2 Dashboard Integration

**Frontend Changes**:
```typescript
// frontend/src/app/dashboard/page.tsx

import { AIChatButton } from '@/components/ai-assistant/AIChatButton';
import { AIChatPanel } from '@/components/ai-assistant/AIChatPanel';

export default function DashboardPage() {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="relative">
      {/* Existing Dashboard UI - UNCHANGED */}
      <TodoStats />
      <TodoFilters />
      <TodoList />
      <CreateTodoModal />

      {/* NEW: Floating AI Chat */}
      <AIChatButton onClick={() => setIsChatOpen(true)} />
      {isChatOpen && (
        <AIChatPanel
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
          conversationId={activeConversationId}
        />
      )}
    </div>
  );
}
```

**Backend Changes**:
```python
# backend/src/api/chat.py
# MODIFY: Support both standalone (deprecated) and dashboard integration

@router.post("/command")  # New endpoint for dashboard
async def ai_command(
    request: AICommandRequest,
    current_user: User = Depends(get_current_user)
):
    # Reuse existing chat logic
    # Return format optimized for dashboard UI
    pass

# DEPRECATED: Keep for backward compatibility during transition
@router.post("/")
async def chat_legacy(...):
    # Existing standalone chatbot logic
    # Mark as deprecated in docs
    pass
```

### 3.3 Migration Timeline

1. **Step 1**: Deploy new dashboard with AI button (alongside existing chatbot)
2. **Step 2**: Monitor usage, fix bugs
3. **Step 3**: Deprecate standalone chatbot page (show migration notice)
4. **Step 4**: Remove standalone chatbot routes and components
5. **Step 5**: Update documentation and README

## Phase 4: Testing Strategy

### 4.1 Mandatory Full System Test

**Pre-Deployment Checklist** (from user's plan):

```text
□ Auth Test
  □ Signup works
  □ Login works
  □ Session valid

□ Todo UI Test (Phase 2 Regression Check)
  □ Create task via UI
  □ Edit task via UI
  □ Delete task via UI
  □ Mark complete via UI
  □ All existing features work identically

□ AI Test (New Phase 3 Features)
  □ "Add task buy milk" → Task created
  □ "Show my tasks" → Tasks listed in chat
  □ "Mark task done" → Task status updated
  □ "Delete task" → Task removed
  □ AI responses visible in chat panel
  □ Task list updates after AI action

□ Integration Test
  □ Task created via AI appears in UI
  □ Task created via UI visible to AI queries
  □ Both interfaces use same database
```

**If any test fails** → STOP deployment, fix issue, re-test.

### 4.2 Test Coverage Requirements

**Backend Tests** (`tests/integration/ai_integration.test.py`):
```python
def test_ai_command_create_task():
    """Test AI creates task via natural language"""
    pass

def test_ai_command_list_tasks():
    """Test AI lists user's tasks"""
    pass

def test_ai_command_invalid_task_id():
    """Test AI handles invalid task ID gracefully"""
    pass

def test_ai_user_isolation():
    """Test AI cannot access other users' tasks"""
    pass

def test_ai_authentication_required():
    """Test AI endpoint rejects unauthenticated requests"""
    pass
```

**Frontend Tests** (`tests/integration/ai-chat.test.tsx`):
```typescript
describe('AI Chat Integration', () => {
  it('opens chat panel when button clicked');
  it('sends message and receives AI response');
  it('displays loading indicator during processing');
  it('shows error message on AI failure');
  it('syncs todo list after AI creates task');
  it('maintains conversation history');
});
```

### 4.3 Security Testing

```python
def test_jwt_required():
    """Verify AI endpoint requires valid JWT"""
    response = client.post("/api/ai-command", json={...})
    assert response.status_code == 401  # Unauthorized

def test_user_isolation():
    """Verify AI cannot access other users' tasks"""
    user1_tasks = create_tasks(user_id=1)
    user2_token = authenticate_user(user_id=2)
    response = client.post(
        "/api/ai-command",
        json={"message": "Show me all tasks"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    # Should only return user2's tasks, not user1's
    assert len(response.json()['data']['tasks']) == 0

def test_input_sanitization():
    """Verify malicious input is sanitized"""
    malicious_input = "<script>alert('xss')</script> Create task"
    response = client.post("/api/ai-command", json={
        "message": malicious_input
    })
    # Should not execute script, should sanitize input
    assert "<script>" not in response.text
```

## Phase 5: Deployment Plan

### 5.1 Frontend Deployment (Vercel)

**Pre-Deployment Checklist**:
- [ ] All tests passing (pytest, npm test)
- [ ] No console errors in dev mode
- [ ] AI button visible on Dashboard
- [ ] Chat panel opens and closes correctly
- [ ] Environment variables configured (VITE_API_URL)

**Deployment Steps**:
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Deploy to Vercel
vercel --prod

# 3. Verify deployment
# - Open deployed URL
# - Login with test account
# - Test AI integration
# - Check browser console for errors
```

**Environment Variables** (Vercel):
```
VITE_API_URL=https://<backend-url>
```

### 5.2 Backend Deployment (Hugging Face Spaces)

**Pre-Deployment Checklist**:
- [ ] All backend tests passing
- [ ] AI endpoint responds correctly
- [ ] JWT authentication working
- [ ] Database connection stable
- [ ] MCP tools functional

**Deployment Steps**:
```bash
# 1. Update Hugging Face Space repository
git remote add hf https://huggingface.co/spaces/<username>/<space-name>
git push hf main

# 2. Verify deployment
# - Check Space status (Running)
# - Test /api/ai-command endpoint
# - Monitor logs for errors
```

**Environment Variables** (Hugging Face):
```
DATABASE_URL=postgresql://...
QWEN_API_KEY=hf_...
JWT_SECRET=...
CORS_ORIGINS=https://<frontend-url>
```

### 5.3 Deployment Safety Rules (from user's plan)

**Deployment allowed ONLY if**:

✅ No console errors
✅ No API failures
✅ No broken routes
✅ Todo works via UI
✅ Todo works via AI
✅ Auth stable

**If any condition fails**:
1. STOP deployment
2. Identify failing component
3. Fix issue
4. Re-run full system test
5. Retry deployment

### 5.4 Rollback Plan

**If critical issues found post-deployment**:

**Frontend Rollback**:
```bash
# Revert to previous Vercel deployment
vercel rollback --prod
```

**Backend Rollback**:
```bash
# Revert Hugging Face Space to previous commit
git revert HEAD
git push hf main
```

**Database**: No schema changes, so rollback is safe

## Phase 6: Monitoring & Observability

### 6.1 Metrics to Track

**Performance Metrics**:
- AI command response time (p50, p95, p99)
- AI command success rate
- Chat panel open/close frequency
- Task creation via AI vs UI ratio

**Error Metrics**:
- AI service failures
- Timeout errors
- Authentication failures
- Malicious input attempts

**User Engagement**:
- Daily active users of AI chat
- Average messages per conversation
- Task completion rate (AI-assisted vs manual)

### 6.2 Logging Strategy

**Backend Logging**:
```python
# Log all AI commands
logger.info(f"AI command", extra={
    "user_id": user_id,
    "action": action,
    "response_time_ms": response_time,
    "success": success
})
```

**Frontend Logging**:
```typescript
// Track errors
console.error('[AI Chat Error]', error);
// Send to error tracking service (e.g., Sentry)
```

## Phase 7: Documentation Updates

### 7.1 README Updates

**Add to Project README**:
```markdown
## AI Assistant Integration

The Todo application includes an AI-powered assistant that helps you manage tasks using natural language.

### How to Use

1. Open the Dashboard
2. Click the AI Assistant button (bottom-right corner)
3. Type commands like:
   - "Create a task called 'Buy groceries'"
   - "Show me my tasks"
   - "Mark task 1 as completed"
   - "Delete the task about meeting"

### Supported Commands

- **Create tasks**: "Add task [title]"
- **List tasks**: "Show my tasks" / "What are my tasks?"
- **Complete tasks**: "Mark task [id/title] as done"
- **Update tasks**: "Update task [id] to [new title]"
- **Delete tasks**: "Delete task [id/title]"

### Privacy & Security

- AI commands are executed using your authenticated session
- AI can only access your own tasks (user isolation enforced)
- All conversations are stored securely in the database
```

### 7.2 API Documentation

**Update OpenAPI Docs** (FastAPI auto-docs at `/docs`):
- Add `/api/ai-command` endpoint documentation
- Include request/response examples
- Document authentication requirement
- Add error response scenarios

## Definition of Phase 3 Completion

Phase 3 is complete when:

✅ **One Unified Application**
- AI assistant integrated into Dashboard (floating panel)
- No standalone chatbot page
- All features accessible from single interface

✅ **No Standalone Chatbot**
- `/chat` route removed
- Chatbot components deleted
- No duplicate task management logic

✅ **AI Controls Todo System**
- Natural language commands work
- AI actions trigger existing Todo APIs
- Changes visible in real-time in Dashboard

✅ **System Secure**
- JWT authentication enforced on all AI endpoints
- User isolation verified (100% of tests pass)
- Input sanitization in place
- No direct database access from AI

✅ **All Tests Pass**
- Auth test: ✅
- Todo UI test: ✅ (Phase 2 regression check)
- AI test: ✅
- Integration test: ✅
- Security test: ✅

✅ **GitHub Updated**
- README documents AI integration
- API documentation updated
- Migration strategy documented

✅ **Deployments Replaced**
- Vercel deployment updated (frontend)
- Hugging Face deployment updated (backend)
- Old standalone chatbot removed
- Both deployments functional

✅ **Performance Targets Met**
- AI response time p95 <3 seconds
- Task creation via AI <10 seconds
- 100 concurrent requests supported

✅ **Zero Regression**
- All Phase 2 features work identically
- No broken routes
- No new bugs in existing functionality

---

## Next Steps

1. **Execute Research Phase** (Phase 0)
   - Investigate chat UI patterns
   - Decide on real-time communication strategy
   - Document findings in `research.md`

2. **Create Detailed Design** (Phase 1)
   - Generate `data-model.md` (confirm no changes needed)
   - Generate API contracts in `contracts/`
   - Create `quickstart.md`

3. **Generate Implementation Tasks** (Phase 2 via `/sp.tasks`)
   - Break down implementation into testable tasks
   - Order by dependencies
   - Assign task IDs

4. **Execute Implementation** (via `/sp.implement`)
   - Follow tasks from `tasks.md`
   - Write tests for each task
   - Update documentation

5. **Deploy & Validate**
   - Run full system test suite
   - Deploy to staging
   - Verify all functionality
   - Deploy to production

---

**Architectural Decision Records (ADRs)**:

**📋 Architectural decision detected: Floating chat panel vs separate page**
   - **Decision**: Floating chat panel integrated into Dashboard
   - **Rationale**: Maintains single unified application, always accessible, follows user's explicit requirement
   - **Trade-offs**: Simpler navigation vs. more complex state management
   - **Mitigation**: Use React Context for state, localStorage for persistence
   - Document? Run `/sp.adr chat-integration-pattern`

**📋 Architectural decision detected: Communication protocol for AI responses**
   - **Decision**: Simple HTTP responses with polling (not SSE/WebSocket)
   - **Rationale**: Simpler implementation, sufficient for <3s response times, easier to test
   - **Trade-offs**: No true streaming vs. simpler architecture
   - **Mitigation**: Show loading indicator, provide quick feedback
   - Document? Run `/sp.adr ai-communication-protocol`

---

**Plan Status**: ✅ Complete
**Branch**: `001-ai-assistant`
**Next Command**: `/sp.tasks` to generate implementation task list
