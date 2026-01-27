'use client';

import { useState, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';

/**
 * T022: ChatInput component
 * Input field for user messages with send button
 */
export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = 'Ask me to create, update, or manage your tasks...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled && !isLoading) {
      onSend(trimmed);
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-2 items-end p-3 md:p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700"
    >
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={1}
        className="flex-1 px-3 md:px-4 py-2 md:py-3 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:focus:ring-cyan-400 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 text-sm md:text-base"
        style={{
          minHeight: '40px',
          maxHeight: '100px',
        }}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = 'auto';
          target.style.height = `${Math.min(target.scrollHeight, 100)}px`;
        }}
      />
      <button
        onClick={handleSend}
        disabled={disabled || isLoading || !message.trim()}
        className="px-3 md:px-4 py-2 md:py-3 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed dark:shadow-[0_0_10px_rgba(6,182,212,0.3)] dark:hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] flex-shrink-0 min-w-[40px] md:min-w-[60px]"
        aria-label="Send message"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 md:w-5 md:h-5 animate-spin" />
        ) : (
          <Send className="w-4 h-4 md:w-5 md:h-5" />
        )}
      </button>
    </motion.div>
  );
}
