'use client';

// Phase III - AI-Powered Todo Chatbot
// Advanced ChatInterface - Modern, professional UI with animations

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Trash2, Copy, Check } from 'lucide-react';
import RobotAvatar from './RobotAvatar';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tool_calls?: any[];
}

interface ChatResponse {
  reply: string;
  conversation_id: string;
  tool_calls?: any[];
}

interface ChatInterfaceProps {
  jwtToken: string;
  apiBaseUrl?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  jwtToken,
  apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const detectLanguage = (text: string): 'en' | 'ur' => {
    const urduPattern = /[\u0600-\u06FF]/;
    return urduPattern.test(text) ? 'ur' : 'en';
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) {
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    inputRef.current?.focus();

    try {
      const response = await fetch(`${apiBaseUrl}/api/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data: ChatResponse = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.reply,
        timestamp: new Date(),
        tool_calls: data.tool_calls
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setConversationId(data.conversation_id);

      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log('Tool calls executed:', data.tool_calls);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      const errorMessageObj: Message = {
        role: 'assistant',
        content: `❌ Error: ${errorMessage}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    inputRef.current?.focus();
  };

  const handleCopyMessage = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const suggestions = [
    { text: 'Add a task to buy milk', lang: 'en' },
    { text: 'میرے ٹاسک دکھاؤ', lang: 'ur' },
    { text: 'Show my pending tasks', lang: 'en' },
    { text: 'ہائی پرئورٹی ٹاسک شامل کرو', lang: 'ur' },
  ];

  const currentLang = detectLanguage(inputMessage);

  return (
    <div ref={containerRef} className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl blur-lg opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
                <RobotAvatar size={32} isThinking={isLoading} />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                AI Assistant
                <Sparkles className="w-4 h-4 text-yellow-500" />
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {currentLang === 'ur' ? 'اردو میں بات کریں' : 'Chat in English or Urdu'}
              </p>
            </div>
          </div>

          <button
            onClick={handleClearChat}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="mb-6">
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-full">
                    <RobotAvatar size={64} />
                  </div>
                </div>
              </div>

              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {currentLang === 'ur' ? 'آپ کا AI مددگار' : 'Your AI Assistant'}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                {currentLang === 'ur'
                  ? 'قدمی بات سے ٹاسک منیج کریں'
                  : 'Manage tasks with natural conversation'}
              </p>

              <div className="grid grid-cols-1 gap-2">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                  {currentLang === 'ur' ? 'مثالیں:' : 'Try these:'}
                </p>
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputMessage(suggestion.text)}
                    className="text-left px-4 py-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all text-sm text-gray-700 dark:text-gray-300 hover:shadow-md"
                  >
                    "{suggestion.text}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`flex gap-3 max-w-[80%] ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div className="flex-shrink-0">
                  {message.role === 'user' ? (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                      <RobotAvatar size={24} isThinking={false} />
                    </div>
                  )}
                </div>

                {/* Message */}
                <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`px-5 py-3 rounded-2xl shadow-lg ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                        : 'bg-white dark:bg-slate-800 text-gray-900 dark:text-white border border-slate-200 dark:border-slate-700'
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed">
                      {message.content}
                    </p>
                  </div>

                  {/* Timestamp & Actions */}
                  <div className="flex items-center gap-2 mt-1 px-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>

                    {message.role === 'assistant' && (
                      <button
                        onClick={() => handleCopyMessage(message.content, index)}
                        className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded transition-colors"
                        title="Copy message"
                      >
                        {copiedIndex === index ? (
                          <Check className="w-3 h-3 text-green-500" />
                        ) : (
                          <Copy className="w-3 h-3 text-gray-400" />
                        )}
                      </button>
                    )}
                  </div>

                  {/* Tool Calls Indicator */}
                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                      <Sparkles className="w-3 h-3" />
                      <span>{message.tool_calls.length} tool(s) executed</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="flex gap-3 max-w-[80%]">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                <RobotAvatar size={24} isThinking={true} />
              </div>
              <div className="bg-white dark:bg-slate-800 px-5 py-4 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-purple-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {currentLang === 'ur' ? 'سوچ رہا ہے...' : 'Thinking...'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 animate-fade-in">
          <p className="text-sm text-red-600 dark:text-red-400 text-center">{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 p-4 shadow-lg">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                currentLang === 'ur'
                  ? 'اپنا میسج ٹائپ کریں...'
                  : 'Type your message...'
              }
              disabled={isLoading}
              maxLength={1000}
              className="w-full px-5 py-4 bg-slate-100 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 rounded-2xl border-2 border-transparent focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all pr-12 text-[15px]"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
              {inputMessage.length}/1000
            </div>
          </div>

          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">{currentLang === 'ur' ? 'بھیجیں' : 'Send'}</span>
              </>
            )}
          </button>
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <p>
            {currentLang === 'ur'
              ? 'قانونی طور پر: انگریزی یا اردو میں بات کریں'
              : 'Press Enter to send • Shift+Enter for new line • Supports English & Urdu'}
          </p>
          <p className="hidden sm:block">
            {conversationId ? `Session: ${conversationId.slice(0, 8)}...` : 'New session'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
