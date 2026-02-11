'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/use-auth';
import { useTodos } from '@/hooks/use-todos';
import { TopNavLayout } from '@/components/layout/TopNavLayout';
import { TodoStats } from '@/components/dashboard/TodoStats';
import { TodoList } from '@/components/dashboard/TodoList';
import { TodoFilters } from '@/components/dashboard/TodoFilters';
import { CreateTodoModal } from '@/components/dashboard/CreateTodoModal';
// T026: Import AI chat components
import { AIChatButton, AIChatPanel } from '@/components/ai-assistant';
import { Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  // T026: AI chat state
  const [isAIChatOpen, setIsAIChatOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all' as 'all' | 'pending' | 'completed',
    priority: undefined as string | undefined,
    search: '',
    sortBy: 'created_at' as 'created_at' | 'due_date' | 'priority',
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Fetch todos with filters
  const { todos, loading, error, refetch, createTodo, toggleComplete, deleteTodo } =
    useTodos({
      status: filters.status === 'all' ? undefined : filters.status,
      priority: filters.priority,
      search: filters.search || undefined,
      sort_by: filters.sortBy,
    });

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  const handleCreateTodo = async (todoData: any) => {
    try {
      await createTodo(todoData);
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      // Error is already displayed in the modal, don't close it
      console.error('Failed to create todo in dashboard:', error);
    }
  };

  const handleToggleComplete = async (todoId: string, completed: boolean) => {
    await toggleComplete(todoId, completed);
    refetch();
  };

  const handleDeleteTodo = async (todoId: string) => {
    if (confirm('Are you sure you want to delete this todo?')) {
      await deleteTodo(todoId);
      refetch();
    }
  };

  // T027: Handle AI actions - sync state with dashboard
  const handleAIActionExecuted = (action: string, data?: any) => {
    console.log('AI action executed:', action, data);
    // Refetch todos to show changes made by AI
    // Small delay to ensure backend operation completes before refetch
    setTimeout(() => {
      refetch();
    }, 500);
  };

  return (
    <TopNavLayout>
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white dark:drop-shadow-[0_0_10px_rgba(6,182,212,0.5)]">
          Welcome back, {user?.name?.split(' ')[0]}! 👋
        </h1>
        <p className="text-gray-600 dark:text-cyan-400/80 mt-1">
          Here's what's happening with your tasks today
        </p>
      </motion.div>

      {/* Stats */}
      <TodoStats />

      {/* Filters and Create Button */}
      <div className="mt-8 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <TodoFilters filters={filters} setFilters={setFilters} />
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 dark:from-cyan-500 dark:to-purple-500 hover:from-blue-700 hover:to-purple-700 dark:hover:from-cyan-400 dark:hover:to-purple-400 text-white font-semibold py-2 px-6 rounded-lg transition-all duration-200 dark:shadow-[0_0_15px_rgba(6,182,212,0.5)] dark:hover:shadow-[0_0_25px_rgba(6,182,212,0.8)]"
        >
          + New Todo
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
        >
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </motion.div>
      )}

      {/* Todo List */}
      <TodoList
        todos={todos}
        loading={loading}
        onToggleComplete={handleToggleComplete}
        onDelete={handleDeleteTodo}
      />

      {/* Create Todo Modal */}
      {showCreateModal && (
        <CreateTodoModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateTodo}
        />
      )}

      {/* T026: AI Chat Button and Panel */}
      <AIChatButton
        isOpen={isAIChatOpen}
        onClick={() => setIsAIChatOpen(!isAIChatOpen)}
      />
      <AIChatPanel
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
        onActionExecuted={handleAIActionExecuted}
      />
    </TopNavLayout>
  );
}
