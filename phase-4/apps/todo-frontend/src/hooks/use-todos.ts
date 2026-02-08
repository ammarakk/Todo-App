'use client';

import { useState, useEffect } from 'react';
import { todosApi, ApiError } from '@/lib/api';
import type { Todo, TodoPriority, CreateTodoRequest } from '@/types';

interface TodoListParams {
  skip?: number;
  limit?: number;
  status?: 'all' | 'pending' | 'completed';
  priority?: string;
  search?: string;
  sort_by?: 'created_at' | 'due_date' | 'priority';
}

export function useTodos(params: TodoListParams = {}) {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTodos();
  }, [params.skip, params.limit, params.status, params.priority, params.search, params.sort_by]);

  async function fetchTodos() {
    setLoading(true);
    setError(null);
    try {
      console.log('[useTodos] Fetching todos with params:', params);
      const response = await todosApi.list(params);
      console.log('[useTodos] API Response:', response);

      // Handle both response formats
      if (Array.isArray(response)) {
        console.log('[useTodos] Response is array, setting todos directly');
        setTodos(response);
      } else if (response && typeof response === 'object' && 'todos' in response) {
        console.log('[useTodos] Response has todos property');
        setTodos(response.todos);
      } else {
        console.warn('[useTodos] Unexpected response format:', response);
        setTodos([]);
      }
    } catch (err: any) {
      console.error('[useTodos] Fetch error:', err);
      // Show more detailed error info
      let message = 'Failed to fetch todos';
      if (err?.message) {
        message = err.message;
      } else if (err?.detail) {
        message = err.detail;
      } else if (typeof err === 'string') {
        message = err;
      }
      console.error('[useTodos] Error message to display:', message);
      setError(message);
      setTodos([]); // Set empty array on error to prevent crashes
    } finally {
      setLoading(false);
    }
  }

  async function createTodo(todoData: {
    title: string;
    description?: string | null;
    priority?: string;
    due_date?: string | null;
    tags?: string[] | null;
  }) {
    setError(null);
    try {
      // Build API data - omit undefined fields
      const apiData: CreateTodoRequest = {
        title: todoData.title,
      };

      // Only add optional fields if they have values
      if (todoData.description) {
        apiData.description = todoData.description;
      }
      if (todoData.priority) {
        apiData.priority = todoData.priority as TodoPriority;
      }
      if (todoData.due_date) {
        apiData.due_date = todoData.due_date;
      }
      if (todoData.tags && todoData.tags.length > 0) {
        apiData.tags = todoData.tags;
      }

      console.log('Sending todo data:', JSON.stringify(apiData, null, 2));
      const newTodo = await todosApi.create(apiData);
      setTodos([newTodo, ...todos]);
      return newTodo;
    } catch (err: any) {
      console.error('Create todo error:', err);
      const message = err instanceof ApiError ? err.message : 'Failed to create todo';
      setError(message);
      throw err;
    }
  }

  async function updateTodo(id: string, data: Partial<Todo>) {
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
    loading,
    error,
    createTodo,
    updateTodo,
    deleteTodo,
    toggleComplete,
    refetch: fetchTodos,
  };
}
