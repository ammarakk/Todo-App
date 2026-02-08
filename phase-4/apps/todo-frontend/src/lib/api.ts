/**
 * API client for communicating with the backend
 * Direct calls to HuggingFace backend with proper CORS handling
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://ammaraak-todo-api.hf.space';

/**
 * API error class
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Make a fetch request to the API
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Ensure endpoint starts with /api/
  let cleanEndpoint = endpoint.startsWith('/api/') ? endpoint : `/api${endpoint}`;

  // HuggingFace Spaces has inconsistent trailing slash behavior:
  // - Auth endpoints (/api/auth/*) should NOT have trailing slashes
  // - Other endpoints (/api/todos, /api/users/*) SHOULD have trailing slashes
  const isAuthEndpoint = cleanEndpoint.startsWith('/api/auth/');
  if (!isAuthEndpoint && !cleanEndpoint.endsWith('/')) {
    cleanEndpoint += '/';
  }

  const url = `${API_BASE}${cleanEndpoint}`;

  // Get token from localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json();

  // Handle error responses
  if (!response.ok) {
    throw new ApiError(
      data.detail || 'An error occurred',
      response.status,
      data.detail
    );
  }

  return data;
}

/**
 * Auth API
 */
export const authApi = {
  async signup(data: { name: string; email: string; password: string }) {
    return fetchAPI<{ access_token: string; token_type: string; user: any }>(
      '/auth/signup',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  async login(data: { email: string; password: string }) {
    return fetchAPI<{ access_token: string; token_type: string; user: any }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  async logout() {
    return fetchAPI<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
  },

  async getCurrentUser(token: string) {
    return fetchAPI<any>('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

/**
 * Todos API
 */
export const todosApi = {
  async list(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
    search?: string;
    sort_by?: string;
  }) {
    const queryParams: Record<string, string> = {};
    if (params?.skip !== undefined) queryParams.skip = params.skip.toString();
    if (params?.limit !== undefined) queryParams.limit = params.limit.toString();
    if (params?.status) queryParams.status = params.status;
    if (params?.priority) queryParams.priority = params.priority;
    if (params?.search) queryParams.search = params.search;
    if (params?.sort_by) queryParams.sort_by = params.sort_by;

    const queryString = Object.keys(queryParams).length > 0
      ? '?' + new URLSearchParams(queryParams).toString()
      : '';

    return fetchAPI<{ todos: any[] }>('/todos' + queryString);
  },

  async get(id: string) {
    return fetchAPI<any>(`/todos/${id}`);
  },

  async create(data: {
    title: string;
    description?: string;
    priority?: string;
    due_date?: string;
    tags?: string[];
  }) {
    return fetchAPI<any>('/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async update(id: string, data: Partial<any>) {
    return fetchAPI<any>(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete(id: string) {
    return fetchAPI<{ message: string }>(`/todos/${id}`, {
      method: 'DELETE',
    });
  },

  async toggleComplete(id: string, completed: boolean) {
    return fetchAPI<any>(`/todos/${id}/complete?completed=${completed}`, {
      method: 'PATCH',
    });
  },
};

/**
 * Users API
 */
export const usersApi = {
  async getProfile() {
    return fetchAPI<any>('/users/me');
  },

  async updateProfile(data: { name?: string; avatar_url?: string }) {
    return fetchAPI<any>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async uploadAvatar(file: File) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/users/me/avatar/`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new ApiError(data.detail || 'Upload failed', response.status, data.detail);
    }

    return data;
  },
};

/**
 * AI Chat API
 */
export const aiApi = {
  async chat(message: string, context?: any) {
    return fetchAPI<any>('/ai-chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },

  async sendCommand(message: string, conversationId: string = 'new') {
    return fetchAPI<any>('/ai-chat/command', {
      method: 'POST',
      body: JSON.stringify({ message, conversationId }),
    });
  },
};

// Legacy exports for backward compatibility
export const api = {
  login: authApi.login,
  signup: authApi.signup,
  logout: authApi.logout,
  getCurrentUser: authApi.getCurrentUser,
};
