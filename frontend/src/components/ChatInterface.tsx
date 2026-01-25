// Implements: T036-T043
// Phase III - AI-Powered Todo Chatbot
// ChatInterface Component - Full implementation with API integration

import React, { useState, useRef, useEffect } from 'react';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const detectLanguage = (text: string): 'en' | 'ur' => {
    // Urdu Unicode range
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

    // Add user message to chat
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    inputRef.current?.focus();

    try {
      // Call Phase III backend API
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

      // Log tool calls for debugging
      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log('Tool calls executed:', data.tool_calls);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Error sending message:', err);

      // Add error message to chat
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

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>AI Task Assistant</h2>
        <p>Manage tasks in English or Urdu</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Start a conversation...</p>
            <p>Try: "Add a task to buy milk" or "دودھ لینے کا ٹاسک شامل کرو"</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-content">{msg.content}</div>
            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant-message">
            <div className="typing-indicator">Thinking...</div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          ref={inputRef}
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            detectLanguage(inputMessage) === 'ur'
              ? 'اپنا میسج ٹائپ کریں...'
              : 'Type your message...'
          }
          disabled={isLoading}
          maxLength={1000}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputMessage.trim()}
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>

      <style jsx>{`
        .chat-interface {
          display: flex;
          flex-direction: column;
          height: 600px;
          max-width: 800px;
          margin: 0 auto;
          border: 1px solid #ccc;
          border-radius: 8px;
          overflow: hidden;
        }

        .chat-header {
          background: #f5f5f5;
          padding: 16px;
          border-bottom: 1px solid #ddd;
        }

        .chat-header h2 {
          margin: 0 0 8px 0;
          font-size: 20px;
        }

        .chat-header p {
          margin: 0;
          color: #666;
          font-size: 14px;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .empty-state {
          text-align: center;
          color: #999;
          padding: 40px 20px;
        }

        .message {
          max-width: 70%;
          padding: 12px 16px;
          border-radius: 12px;
        }

        .user-message {
          align-self: flex-end;
          background: #007bff;
          color: white;
        }

        .assistant-message {
          align-self: flex-start;
          background: #f0f0f0;
          color: #333;
        }

        .message-content {
          margin-bottom: 4px;
        }

        .message-timestamp {
          font-size: 11px;
          opacity: 0.7;
        }

        .typing-indicator {
          color: #666;
          font-style: italic;
        }

        .error-message {
          align-self: center;
          background: #f8d7da;
          color: #721c24;
          padding: 12px 16px;
          border-radius: 8px;
          margin: 8px 0;
        }

        .chat-input {
          display: flex;
          padding: 16px;
          border-top: 1px solid #ddd;
          gap: 8px;
        }

        .chat-input input {
          flex: 1;
          padding: 12px;
          border: 1px solid #ccc;
          border-radius: 6px;
          font-size: 14px;
        }

        .chat-input button {
          padding: 12px 24px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        }

        .chat-input button:hover:not(:disabled) {
          background: #0056b3;
        }

        .chat-input button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
