'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Check, Trash2, Calendar, Tag } from 'lucide-react';
import { format } from 'date-fns';
import type { Todo } from '@/types';

interface TodoListProps {
  todos: Todo[];
  loading: boolean;
  onToggleComplete: (todoId: string, completed: boolean) => void;
  onDelete: (todoId: string) => void;
}

const priorityColors = {
  high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:shadow-[0_0_10px_rgba(248,113,113,0.5)]',
  medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 dark:shadow-[0_0_10px_rgba(251,191,36,0.5)]',
  low: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 dark:shadow-[0_0_10px_rgba(74,222,128,0.5)]',
};

export function TodoList({ todos, loading, onToggleComplete, onDelete }: TodoListProps) {
  if (loading) {
    return (
      <div className="mt-8 flex justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <div className="mt-8 text-center py-12">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No todos yet
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Create your first todo to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="mt-8 space-y-4">
      <AnimatePresence>
        {todos.map((todo) => (
          <motion.div
            key={todo.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className={`bg-white dark:bg-gray-900/80 rounded-lg p-4 border backdrop-blur-sm ${
              todo.status === 'completed'
                ? 'border-gray-200 dark:border-gray-700 opacity-75'
                : 'border-gray-300 dark:border-cyan-500/50 dark:shadow-[0_0_15px_rgba(6,182,212,0.3)]'
            } shadow-sm hover:shadow-lg dark:hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transition-all duration-300`}
          >
            <div className="flex items-start gap-4">
              {/* Checkbox */}
              <button
                onClick={() => onToggleComplete(todo.id, todo.status !== 'completed')}
                className={`mt-1 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                  todo.status === 'completed'
                    ? 'bg-green-500 border-green-500 dark:shadow-[0_0_10px_rgba(34,197,94,0.8)]'
                    : 'border-gray-300 dark:border-cyan-500/50 hover:border-green-500 dark:hover:border-cyan-400 dark:hover:shadow-[0_0_10px_rgba(6,182,212,0.6)]'
                }`}
              >
                {todo.status === 'completed' && <Check className="w-4 h-4 text-white" />}
              </button>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3
                      className={`text-lg font-semibold mb-1 ${
                        todo.status === 'completed'
                          ? 'text-gray-500 dark:text-gray-400 line-through'
                          : 'text-gray-900 dark:text-white'
                      }`}
                    >
                      {todo.title}
                    </h3>
                    {todo.description && (
                      <p
                        className={`text-sm mb-2 ${
                          todo.status === 'completed'
                            ? 'text-gray-400 dark:text-gray-500'
                            : 'text-gray-600 dark:text-gray-400'
                        }`}
                      >
                        {todo.description}
                      </p>
                    )}

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-2 items-center">
                      {/* Priority Badge */}
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${priorityColors[todo.priority as keyof typeof priorityColors]}`}
                      >
                        {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
                      </span>

                      {/* Due Date */}
                      {todo.due_date && (
                        <span className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                          <Calendar className="w-3 h-3" />
                          {format(new Date(todo.due_date), 'MMM d, yyyy')}
                          {!todo.reminder_sent && todo.status !== 'completed' && (
                            <span
                              className="ml-1 text-blue-500 dark:text-blue-400"
                              title="Reminder scheduled"
                            >
                              🔔
                            </span>
                          )}
                        </span>
                      )}

                      {/* Tags */}
                      {todo.tags && todo.tags.length > 0 && (
                        <div className="flex items-center gap-1">
                          <Tag className="w-3 h-3 text-gray-400" />
                          {todo.tags.slice(0, 2).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                            >
                              {tag}
                            </span>
                          ))}
                          {todo.tags.length > 2 && (
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              +{todo.tags.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={() => onDelete(todo.id)}
                    className="flex-shrink-0 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all dark:hover:shadow-[0_0_10px_rgba(239,68,68,0.5)]"
                    aria-label="Delete todo"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
