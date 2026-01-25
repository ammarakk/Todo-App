# Implementation Plan: Phase 2 Cloud-Native Todo App

**Branch**: `001-phase-2-saas` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-2-saas/spec.md`

**Note**: This is a **controlled refinement** plan. We are upgrading an existing system to production-grade standards without breaking working functionality.

## Summary

Phase 2 transforms the existing Todo application from a basic implementation into a **secure, cloud-native, production-grade SaaS** with JWT-based authentication and user-isolated data management. The primary requirements are:

1. **JWT Authentication**: Secure token-based auth with validation, expiration, and logout
2. **User Data Isolation**: NON-NEGOTIABLE scoping of all data by user_id
3. **Premium UI/UX**: Responsive design, dark/light theme, professional layouts
4. **Complete CRUD**: Create, read, update, delete todos with search, filter, and sort
5. **Stability**: All existing functionality must remain working

**Technical Approach**: Incremental refinement with continuous validation against spec requirements.

## Technical Context

**Language/Version**:
- Frontend: TypeScript, React 18+, Next.js 14 (App Router)
- Backend: Python 3.11+, FastAPI
- Database: PostgreSQL 15+ (Neon hosting)

**Primary Dependencies**:
- Frontend: Next.js, React, TailwindCSS, shadcn/ui, axios/react-query
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, JWT (python-jose), bcrypt
- Auth: JWT (HS256 or RS256), bcrypt password hashing

**Storage**:
- PostgreSQL via Prisma ORM (frontend) or SQLAlchemy (backend)
- User accounts and todos tables with foreign key relationships
- JWT tokens stored client-side (localStorage or httpOnly cookies)

**Testing**:
- Frontend: Jest, React Testing Library, Playwright (E2E)
- Backend: pytest, pytest-asyncio, httpx
- Integration tests for auth flows and data isolation

**Target Platform**:
- Frontend: Vercel (server-side rendering, static optimization)
- Backend: HuggingFace Spaces or alternative container hosting
- Database: Neon PostgreSQL (managed cloud database)

**Project Type**: Web application (frontend + backend separation)

**Performance Goals**:
- Page load: <2s p95
- API response: <500ms p95
- Support 1,000+ concurrent users
- JWT validation: <100ms per request

**Constraints**:
- All protected API requests must include valid JWT in Authorization header
- Database queries must scope by user_id (data isolation)
- UI must be responsive (mobile, tablet, desktop)
- No horizontal scroll, no screen overflow
- Theme preference must persist across sessions

**Scale/Scope**:
- Target: 10,000 users, 1M+ todos
- User registration and login flows
- Todo CRUD with search, filter, sort
- Dark/light theme across all pages
- Responsive sidebar navigation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Current Constitution Status**: Template (not yet customized)

**Assessment**: No constitution gates to violate. Proceeding with best practices:

✅ **Spec-Driven Development**: All work driven by approved spec.md
✅ **Incremental Refinement**: Upgrading existing system, not greenfield
✅ **Security First**: JWT auth and data isolation as top priorities
✅ **No Regressions**: Existing functionality must remain working
✅ **Stability Before Next Phase**: Phase 2 must be complete and stable before Phase 3

**Re-Check After Design**: Post-Phase 1, verify that chosen technologies and patterns align with production SaaS standards.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-2-saas/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (JWT, auth patterns, UI libraries)
├── data-model.md        # Phase 1 output (User, Todo entities)
├── quickstart.md        # Phase 1 output (dev setup, run instructions)
├── contracts/           # Phase 1 output (API contracts)
│   ├── auth-api.yaml    # Auth endpoints (signup, login, logout)
│   ├── todos-api.yaml   # Todo CRUD endpoints
│   └── openapi.json     # Complete OpenAPI spec
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created yet)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/                          # FastAPI backend service
├── alembic/                      # Database migrations
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User ORM model
│   │   ├── todo.py               # Todo ORM model
│   │   └── base.py               # Base ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth request/response schemas
│   │   ├── todo.py               # Todo schemas
│   │   └── user.py               # User schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependencies (JWT auth, get_db)
│   │   ├── auth.py               # Auth endpoints
│   │   └── todos.py              # Todo endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py           # JWT functions, password hashing
│   │   ├── database.py           # DB session management
│   │   └── config.py             # Settings from env
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py          # Auth flow tests
│       ├── test_todos.py         # Todo CRUD tests
│       └── test_security.py      # Data isolation tests
├── alembic.ini
├── pyproject.toml
└── .env                          # Environment variables

frontend/                         # Next.js 14 frontend (App Router)
├── src/
│   ├── app/
│   │   ├── layout.tsx            # Root layout (theme provider)
│   │   ├── page.tsx              # Home/login page
│   │   ├── signup/
│   │   │   └── page.tsx          # Signup page
│   │   ├── dashboard/
│   │   │   ├── layout.tsx        # Dashboard layout (sidebar)
│   │   │   └── page.tsx          # Dashboard main page
│   │   └── api/                  # Next.js API routes (if any proxying)
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx     # Login form with validation
│   │   │   └── SignupForm.tsx    # Signup form with validation
│   │   ├── dashboard/
│   │   │   ├── Sidebar.tsx       # Responsive sidebar
│   │   │   ├── TodoList.tsx      # Todo list with cards
│   │   │   ├── TodoForm.tsx      # Create/edit todo form
│   │   │   └── TodoCard.tsx      # Individual todo card
│   │   ├── theme/
│   │   │   ├── ThemeToggle.tsx   # Dark/light mode toggle
│   │   │   └── ThemeProvider.tsx # Theme context
│   │   └── layout/
│   │       ├── Header.tsx        # Top header with profile
│   │       └── LoadingSpinner.tsx
│   ├── lib/
│   │   ├── api.ts                # API client (axios/fetch wrapper)
│   │   ├── auth.ts               # Auth utilities (token storage)
│   │   └── utils.ts              # Helper functions
│   ├── hooks/
│   │   ├── useAuth.ts            # Auth hook (user, token, login, logout)
│   │   └── useTodos.ts           # Todo CRUD hook
│   ├── types/
│   │   ├── auth.ts               # Auth types (User, LoginRequest, etc.)
│   │   └── todo.ts               # Todo types
│   └── styles/
│       └── globals.css           # Global styles with Tailwind
├── public/                       # Static assets
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                      # Playwright E2E tests
├── next.config.js
├── tailwind.config.ts
├── package.json
└── tsconfig.json

docker-compose.yml                # Local dev (PostgreSQL, backend, frontend)
.env.example                      # Environment variables template
README.md                         # Project documentation
```

