# Phase 2 Developer Quickstart

**Feature**: 001-phase-2-saas
**Purpose**: Get started with Phase 2 development quickly
**Last Updated**: 2025-01-23

---

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL (or Neon account)
- Git

---

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo>
cd todo-app
git checkout 001-phase-2-saas
```

### 2. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlmodel alembic psycopg[binary] python-jose passlib[bcrypt] python-multipart cloudinary huggingface_hub

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run database migrations
alembic upgrade head

# Start backend
uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local with API URL

# Start dev server
npm run dev
```

### 4. Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/todoapp
JWT_SECRET=your-secret-key-min-32-chars
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
HUGGINGFACE_API_KEY=your-huggingface-key
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Key Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost or Neon

---

## Common Commands

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn src.main:app --reload` | Start dev server |
| `pytest` | Run tests |
| `alembic revision --autogenerate -m "message"` | Create migration |
| `alembic upgrade head` | Apply migrations |
| `alembic downgrade -1` | Rollback one migration |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm test` | Run unit tests |
| `npm run test:e2e` | Run E2E tests |
| `npm run lint` | Run ESLint |

---

## Development Workflow

1. Make changes to code
2. Run tests: `pytest` (backend) or `npm test` (frontend)
3. Commit changes with descriptive messages
4. Push to feature branch

---

## Troubleshooting

**Backend won't start**: Check DATABASE_URL in .env
**Frontend can't connect**: Ensure NEXT_PUBLIC_API_URL is correct
**Tests failing**: Run `alembic upgrade head` to reset database
**AI features not working**: Check HUGGINGFACE_API_KEY

---

**Next Steps**:
1. Read `spec.md` for feature requirements
2. Read `plan.md` for implementation phases
3. Run `/sp.tasks` to get implementation tasks
4. Run `/sp.implement` to generate code

---

**Quickstart Status**: ✅ Complete
