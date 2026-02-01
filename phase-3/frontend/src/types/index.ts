/**
 * TypeScript type definitions for the Todo App.
 */

/**
 * User entity
 */
export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Auth response with token
 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Signup request
 */
export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

/**
 * Login request
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
  error_code?: string;
}

/**
 * Todo priority
 */
export type TodoPriority = 'low' | 'medium' | 'high';

/**
 * Todo status
 */
export type TodoStatus = 'pending' | 'completed';

/**
 * Todo entity
 */
export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: TodoStatus;
  priority: TodoPriority;
  due_date?: string;
  completed_at?: string;
  user_id: string;
  tags?: string[];
  reminder_sent?: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Create todo request
 */
export interface CreateTodoRequest {
  title: string;
  description?: string;
  priority?: TodoPriority;
  due_date?: string;
  tags?: string[];
}

/**
 * Update todo request
 */
export interface UpdateTodoRequest {
  title?: string;
  description?: string;
  status?: TodoStatus;
  priority?: TodoPriority;
  due_date?: string;
}