**Structure Decision**: Monorepo with separate frontend (Next.js) and backend (FastAPI) directories. This is a **web application** type with clear separation of concerns. Frontend communicates with backend via REST API using JWT authentication.

## Complexity Tracking

> **No Constitution Violations** - This section is not needed as we are following standard web application patterns without introducing unnecessary complexity.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **JWT Authentication Patterns**
   - Decision: Use JWT (HS256) with server-side secret
   - Rationale: Simple to implement, secure, stateless, works well with FastAPI
   - Alternatives considered: OAuth2 (too complex for single-user app), Sessions (less scalable)

2. **Password Hashing**
   - Decision: bcrypt with 12 rounds
   - Rationale: Industry standard, proven security, built-in salt
   - Alternatives considered: Argon2 (slower), PBKDF2 (older standard)

3. **Token Storage**
   - Decision: httpOnly cookies + fallback to localStorage
   - Rationale: httpOnly cookies prevent XSS, localStorage fallback for compatibility
   - Alternatives considered: Only localStorage (XSS risk), only cookies (CSRF risk)

4. **Frontend UI Library**
   - Decision: shadcn/ui + TailwindCSS
   - Rationale: Modern, accessible, customizable, great dark mode support
   - Alternatives considered: Material-UI (too opinionated), Chakra UI (larger bundle)

5. **ORM Choice**
   - Decision: SQLAlchemy 2.0 with async support
   - Rationale: Mature, async-ready, excellent FastAPI integration
   - Alternatives considered: Prisma (better TypeScript, but Python backend), Tortoise ORM (less mature)

6. **Database Validation**
   - Decision: Prisma ORM (if using Prisma) or SQLAlchemy validation
   - Rationale: Declarative validation, type safety
   - Alternatives considered: Manual SQL queries (error-prone)

**Output**: `research.md` will document these decisions with detailed rationale and code examples.

## Phase 1: Design & Contracts

### Data Model Design

**Entities** (from spec):

1. **User**
   - Fields: id (UUID), email (unique, indexed), password_hash (string), created_at (timestamp)
   - Relationships: has many Todos
   - Validation: email format, password min 8 chars, email uniqueness

2. **Todo**
   - Fields: id (UUID), title (string, required), completed (boolean, default false), priority (enum: low|medium|high, default medium), tags (array of strings), created_at (timestamp), user_id (FK to User)
   - Relationships: belongs to User
   - Constraints: user_id required, title required, title max length 255

**Database Schema** (SQLAlchemy models):

```python
# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    todos = relationship("Todo", back_populates="user")

# Todo Model
class Todo(Base):
    __tablename__ = "todos"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    tags = Column(JSON, default=list)  # Array of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="todos")
```

**Output**: `data-model.md` with complete entity definitions, relationships, and validation rules.

### API Contracts

**Authentication Endpoints**:

