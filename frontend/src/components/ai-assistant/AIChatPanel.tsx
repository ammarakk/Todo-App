'use client';

import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Minimize2, Maximize2, Sparkles } from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useAIChat, ChatMessage as ChatMessageType } from './useAIChat';

/**
 * T020: AIChatPanel component
 * Floating modal panel for AI chat interface
 */
export interface AIChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onActionExecuted?: (action: string, data?: any) => void;
}

export function AIChatPanel({ isOpen, onClose, onActionExecuted }: AIChatPanelProps) {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    openChat,
    closeChat,
  } = useAIChat({
    onActionExecuted,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isMinimized, setIsMinimized] = useState(false);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sync isOpen state
  useEffect(() => {
    if (isOpen) {
      openChat();
    } else {
      closeChat();
    }
  }, [isOpen, openChat, closeChat]);

  const handleSendMessage = async (content: string) => {
    try {
      await sendMessage(content);
    } catch (err) {
      // Error already handled in useAIChat
      console.error('Failed to send message:', err);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{
            opacity: 1,
            scale: 1,
            y: 0,
            height: isMinimized ? 'auto' : '600px',
          }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className="fixed bottom-20 left-3 right-3 sm:left-auto sm:right-4 max-w-md w-auto max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-900 rounded-2xl shadow-2xl dark:shadow-[0_0_40px_rgba(6,182,212,0.3)] border border-gray-200 dark:border-cyan-500/30 flex flex-col z-50"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-cyan-500 to-purple-600 dark:from-cyan-600 dark:to-purple-700">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white dark:border-gray-900" />
              </div>
              <div>
                <h3 className="text-white font-semibold">AI Assistant</h3>
                <p className="text-cyan-100 text-xs">
                  {isLoading ? 'Thinking...' : 'Ask me anything about your tasks'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                aria-label={isMinimized ? 'Maximize' : 'Minimize'}
              >
                {isMinimized ? (
                  <Maximize2 className="w-5 h-5 text-white" />
                ) : (
                  <Minimize2 className="w-5 h-5 text-white" />
                )}
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                aria-label="Close chat"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800/50">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center p-8">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 dark:shadow-[0_0_20px_rgba(6,182,212,0.5)] flex items-center justify-center mb-4">
                      <Sparkles className="w-8 h-8 text-white" />
                    </div>
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Your AI Assistant
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      I can help you manage your tasks using natural language
                    </p>
                    <div className="text-xs text-left bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 w-full">
                      <p className="font-semibold text-gray-900 dark:text-white mb-2">
                        Try saying:
                      </p>
                      <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                        <li>"Create a task to buy groceries"</li>
                        <li>"Show my pending tasks"</li>
                        <li>"Mark task 1 as completed"</li>
                        <li>"Delete task 2"</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((message: ChatMessageType) => (
                      <ChatMessage
                        key={message.id}
                        role={message.role}
                        content={message.content}
                        timestamp={message.timestamp}
                        isLoading={message.role === 'assistant' && isLoading}
                      />
                    ))}
                    {isLoading && (
                      <ChatMessage
                        key="loading"
                        role="assistant"
                        content="Thinking..."
                        isLoading
                      />
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* T029: Error Display */}
              {error && (
                <div className="px-4 py-3 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
                  <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              )}

              {/* Input Area */}
              <ChatInput
                onSend={handleSendMessage}
                disabled={isLoading}
                isLoading={isLoading}
              />

              {/* Clear Conversation Button */}
              {messages.length > 0 && (
                <div className="px-4 py-2 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={clearMessages}
                    className="text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
                  >
                    Clear conversation
                  </button>
                </div>
              )}
            </>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Import useState for isMinimized
import { useState } from 'react';
