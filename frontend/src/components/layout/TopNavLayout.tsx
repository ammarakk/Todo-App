'use client';

import { ReactNode } from 'react';
import { Navbar } from '@/components/layout/Navbar';

interface TopNavLayoutProps {
  children: ReactNode;
}

export function TopNavLayout({ children }: TopNavLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  );
}
