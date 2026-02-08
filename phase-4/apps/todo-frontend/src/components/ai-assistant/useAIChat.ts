'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { aiApi } from '@/lib/api';

/**
 * T023: useAIChat hook
 * Manages AI chat state and communication
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  actionType?: 'create_task' | 'list_tasks' | 'update_task' | 'delete_task' | 'complete_task' | 'clarify';
  taskData?: any;
}

export interface UseAIChatOptions {
  onActionExecuted?: (action: string, data?: any) => void;
}

export function useAIChat(options: UseAIChatOptions = {}) {
  const { onActionExecuted } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string>('new');
  const [isOpen, setIsOpen] = useState(false);

  // Use ref to avoid stale closures
  const messagesRef = useRef(messages);
  const conversationIdRef = useRef(conversationId);

  // Keep refs in sync
  useEffect(() => {
    messagesRef.current = messages;
    conversationIdRef.current = conversationId;
  }, [messages, conversationId]);

  // T038: Load conversation from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedConversationId = localStorage.getItem('ai_chat_conversation_id');
      const savedMessages = localStorage.getItem('ai_chat_messages');

      if (savedConversationId) {
        setConversationId(savedConversationId);
        conversationIdRef.current = savedConversationId;
      }

      if (savedMessages) {
        try {
          const parsed = JSON.parse(savedMessages);
          setMessages(parsed);
        } catch (e) {
          console.error('Failed to parse saved messages:', e);
        }
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined' && messages.length > 0) {
      localStorage.setItem('ai_chat_messages', JSON.stringify(messages));
    }
  }, [messages]);

  // Save conversation ID to localStorage
  const saveConversationId = useCallback((id: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('ai_chat_conversation_id', id);
    }
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}-user`,
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        // Call AI API
        console.log('Sending AI command:', content, 'conversationId:', conversationIdRef.current);
        const response = await aiApi.sendCommand(content, conversationIdRef.current);
        console.log('AI Response:', response);

        // Update conversation ID if new
        if (conversationIdRef.current === 'new' && response.data?.conversation_id) {
          const newConvId = response.data.conversation_id;
          setConversationId(newConvId);
          conversationIdRef.current = newConvId;
          saveConversationId(newConvId);
        }

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now()}-assistant`,
          role: 'assistant',
          content: response.message || response.reply || 'No response from AI',
          timestamp: new Date().toISOString(),
          actionType: response.action as any,
          taskData: response.data,
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Trigger action callback if AI executed an action
        if (response.action && response.action !== 'clarify') {
          onActionExecuted?.(response.action, response.data);
        }

        // Return response for caller to handle
        return response;
      } catch (err) {
        console.error('AI chat error:', err);
        const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
        setError(errorMessage);

        // Add error message as system message
        const systemMessage: ChatMessage = {
          id: `msg-${Date.now()}-system`,
          role: 'system',
          content: errorMessage,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, systemMessage]);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, onActionExecuted, saveConversationId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setConversationId('new');
    setError(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('ai_chat_messages');
      localStorage.removeItem('ai_chat_conversation_id');
    }
  }, []);

  const openChat = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    isOpen,
    sendMessage,
    clearMessages,
    openChat,
    closeChat,
  };
}
