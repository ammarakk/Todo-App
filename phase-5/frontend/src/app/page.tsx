'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import TaskList from '@/components/TaskList'
import { Task } from '@/types/task'

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleTaskCreated = (task: Task) => {
    setTasks(prev => [task, ...prev])
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🤖 AI Todo Assistant
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage tasks with natural language • Powered by AI
          </p>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-1">
            <ChatInterface onTaskCreated={handleTaskCreated} />
          </div>

          {/* Task List */}
          <div className="lg:col-span-1">
            <TaskList tasks={tasks} isLoading={isLoading} />
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-2">💬</div>
            <h3 className="font-semibold mb-1">Natural Language</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Create tasks by simply chatting
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-2">⚡</div>
            <h3 className="font-semibold mb-1">AI Powered</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Smart extraction and prioritization
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-2">🔔</div>
            <h3 className="font-semibold mb-1">Reminders</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Never miss important deadlines
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
