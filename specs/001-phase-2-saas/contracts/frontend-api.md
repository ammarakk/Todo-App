# Frontend API Integration Guide

**Feature**: 001-phase-2-saas
**Purpose**: Guide for integrating FastAPI backend with Next.js frontend
**Last Updated**: 2025-01-23

---

## Overview

This document provides TypeScript types and API client functions for integrating the FastAPI backend with the Next.js frontend.

---

## TypeScript Types

Copy these types into `frontend/src/types/api.ts`:

```typescript
// Common Types

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
}

export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

// Auth Types

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  message: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}

// Todo Types

export type TodoStatus = 'pending' | 'completed';
export type TodoPriority = 'low' | 'medium' | 'high';

export interface TodoCreateRequest {
  title: string;
  description?: string | null;
  priority?: TodoPriority;
  due_date?: string | null;
  tags?: string[] | null;
}

export interface TodoUpdateRequest {
  title?: string;
  description?: string | null;
  priority?: TodoPriority;
  due_date?: string | null;
  tags?: string[] | null;
}

export interface Todo {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TodoStatus;
  priority: TodoPriority;
  tags: string[] | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TodoListParams {
  skip?: number;
  limit?: number;
  status?: 'all' | 'pending' | 'completed';
  priority?: TodoPriority;
  search?: string;
  sort_by?: 'created_at' | 'due_date' | 'priority';
}

export interface TodoListResponse {
  todos: Todo[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

// User Profile Types

export interface UserProfile extends User {
  stats: {
    total_todos: number;
    pending_todos: number;
    completed_todos: number;
  };
}

export interface UserProfileUpdateRequest {
  name?: string;
}

export interface AvatarUploadResponse {
  avatar_url: string;
  message: string;
}

// AI Types

export interface AIGenerateRequest {
  goal: string;
}

export interface AIGeneratedTodo {
  title: string;
  description: string;
  priority: TodoPriority;
  due_date: string;
}

export interface AIGenerateResponse {
  todos: AIGeneratedTodo[];
  message: string;
}

export interface AISummaryBreakdown {
  high_priority: number;
  medium_priority: number;
  low_priority: number;
}

export interface AISummarizeResponse {
  summary: string;
  breakdown: AISummaryBreakdown;
  urgent_todos: string[];
}

export interface AIPrioritizedTodo {
  id: string;
  title: string;
  priority_score: number;
  reasoning: string;
}

export interface AIPrioritizeResponse {
  prioritized_todos: AIPrioritizedTodo[];
  message: string;
}
```

---

## API Client

Create `frontend/src/lib/api.ts`:

```typescript
/**
 * API Client for Todo App Backend
 *
 * Handles all HTTP communication with FastAPI backend.
 * Manages JWT tokens automatically via httpOnly cookies.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Include httpOnly cookies
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();

  if (!response.ok) {
    throw new ApiError(data.detail || 'An error occurred', response.status);
  }

  return data;
}

class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

// Auth API

export const authApi = {
  /**
   * Register new user
   * POST /auth/signup
   */
  async signup(data: SignupRequest): Promise<AuthResponse> {
    return fetchApi<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Login user
   * POST /auth/login
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    return fetchApi<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Logout user
   * POST /auth/logout
   */
  async logout(): Promise<{ message: string }> {
    return fetchApi<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
  },

  /**
   * Get current user
   * GET /auth/me
   */
  async getMe(): Promise<User> {
    return fetchApi<User>('/auth/me');
  },
};

// Todos API

export const todosApi = {
  /**
   * List todos with filtering and pagination
   * GET /todos
   */
  async list(params: TodoListParams = {}): Promise<TodoListResponse> {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.set('limit', params.limit.toString());
    if (params.status) queryParams.set('status', params.status);
    if (params.priority) queryParams.set('priority', params.priority);
    if (params.search) queryParams.set('search', params.search);
    if (params.sort_by) queryParams.set('sort_by', params.sort_by);

    const query = queryParams.toString();
    return fetchApi<TodoListResponse>(`/todos${query ? `?${query}` : ''}`);
  },

  /**
   * Get single todo
   * GET /todos/{id}
   */
  async get(id: string): Promise<Todo> {
    return fetchApi<Todo>(`/todos/${id}`);
  },

  /**
   * Create todo
   * POST /todos
   */
  async create(data: TodoCreateRequest): Promise<Todo> {
    return fetchApi<Todo>('/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update todo
   * PUT /todos/{id}
   */
  async update(id: string, data: TodoUpdateRequest): Promise<Todo> {
    return fetchApi<Todo>(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete todo
   * DELETE /todos/{id}
   */
  async delete(id: string): Promise<void> {
    return fetchApi<void>(`/todos/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Toggle todo completion
   * PATCH /todos/{id}/complete
   */
  async toggleComplete(id: string, completed: boolean): Promise<Todo> {
    return fetchApi<Todo>(`/todos/${id}/complete`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
  },
};

// Users API

export const usersApi = {
  /**
   * Get user profile with stats
   * GET /users/me
   */
  async getProfile(): Promise<UserProfile> {
    return fetchApi<UserProfile>('/users/me');
  },

  /**
   * Update user profile
   * PUT /users/me
   */
  async updateProfile(data: UserProfileUpdateRequest): Promise<UserProfile> {
    return fetchApi<UserProfile>('/users/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Upload avatar
   * POST /users/me/avatar
   */
  async uploadAvatar(file: File): Promise<AvatarUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json();
      throw new ApiError(data.detail || 'Upload failed', response.status);
    }

    return response.json();
  },
};

