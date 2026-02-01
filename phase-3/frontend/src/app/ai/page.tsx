'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/use-auth';
import { Header } from '@/components/common/Header';
import { aiApi } from '@/lib/api';
import { Loader2, Sparkles, CheckCircle, List, TrendingUp } from 'lucide-react';

type TabType = 'generate' | 'summarize' | 'prioritize';

export default function AIPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('generate');
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const handleGenerate = async () => {
    if (!goal.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiApi.generateTodos(goal);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to generate todos. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiApi.summarize();
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to summarize todos. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePrioritize = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await aiApi.prioritize();
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to prioritize todos. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabAction = () => {
    if (activeTab === 'generate' && goal.trim()) {
      handleGenerate();
    } else if (activeTab === 'summarize') {
      handleSummarize();
    } else if (activeTab === 'prioritize') {
      handlePrioritize();
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-8 h-8 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Assistant
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            Let AI help you manage your tasks more effectively
          </p>

          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => {
                setActiveTab('generate');
                setResult(null);
                setError('');
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <List className="w-5 h-5" />
              Generate Todos
            </button>
            <button
              onClick={() => {
                setActiveTab('summarize');
                setResult(null);
                setError('');
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'summarize'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <CheckCircle className="w-5 h-5" />
              Summarize
            </button>
            <button
              onClick={() => {
                setActiveTab('prioritize');
                setResult(null);
                setError('');
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'prioritize'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <TrendingUp className="w-5 h-5" />
              Prioritize
            </button>
          </div>

          {/* Content */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            {activeTab === 'generate' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    What's your goal?
                  </label>
                  <textarea
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    rows={4}
                    placeholder="e.g., Plan a birthday party, Launch a new product, Learn a new language..."
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                  />
                </div>

                <button
                  onClick={handleTabAction}
                  disabled={loading || !goal.trim()}
                  className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Generate Todos
                    </>
                  )}
                </button>
              </div>
            )}

            {activeTab === 'summarize' && (
              <div className="space-y-6">
                <p className="text-gray-600 dark:text-gray-400">
                  Get an AI-powered overview of all your todos with priority breakdown and urgent items.
                </p>

                <button
                  onClick={handleTabAction}
                  disabled={loading}
                  className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      Summarize My Todos
                    </>
                  )}
                </button>
              </div>
            )}

            {activeTab === 'prioritize' && (
              <div className="space-y-6">
                <p className="text-gray-600 dark:text-gray-400">
                  Let AI analyze and reorder your todos based on urgency and importance.
                </p>

                <button
                  onClick={handleTabAction}
                  disabled={loading}
                  className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Prioritizing...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-5 h-5" />
                      Prioritize My Todos
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
              >
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </motion.div>
            )}

            {/* Results */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-6 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {activeTab === 'generate' && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                      Generated Todos
                    </h3>
                    <ul className="space-y-2">
                      {result.todos.map((todo: any, index: number) => (
                        <li
                          key={index}
                          className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                        >
                          <p className="font-medium text-gray-900 dark:text-white">
                            {todo.title}
                          </p>
                          {todo.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {todo.description}
                            </p>
                          )}
                          <div className="flex gap-2 mt-2">
                            <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                              {todo.priority}
                            </span>
                            {todo.due_date && (
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {todo.due_date}
                              </span>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {activeTab === 'summarize' && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                      Summary
                    </h3>
                    <p className="text-gray-700 dark:text-gray-300 mb-4">{result.summary}</p>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {result.breakdown.high_priority}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">High Priority</p>
                      </div>
                      <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                          {result.breakdown.medium_priority}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Medium</p>
                      </div>
                      <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {result.breakdown.low_priority}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Low Priority</p>
                      </div>
                    </div>

                    {result.urgent_todos.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                          Urgent Items
                        </h4>
                        <ul className="space-y-1">
                          {result.urgent_todos.map((todo: string, index: number) => (
                            <li
                              key={index}
                              className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2"
                            >
                              <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                              {todo}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'prioritize' && (
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                      Prioritized Todos
                    </h3>
                    <ul className="space-y-2">
                      {result.prioritized_todos.map((todo: any, index: number) => (
                        <li
                          key={index}
                          className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                        >
                          <div className="flex items-center justify-between">
                            <p className="font-medium text-gray-900 dark:text-white">
                              {todo.title}
                            </p>
                            <span className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                              {todo.priority_score}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {todo.reasoning}
                          </p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
