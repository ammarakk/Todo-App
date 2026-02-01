'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Circle, ListTodo } from 'lucide-react';
import { useTodos } from '@/hooks/use-todos';

export function TodoStats() {
  const { todos } = useTodos();

  const total = todos.length;
  const completed = todos.filter((t) => t.status === 'completed').length;
  const pending = todos.filter((t) => t.status === 'pending').length;

  const stats = [
    {
      label: 'Total Tasks',
      value: total,
      icon: ListTodo,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50 dark:bg-cyan-900/20',
      textColor: 'text-blue-600 dark:text-cyan-400',
      shadowColor: 'shadow-[0_0_20px_rgba(6,182,212,0.3)]',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle2,
      color: 'bg-green-500',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      textColor: 'text-green-600 dark:text-green-400',
      shadowColor: 'shadow-[0_0_20px_rgba(34,197,94,0.3)]',
    },
    {
      label: 'Pending',
      value: pending,
      icon: Circle,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-amber-900/20',
      textColor: 'text-yellow-600 dark:text-amber-400',
      shadowColor: 'shadow-[0_0_20px_rgba(251,191,36,0.3)]',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ staggerChildren: 0.1 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-6"
    >
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`${stat.bgColor} rounded-xl p-6 border border-gray-200 dark:border-gray-700 dark:${stat.shadowColor} backdrop-blur-sm transition-all hover:scale-105`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                {stat.label}
              </p>
              <p className={`text-3xl font-bold ${stat.textColor} dark:drop-shadow-[0_0_8px_currentColor]`}>{stat.value}</p>
            </div>
            <div className={`${stat.color} p-3 rounded-lg dark:shadow-[0_0_15px_rgba(255,255,255,0.3)]`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
