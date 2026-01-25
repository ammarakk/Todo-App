'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

import { api } from '@/lib/api';
import { clearAuth, getToken, getUser, isAuthenticated, setToken, setUser } from '@/lib/auth';
import type { User, LoginRequest, SignupRequest } from '@/types';

/**
 * Auth context interface
 */
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  loading: boolean; // Alias for isLoading
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  error?: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth provider props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth provider component
 *
 * Manages authentication state and provides auth methods to child components.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      if (isAuthenticated()) {
        const token = getToken();
        const savedUser = getUser();

        if (token && savedUser) {
          setUserState(savedUser);

          // Verify token is still valid
          try {
            const currentUser = await api.getCurrentUser(token);
            setUserState(currentUser);
            setUser(currentUser);
          } catch {
            // Token invalid, clear auth
            clearAuth();
            setUserState(null);
          }
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Login with email and password
   */
  const login = async (credentials: LoginRequest) => {
    const response = await api.login(credentials);
    setToken(response.access_token);
    setUser(response.user);
    setUserState(response.user);
  };

  /**
   * Signup with name, email, and password
   */
  const signup = async (data: SignupRequest) => {
    const response = await api.signup(data);
    setToken(response.access_token);
    setUser(response.user);
    setUserState(response.user);
  };

  /**
   * Logout current user
   */
  const logout = async () => {
    const token = getToken();
    if (token) {
      try {
        await api.logout(token);
      } catch {
        // Ignore logout errors
      }
    }
    clearAuth();
    setUserState(null);
  };

  /**
   * Refresh user data from server
   */
  const refreshUser = async () => {
    const token = getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const currentUser = await api.getCurrentUser(token);
    setUser(currentUser);
    setUserState(currentUser);
  };

  const value: AuthContextType = {
    user,
    isLoading,
    loading: isLoading,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
    refreshUser,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 *
 * @throws Error if used outside AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