```
POST /api/auth/signup
- Request: { email: string, password: string }
- Response: { access_token: string, token_type: "bearer", user: { id, email } }
- Errors: 400 (validation), 409 (email exists)

POST /api/auth/login
- Request: { email: string, password: string }
- Response: { access_token: string, token_type: "bearer", user: { id, email } }
- Errors: 401 (invalid credentials)

POST /api/auth/logout
- Request: Header: Authorization: Bearer <token>
- Response: { message: "logged out" }
- Errors: 401 (invalid token)

GET /api/auth/me
- Request: Header: Authorization: Bearer <token>
- Response: { id, email, created_at }
- Errors: 401 (invalid token)
```

**Todo Endpoints** (All protected by JWT):

```
GET /api/todos
- Auth: Bearer token required
- Query params: ?search=string&status=pending|completed&priority=low|medium|high&sort=priority|title|created_at
- Response: [{ id, title, completed, priority, tags, created_at, user_id }]
- Errors: 401 (invalid token)

POST /api/todos
- Auth: Bearer token required
- Request: { title, priority?, tags? }
- Response: { id, title, completed, priority, tags, created_at, user_id }
- Errors: 400 (validation), 401 (invalid token)

GET /api/todos/{id}
- Auth: Bearer token required
- Response: { id, title, completed, priority, tags, created_at, user_id }
- Errors: 401 (invalid token), 404 (not found or not owned)

PUT /api/todos/{id}
- Auth: Bearer token required
- Request: { title?, completed?, priority?, tags? }
- Response: { id, title, completed, priority, tags, created_at, user_id }
- Errors: 400 (validation), 401 (invalid token), 404 (not found or not owned)

DELETE /api/todos/{id}
- Auth: Bearer token required
- Response: { message: "deleted" }
- Errors: 401 (invalid token), 404 (not found or not owned)
```

**Output**: `contracts/auth-api.yaml`, `contracts/todos-api.yaml`, `contracts/openapi.json`

### Security Implementation

**JWT Middleware** (FastAPI dependency):

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # 1. Decode token
    # 2. Verify signature
    # 3. Verify expiration
    # 4. Extract user_id
    # 5. Query user from DB
    # 6. Return user or raise 401
```

**Data Isolation Enforcement**:

```python
# All Todo queries MUST include user_id filter
stmt = select(Todo).where(Todo.user_id == current_user.id)
```

**Output**: `quickstart.md` with security patterns and implementation examples.

### Agent Context Update

After Phase 1 design, run:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This updates `.claude/settings.local.json` with:
- FastAPI patterns
- Next.js 14 App Router patterns
- JWT authentication flows
- SQLAlchemy async patterns

## Phase 2: Execution Strategy

This phase is **NOT greenfield development**. It is **controlled refinement**.

### Execution Flow

1. **Spec Compliance Mapping**
   - Convert 83 functional requirements into validation checklist
   - Create automated tests for each requirement

2. **Existing System Audit**
   - Scan current codebase for spec violations
   - Identify broken features, missing auth, UI issues
   - Generate prioritized bug list

3. **Security Enforcement**
   - Implement JWT validation middleware
   - Add user_id scoping to all database queries
   - Test data isolation (users cannot see other users' todos)

4. **UI/UX Upgrade**
   - Implement shadcn/ui components
   - Add dark/light theme with persistence
   - Build responsive sidebar layout
   - Add loading/error/empty states

5. **Functional Repair**
   - Fix broken signup/login flows
   - Fix routing issues
   - Connect frontend to backend APIs
   - Implement search, filter, sort

6. **QA Simulation**
   - Run E2E tests for complete user flows
   - Test auth: signup → login → dashboard → logout
   - Test CRUD: create → read → update → delete
   - Test data isolation: verify user cannot access other users' data

7. **Auto-Fix Loop**
   - Run tests
   - Fix failures
   - Re-run tests
   - Repeat until zero failures

### Exit Conditions (Phase 2 Lock)

Phase 2 is **COMPLETE** only when:

- ✅ JWT auth fully works (signup, login, logout, token validation)
- ✅ Users see only their own tasks (data isolation enforced)
- ✅ UI is premium & responsive (dark/light theme, mobile-ready)
- ✅ All CRUD works via database (not static/mock data)
- ✅ No console or runtime errors
- ✅ All 38 completion criteria pass

### Hard Rules

- **No working feature may be removed**
- **No hacks or shortcuts**
- **No UI regressions**
- **No security bypass**
- **No moving to Phase 3 without full stability**

## Next Steps

After this plan is approved:

1. **Phase 0**: Run research tasks to validate technology choices
2. **Phase 1**: Generate detailed design artifacts (data-model.md, contracts/, quickstart.md)
3. **Phase 2**: Run `/sp.tasks` to generate actionable task list
4. **Execute**: Run `/sp.implement` to begin controlled refinement

---

**Plan Status**: Ready for Phase 0 research
**Branch**: `001-phase-2-saas`
**Next Command**: `/sp.tasks` (to generate actionable task breakdown)