// AI API

export const aiApi = {
  /**
   * Generate todos from goal
   * POST /ai/generate-todo
   */
  async generateTodos(goal: string): Promise<AIGenerateResponse> {
    return fetchApi<AIGenerateResponse>('/ai/generate-todo', {
      method: 'POST',
      body: JSON.stringify({ goal }),
    });
  },

  /**
   * Summarize todos
   * POST /ai/summarize
   */
  async summarize(): Promise<AISummarizeResponse> {
    return fetchApi<AISummarizeResponse>('/ai/summarize', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },

  /**
   * Prioritize todos
   * POST /ai/prioritize
   */
  async prioritize(): Promise<AIPrioritizeResponse> {
    return fetchApi<AIPrioritizeResponse>('/ai/prioritize', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },
};

// Health API

export const healthApi = {
  /**
   * Check API health
   * GET /health
   */
  async check(): Promise<{ status: string }> {
    return fetchApi<{ status: string }>('/health');
  },
};

export { ApiError };
```

---

## React Hooks

Create `frontend/src/hooks/useAuth.ts`:

```typescript
import { useState, useEffect } from 'react';
import { authApi, ApiError } from '@/lib/api';
import type { User } from '@/types/api';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const userData = await authApi.getMe();
      setUser(userData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        // Not logged in - clear user
        setUser(null);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }

  async function signup(name: string, email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await authApi.signup({ name, email, password });
      setUser(response.user);
      return response;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Signup failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await authApi.login({ email, password });
      setUser(response.user);
      return response;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    setLoading(true);
    setError(null);
    try {
      await authApi.logout();
      setUser(null);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Logout failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return {
    user,
    loading,
    error,
    signup,
    login,
    logout,
    isAuthenticated: !!user,
  };
}
```

Create `frontend/src/hooks/useTodos.ts`:

```typescript
import { useState, useEffect } from 'react';
import { todosApi, ApiError } from '@/lib/api';
import type { Todo, TodoListParams, TodoCreateRequest } from '@/types/api';

export function useTodos(params: TodoListParams = {}) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTodos();
  }, [params.skip, params.limit, params.status, params.priority, params.search, params.sort_by]);

  async function fetchTodos() {
    setLoading(true);
    setError(null);
    try {
      const response = await todosApi.list(params);
      setTodos(response.todos);
      setTotal(response.total);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to fetch todos';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function createTodo(data: TodoCreateRequest) {
    setError(null);
    try {
      const newTodo = await todosApi.create(data);
      setTodos([newTodo, ...todos]);
      setTotal(total + 1);
      return newTodo;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to create todo';
      setError(message);
      throw err;
    }
  }

  async function updateTodo(id: string, data: Partial<TodoCreateRequest>) {
    setError(null);
    try {
      const updated = await todosApi.update(id, data);
      setTodos(todos.map((t) => (t.id === id ? updated : t)));
      return updated;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to update todo';
      setError(message);
      throw err;
    }
  }

  async function deleteTodo(id: string) {
    setError(null);
    try {
      await todosApi.delete(id);
      setTodos(todos.filter((t) => t.id !== id));
      setTotal(total - 1);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to delete todo';
      setError(message);
      throw err;
    }
  }

  async function toggleComplete(id: string, completed: boolean) {
    setError(null);
    try {
      const updated = await todosApi.toggleComplete(id, completed);
      setTodos(todos.map((t) => (t.id === id ? updated : t)));
      return updated;
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to update todo';
      setError(message);
      throw err;
    }
  }

  return {
    todos,
    total,
    loading,
    error,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleComplete,
    refetch: fetchTodos,
  };
}
```

---

## Environment Variables

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://todo-app-api.onrender.com
```

---

## Usage Examples

### Authentication

```typescript
// In your component
import { useAuth } from '@/hooks/useAuth';

function LoginPage() {
  const { login, error, loading } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err) {
      // Error already set in hook state
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      {/* Form fields */}
    </form>
  );
}
```

### Todo List

```typescript
import { useTodos } from '@/hooks/useTodos';

function Dashboard() {
  const { todos, loading, error, createTodo, toggleComplete } = useTodos({
    status: 'pending',
    limit: 20,
  });

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage>{error}</ErrorMessage>;

  return (
    <div>
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={() => toggleComplete(todo.id, todo.status === 'pending')}
        />
      ))}
    </div>
  );
}
```

### AI Features

```typescript
import { aiApi } from '@/lib/api';

function AIAssistant() {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<AIGeneratedTodo[]>([]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await aiApi.generateTodos('Plan a birthday party');
      setSuggestions(response.todos);
    } catch (err) {
      console.error('AI generation failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        Generate Suggestions
      </button>
      {suggestions.map((todo, i) => (
        <div key={i}>
          <h3>{todo.title}</h3>
          <p>{todo.description}</p>
          <span>{todo.priority}</span>
        </div>
      ))}
    </div>
  );
}
```

---

## Error Handling

All API errors throw `ApiError` with:

- `message`: Human-readable error message
- `status`: HTTP status code

Example error handling:

```typescript
import { ApiError } from '@/lib/api';

try {
  await todosApi.create(todoData);
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      // Redirect to login
      router.push('/login');
    } else if (error.status === 429) {
      // Rate limited
      showToast('Too many requests. Try again later.');
    } else {
      // Other error
      showToast(error.message);
    }
  }
}
```

---

**Last Updated**: 2025-01-23
