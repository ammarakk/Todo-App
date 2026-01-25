# Research: Phase 2 Technology Decisions

**Feature**: Phase 2 Cloud-Native Todo App
**Date**: 2026-01-24
**Status**: Complete

## Overview

This document captures research findings and technology decisions for Phase 2 implementation. All decisions align with production SaaS standards and the functional requirements specified in `spec.md`.

**Scope Note**: Phase 2 focuses on JWT authentication, user data isolation, and premium UI/UX. AI/Agents features are explicitly out of scope.

---

## 1. JWT Authentication Implementation

### Decision
Use **JWT (HS256 algorithm)** with 7-day expiration and httpOnly cookie storage.

### Rationale
- **Stateless**: No server-side session storage required, enabling horizontal scaling
- **FastAPI Integration**: Excellent library support via `python-jose[cryptography]`
- **Security**: HS256 with strong secret provides adequate security for single-tenant SaaS
- **Spec Compliance**: Meets SC-011 requirement (7-day session validity)

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| OAuth2 | Overkill for single-tenant app, adds unnecessary complexity |
| Session-based auth | Less scalable, requires server-side session state |
| RS256 (asymmetric) | More complex key management, benefits primarily for multi-service architectures |

### Implementation Pattern

```python
# backend/src/core/security.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days per spec

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## 2. Password Hashing

### Decision
Use **bcrypt** with 12 rounds.

### Rationale
- **Industry Standard**: Battle-tested, widely trusted
- **Built-in Salt**: No manual salt management required
- **Adaptive**: Work factor can be increased as hardware improves
- **Python Support**: `passlib[bcrypt]` or `bcrypt` library with excellent FastAPI integration

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| Argon2 | Slightly slower, less library support in Python ecosystem |
| PBKDF2 | Older standard, considered less future-proof than bcrypt |
| SHA-256 | Not designed for password hashing (requires manual salt) |

### Implementation Pattern

```python
# backend/src/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 3. Token Storage Strategy

### Decision
Use **httpOnly cookies** as primary method with **localStorage** fallback.

### Rationale
- **httpOnly Cookies**: Prevent XSS attacks (JavaScript cannot access cookies)
- **CSRF Protection**: SameSite=Strict attribute prevents CSRF attacks
- **Fallback to localStorage**: For compatibility with certain deployment scenarios
- **Persistence**: Both methods persist across page refreshes (spec requirement)

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| localStorage only | Vulnerable to XSS attacks, scripts can steal tokens |
| Cookies only (without httpOnly) | XSS can still read cookies via document.cookie |
| Memory only | Doesn't persist across refresh (violates spec requirement) |

### Implementation Pattern

```typescript
// frontend/src/lib/auth.ts
export const setToken = (token: string) => {
  // Backend sets httpOnly cookie
  // Frontend fallback to localStorage for development
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
};

export const getToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

export const clearToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
};
```

---

## 4. Frontend UI Library

### Decision
Use **shadcn/ui + TailwindCSS**

### Rationale
- **Modern & Professional**: Production-ready components with premium design
- **Accessibility**: Built with Radix UI primitives (excellent WCAG compliance)
- **Dark Mode**: First-class dark mode support (critical spec requirement)
- **Customizable**: Components owned by codebase (not npm dependencies)
- **TypeScript**: Full TypeScript support
- **Responsive**: Utility-first CSS enables mobile-first responsive design

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| Material-UI (MUI) | Too opinionated, harder to customize, larger bundle |
| Chakra UI | Good alternative but shadcn/ui has better dark mode |
| Ant Design | Enterprise-focused, too heavy for this use case |

### Implementation Pattern

```bash
# Install shadcn/ui
npx shadcn-ui@latest init

# Add required components
npx shadcn-ui@latest add button input card form toast label select
```

---

## 5. Backend ORM Choice

### Decision
Use **SQLAlchemy 2.0** with async support.

### Rationale
- **Mature**: Battle-tested, widely used in Python ecosystem
- **Async-Ready**: SQLAlchemy 2.0 has first-class async support
- **FastAPI Integration**: Excellent async session management
- **Data Isolation**: Easy to enforce user_id scoping in all queries
- **Migrations**: Alembic provides robust database migrations

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| Prisma | Better TypeScript but Python backend required |
| Tortoise ORM | Less mature, smaller community |
| Django ORM | Tied to Django framework |

### Implementation Pattern

```python
# backend/src/models/base.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 6. API Client Pattern

### Decision
Use **axios** with interceptor for JWT injection.

### Rationale
- **Interceptor**: Automatically add JWT to all requests (spec requirement)
- **Error Handling**: Centralized 401 handling (redirect to login)
- **Type Safety**: Full TypeScript support
- **Request/Response**: Automatic JSON parsing

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| fetch API | More boilerplate, no automatic retries |
| react-query | Good for data fetching but axios provides lower-level control |

### Implementation Pattern

```typescript
// frontend/src/lib/api.ts
import axios from 'axios';
import { getToken } from './auth';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor: add JWT token
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 7. State Management

