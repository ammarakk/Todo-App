---
title: Todo App Backend
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Todo App Backend - Phase 2

FastAPI backend for the Todo SaaS application with authentication, database, and AI integration.

## 🚀 Hugging Face Spaces Deployment

This backend is configured to deploy on Hugging Face Spaces using Docker.

### Required Secrets (Set in Space Settings)

Add these in your Space's **Settings > Variables** section:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+psycopg://user:password@ep-xxx.aws.neon.tech/neondb

# JWT Authentication
JWT_SECRET=your-super-secret-key-min-32-chars-random

# Hugging Face API
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Cloudinary (for avatar uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Frontend CORS
FRONTEND_URL=https://your-frontend-url.vercel.app
CORS_ORIGINS=["https://your-frontend-url.vercel.app","http://localhost:3000"]

# App Settings
ENV=production
PORT=7860
LOG_LEVEL=info
```

### 🔑 Getting Your Hugging Face API Token

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Token name: `todo-app-backend`
4. Type: **Read** (for accessing public models)
5. Click **"Generate token"**
6. Copy the token (starts with `hf_`)
7. Add it as `HUGGINGFACE_API_KEY` in your Space's secrets

### 🐳 Docker Configuration

This Space uses the **Docker** SDK with the following setup:
- Base image: `python:3.11-slim`
- Port: `7860` (Hugging Face default)
- Server: Uvicorn ASGI server

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQLModel for ORM with Pydantic validation
- **Alembic** - Database migration tool
- **PostgreSQL** - Primary database (Neon in production)
- **JWT + bcrypt** - Secure authentication
- **Hugging Face** - AI integration for todo features
- **Cloudinary** - Avatar image storage

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -e .
```

Or install with dev dependencies:

```bash
pip install -e ".[dev]"
```

### 3. Setup environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start development server

```bash
uvicorn src.main:app --reload --port 8000
```

API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Project Structure

```
backend/
├── src/
│   ├── api/          # API route handlers
│   ├── core/         # Core configuration and utilities
│   ├── models/       # SQLModel database models
│   ├── schemas/      # Pydantic schemas for request/response
│   ├── services/     # Business logic services
│   ├── tests/        # Test files
│   └── utils/        # Utility functions
├── alembic/          # Database migrations
└── pyproject.toml    # Project configuration
```

## Available Scripts

```bash
# Development
python -m uvicorn src.main:app --reload

# Testing
pytest                           # Run tests
pytest --cov=src                # Run with coverage

# Database migrations
alembic revision --autogenerate -m "message"  # Create migration
alembic upgrade head                        # Apply migrations
alembic downgrade -1                        # Rollback one migration

# Code quality
black .               # Format code
ruff check .          # Lint code
ruff check . --fix    # Fix linting issues
mypy .               # Type checking
```

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Todos
- `GET /todos` - List todos with filtering
- `POST /todos` - Create todo
- `GET /todos/{id}` - Get single todo
- `PUT /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo
- `PATCH /todos/{id}/complete` - Mark todo complete

### User Profile
- `GET /users/me` - Get user profile
- `PUT /users/me` - Update user profile
- `POST /users/me/avatar` - Upload avatar

### AI Features
- `POST /ai/generate-todo` - Generate todo from text
- `POST /ai/summarize` - Summarize todos
- `POST /ai/prioritize` - Prioritize todos

## Environment Variables

See `.env.example` for required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT (min 32 chars)
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `HUGGINGFACE_API_KEY` - Hugging Face API key
- `FRONTEND_URL` - Frontend URL for CORS

## Development with Docker

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## License

MIT
