'use client';

import { Search, Filter } from 'lucide-react';

interface TodoFiltersProps {
  filters: {
    status: 'all' | 'pending' | 'completed';
    priority: string | undefined;
    search: string;
    sortBy: 'created_at' | 'due_date' | 'priority';
  };
  setFilters: (filters: any) => void;
}

export function TodoFilters({ filters, setFilters }: TodoFiltersProps) {
  return (
    <div className="flex-1 w-full">
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-cyan-400" />
          <input
            type="text"
            placeholder="Search todos..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-cyan-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 dark:focus:shadow-[0_0_10px_rgba(6,182,212,0.5)] focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
          />
        </div>

        {/* Status Filter */}
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value as any })}
          className="px-4 py-2 border border-gray-300 dark:border-cyan-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-cyan-500 dark:focus:shadow-[0_0_10px_rgba(6,182,212,0.5)] focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>

        {/* Priority Filter */}
        <select
          value={filters.priority || 'all'}
          onChange={(e) =>
            setFilters({
              ...filters,
              priority: e.target.value === 'all' ? undefined : e.target.value,
            })
          }
          className="px-4 py-2 border border-gray-300 dark:border-amber-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-amber-500 dark:focus:shadow-[0_0_10px_rgba(251,191,36,0.5)] focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
        >
          <option value="all">All Priority</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        {/* Sort By */}
        <select
          value={filters.sortBy}
          onChange={(e) => setFilters({ ...filters, sortBy: e.target.value as any })}
          className="px-4 py-2 border border-gray-300 dark:border-purple-500/50 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-purple-500 dark:focus:shadow-[0_0_10px_rgba(192,132,252,0.5)] focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-all"
        >
          <option value="created_at">Latest First</option>
          <option value="due_date">Due Date</option>
          <option value="priority">Priority</option>
        </select>
      </div>
    </div>
  );
}