### Decision
**React Context** for auth state, **TanStack Query** for server state.

### Rationale
- **Auth State**: Simple enough for React Context (user, token, login/logout)
- **Server State**: TanStack Query handles caching, invalidation, loading states
- **Type Safety**: Full TypeScript support
- **DevTools**: Excellent React Query DevTools for debugging

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| Redux | Overkill for this app size |
| Zustand | Good but Context + TanStack Query is sufficient |

### Implementation Pattern

```typescript
// frontend/src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const navigate = useNavigate();

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    setUser(response.data.user);
    setToken(response.data.access_token);
    navigate('/dashboard');
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    clearToken();
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

## 8. Testing Strategy

### Decision
- **Backend**: pytest + pytest-asyncio + httpx
- **Frontend Unit**: Jest + React Testing Library
- **Frontend E2E**: Playwright

### Rationale
- **pytest**: Industry standard for Python, async support
- **React Testing Library**: Tests user behavior, not implementation
- **Playwright**: Modern E2E testing, cross-browser, fast

### Implementation Pattern

```python
# backend/src/tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_data_isolation(client: AsyncClient):
    # Create two users
    await client.post("/api/auth/signup", json={"email": "user1@example.com", "password": "pass"})
    await client.post("/api/auth/signup", json={"email": "user2@example.com", "password": "pass"})

    # Login as user1
    response = await client.post("/api/auth/login", json={"email": "user1@example.com", "password": "pass"})
    token1 = response.json()["access_token"]

    # Create todo as user1
    response = await client.post(
        "/api/todos",
        json={"title": "User1 Todo"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    # Login as user2
    response = await client.post("/api/auth/login", json={"email": "user2@example.com", "password": "pass"})
    token2 = response.json()["access_token"]

    # User2 should NOT see user1's todo
    response = await client.get("/api/todos", headers={"Authorization": f"Bearer {token2}"})
    todos = response.json()
    assert len(todos) == 0  # User2 has no todos
```

```typescript
// frontend/tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('user can signup', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'testpass123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});

test('user data isolation', async ({ page, context }) => {
  // Create and login as user1
  await page.goto('/signup');
  await page.fill('input[name="email"]', 'user1@example.com');
  await page.fill('input[name="password"]', 'pass123');
  await page.click('button[type="submit"]');

  // Create todo
  await page.click('text=New Todo');
  await page.fill('input[name="title"]', 'User1 Todo');
  await page.click('button:has-text("Create")');

  // Logout
  await page.click('text=Logout');

  // Login as user2
  await page.fill('input[name="email"]', 'user2@example.com');
  await page.fill('input[name="password"]', 'pass123');
  await page.click('button[type="submit"]');

  // User2 should NOT see User1's todo
  await expect(page.locator('text=User1 Todo')).not.toBeVisible();
});
```

---

## 9. Deployment Architecture

### Decision
- **Frontend**: Vercel (server-side rendering, static optimization)
- **Backend**: HuggingFace Spaces, Railway, or Render (container hosting)
- **Database**: Neon PostgreSQL (managed, serverless Postgres)

### Rationale
- **Vercel**: Best Next.js deployment, zero-config, preview deployments
- **HuggingFace/Railway/Render**: Free tier available, easy container deployment for FastAPI
- **Neon**: Serverless Postgres, auto-scaling, branching

### Environment Variables

```bash
# .env.example
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,https://yourdomain.vercel.app

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 10. Theme Management

### Decision
**next-themes** library for dark/light mode with persistence.

### Rationale
- **Next.js Integration**: Designed for Next.js App Router
- **SSR Support**: Handles server-side rendering correctly
- **Persistence**: Automatic localStorage persistence
- **No Flash**: Prevents flash of wrong theme on page load

### Implementation Pattern

```typescript
// frontend/src/components/theme/ThemeProvider.tsx
import { ThemeProvider as NextThemesProvider } from 'next-themes';

export function ThemeProvider({ children }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}

// Usage in component
import { useTheme } from 'next-themes';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      Toggle Theme
    </button>
  );
}
```

---

## Summary

| Decision | Technology | Rationale |
|----------|-----------|-----------|
| JWT Auth | HS256, 7-day expiration | Stateless, scalable, spec-compliant |
| Password Hashing | bcrypt (12 rounds) | Industry standard, proven security |
| Token Storage | httpOnly cookies + localStorage fallback | XSS-proof, persists across refresh |
| UI Library | shadcn/ui + TailwindCSS | Premium design, dark mode, responsive |
| Backend ORM | SQLAlchemy 2.0 async | Mature, async-ready, excellent FastAPI support |
| API Client | axios with interceptors | Auto JWT injection, centralized error handling |
| State Management | React Context + TanStack Query | Simple auth, powerful server state |
| Testing | pytest + Jest + Playwright | Industry standards, async support |
| Deployment | Vercel (FE) + HuggingFace/Railway (BE) + Neon (DB) | Free tiers, easy deployment |
| Theme | next-themes | Next.js optimized, SSR support |

**Next Phase**: Proceed to Phase 1 (Design & Contracts) to generate data model and API contracts.
