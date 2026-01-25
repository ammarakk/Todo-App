'use client';

// Phase III - AI-Powered Todo Chatbot
// Chat Page - Advanced chat interface with animated UI

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { getToken } from '@/lib/auth';
import { Loader2 } from 'lucide-react';
import ChatInterface from '@/components/ChatInterfaceAdvanced';

export default function ChatPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthenticated } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-900 dark:to-slate-800">
        <div className="text-center">
          <Loader2 className="w-16 h-16 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading AI Assistant...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const jwtToken = getToken() || '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm shadow-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl blur-lg opacity-50 animate-pulse"></div>
                <div className="relative bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  AI Todo Assistant
                  <span className="text-xs bg-gradient-to-r from-blue-500 to-purple-600 text-white px-2 py-1 rounded-full">Phase III</span>
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Manage tasks naturally • English & Urdu supported
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.email || ''}
                </p>
              </div>

              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl overflow-hidden" style={{ height: 'calc(100vh - 220px)', minHeight: '700px' }}>
          <ChatInterface jwtToken={jwtToken} />
        </div>
      </main>

      {/* Footer with tips */}
      <footer className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-t border-slate-200 dark:border-slate-700 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Tips */}
            <div className="text-center md:text-left">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">💡 Quick Tips</h3>
              <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Speak naturally in English or Urdu</li>
                <li>• AI will create, view, update, or delete tasks</li>
                <li>• Add priority, due dates, and tags</li>
              </ul>
            </div>

            {/* Examples */}
            <div className="text-center">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">🗣️ Try Saying</h3>
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>"Add a task to buy milk"</p>
                <p>"میرے ٹاسک دکھاؤ"</p>
                <p>"Show high priority tasks"</p>
              </div>
            </div>

            {/* Features */}
            <div className="text-center md:text-right">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">✨ Features</h3>
              <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Bilingual AI assistant</li>
                <li>• Animated robot avatar</li>
                <li>• Conversation history saved</li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
