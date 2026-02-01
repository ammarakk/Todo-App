'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

interface CreateTodoModalProps {
  onClose: () => void;
  onCreate: (todoData: any) => Promise<void>;
}

export function CreateTodoModal({ onClose, onCreate }: CreateTodoModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      await onCreate({
        title: title.trim(),
        description: description.trim() || null,
        priority,
        due_date: dueDate || null,
        tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : null,
      });
      // Clear form on success
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
      setTags('');
      // Success - modal will close via onCreate callback
    } catch (error: any) {
      console.error('Failed to create todo:', error);
      setErrorMessage(error?.message || 'Failed to create todo. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const priorityStyles = {
    low: {
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
      border: 'border-emerald-200 dark:border-emerald-800',
      text: 'text-emerald-700 dark:text-emerald-300',
      selected: 'bg-emerald-500 border-emerald-500 text-white dark:shadow-[0_0_15px_rgba(16,185,129,0.6)]'
    },
    medium: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      border: 'border-amber-200 dark:border-amber-800',
      text: 'text-amber-700 dark:text-amber-300',
      selected: 'bg-amber-500 border-amber-500 text-white dark:shadow-[0_0_15px_rgba(245,158,11,0.6)]'
    },
    high: {
      bg: 'bg-rose-50 dark:bg-rose-900/20',
      border: 'border-rose-200 dark:border-rose-800',
      text: 'text-rose-700 dark:text-rose-300',
      selected: 'bg-rose-500 border-rose-500 text-white dark:shadow-[0_0_15px_rgba(244,63,94,0.6)]'
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4"
        onClick={onClose}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-md max-h-[90vh] sm:max-h-[85vh] flex flex-col"
        >
          <div className="bg-white dark:bg-gray-900/90 backdrop-blur-sm rounded-2xl shadow-2xl dark:shadow-[0_0_40px_rgba(6,182,212,0.3)] flex flex-col overflow-hidden max-h-[90vh] sm:max-h-[85vh] border dark:border-cyan-500/30">
            {/* Header */}
            <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 sm:px-5 sm:py-4 border-b border-gray-200 dark:border-cyan-500/30 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-900 dark:shadow-[0_0_20px_rgba(6,182,212,0.2)]">
              <div>
                <h2 className="text-base sm:text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-cyan-400 dark:to-purple-400 bg-clip-text text-transparent dark:drop-shadow-[0_0_10px_rgba(6,182,212,0.5)]">
                  Create New Todo
                </h2>
              </div>
              <button
                onClick={onClose}
                className="flex-shrink-0 p-1 rounded-lg hover:bg-gray-200 dark:hover:bg-cyan-500/20 transition-all dark:hover:shadow-[0_0_10px_rgba(6,182,212,0.4)]"
              >
                <X className="w-4 h-4 text-gray-600 dark:text-cyan-400" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
              {/* Error Message */}
              {errorMessage && (
                <div className="flex-shrink-0 px-4 py-3 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
                  <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
                </div>
              )}
              <div className="flex-1 overflow-y-auto">
                <div className="p-4 space-y-3">
                  {/* Title */}
                  <div>
                    <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-cyan-400 mb-1">
                      <span className="w-1 h-3 bg-blue-500 dark:bg-cyan-400 rounded-full dark:shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                      Title <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      required
                      placeholder="What needs to be done?"
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-cyan-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 dark:focus:shadow-[0_0_10px_rgba(6,182,212,0.5)] bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-purple-400 mb-1">
                      <span className="w-1 h-3 bg-purple-500 dark:bg-purple-400 rounded-full dark:shadow-[0_0_8px_rgba(192,132,252,0.8)]"></span>
                      Description
                    </label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={2}
                      placeholder="Add details..."
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-purple-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-purple-500 dark:focus:shadow-[0_0_10px_rgba(192,132,252,0.5)] bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none transition-all"
                    />
                  </div>

                  {/* Priority */}
                  <div>
                    <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-amber-400 mb-1">
                      <span className="w-1 h-3 bg-amber-500 dark:bg-amber-400 rounded-full dark:shadow-[0_0_8px_rgba(251,191,36,0.8)]"></span>
                      Priority
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {(['low', 'medium', 'high'] as const).map((p) => {
                        const styles = priorityStyles[p];
                        const isSelected = priority === p;
                        return (
                          <button
                            key={p}
                            type="button"
                            onClick={() => setPriority(p)}
                            className={`
                              py-2 px-2 sm:px-3 rounded-lg font-semibold text-xs transition-all
                              ${isSelected ? styles.selected : `${styles.bg} ${styles.text} border border-gray-300 dark:border-gray-600`}
                            `}
                          >
                            {p.charAt(0).toUpperCase() + p.slice(1)}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Due Date & Tags */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-green-400 mb-1">
                        <span className="w-1 h-3 bg-green-500 dark:bg-green-400 rounded-full dark:shadow-[0_0_8px_rgba(74,222,128,0.8)]"></span>
                        Due Date
                      </label>
                      <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        className="w-full px-2 sm:px-3 py-2 text-xs border border-gray-300 dark:border-green-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-green-500 dark:focus:shadow-[0_0_10px_rgba(74,222,128,0.5)] bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
                      />
                      {dueDate && (
                        <div className="mt-1.5 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-md border border-blue-200 dark:border-blue-800">
                          <div className="flex items-center gap-1.5 text-xs text-blue-700 dark:text-blue-300">
                            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                            <span className="font-medium">Reminder email will be sent 1 day before</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 dark:text-pink-400 mb-1">
                        <span className="w-1 h-3 bg-pink-500 dark:bg-pink-400 rounded-full dark:shadow-[0_0_8px_rgba(244,114,182,0.8)]"></span>
                        Tags
                      </label>
                      <input
                        type="text"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        placeholder="work"
                        className="w-full px-2 sm:px-3 py-2 text-xs border border-gray-300 dark:border-pink-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-pink-500 dark:focus:shadow-[0_0_10px_rgba(244,114,182,0.5)] bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions - Fixed at bottom */}
              <div className="flex-shrink-0 flex gap-2 p-3 sm:p-4 border-t border-gray-200 dark:border-cyan-500/30 bg-gray-50 dark:bg-gray-900/50">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 py-2 px-3 sm:px-4 text-sm font-semibold border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !title.trim()}
                  className="flex-1 py-2 px-3 sm:px-4 text-sm font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-cyan-500 dark:to-purple-500 hover:from-blue-700 hover:to-purple-700 dark:hover:from-cyan-400 dark:hover:to-purple-400 text-white rounded-lg shadow-lg dark:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed dark:disabled:shadow-none"
                >
                  {isSubmitting ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
