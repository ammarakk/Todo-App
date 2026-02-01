'use client';

import { motion } from 'framer-motion';
import { Bot, User, CheckCircle2, AlertCircle, Loader2, Circle } from 'lucide-react';

/**
 * T021: ChatMessage component
 * Displays individual chat messages with role-based styling
 * T036/T037: Enhanced to display task lists and action confirmations
 */
export interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  isLoading?: boolean;
  actionType?: 'create_task' | 'list_tasks' | 'update_task' | 'delete_task' | 'complete_task' | 'clarify';
  taskData?: any;
}

export function ChatMessage({ role, content, timestamp, isLoading, actionType, taskData }: ChatMessageProps) {
  const isUser = role === 'user';
  const isSystem = role === 'system';

  // T037: Action confirmation icons
  const getActionIcon = () => {
    switch (actionType) {
      case 'create_task':
      case 'complete_task':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'delete_task':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'update_task':
        return <CheckCircle2 className="w-4 h-4 text-blue-500" />;
      default:
        return null;
    }
  };

  // T036: Format task lists
  const formatContent = () => {
    if (actionType === 'list_tasks' && taskData?.tasks) {
      const tasks = taskData.tasks;
      return (
        <div className="space-y-2">
          <p className="text-sm font-semibold mb-2">Here are your tasks:</p>
          {tasks.map((task: any, index: number) => (
            <div
              key={task.id || index}
              className="flex items-start gap-2 p-2 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <Circle
                className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                  task.status === 'completed'
                    ? 'text-green-500 fill-green-500'
                    : 'text-gray-400'
                }`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {task.title}
                </p>
                {task.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    {task.description}
                  </p>
                )}
                <div className="flex gap-2 mt-1">
                  {task.priority && (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                      {task.priority}
                    </span>
                  )}
                  {task.due_date && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }

    // T037: Add confirmation icon for actions
    if (actionType && actionType !== 'clarify' && actionType !== 'list_tasks') {
      return (
        <div className="flex items-start gap-2">
          {getActionIcon()}
          <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
        </div>
      );
    }

    // Default: plain text
    return <p className="text-sm whitespace-pre-wrap break-words">{content}</p>;
  };

  // System message styling (warnings/errors)
  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center my-4"
      >
        <div className="flex items-center gap-2 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg max-w-md">
          <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
          <p className="text-sm text-yellow-800 dark:text-yellow-200">{content}</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-purple-600'
            : 'bg-gradient-to-br from-cyan-500 to-purple-600 dark:shadow-[0_0_10px_rgba(6,182,212,0.5)]'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : isLoading ? (
          <Loader2 className="w-4 h-4 text-white animate-spin" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[75%]`}
      >
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-br-md'
              : 'bg-gray-100 dark:bg-gray-800 dark:border dark:border-cyan-500/30 text-gray-900 dark:text-gray-100 rounded-bl-md'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <p className="text-sm">Thinking...</p>
            </div>
          ) : (
            formatContent()
          )}
        </div>

        {/* Timestamp */}
        {timestamp && !isLoading && (
          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 px-2">
            {new Date(timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        )}
      </div>
    </motion.div>
  );
}
