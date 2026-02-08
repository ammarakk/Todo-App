'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Root page that redirects to login.
 *
 * This page serves as the entry point and redirects users to /login.
 * Using client-side redirect to avoid hydration errors.
 */
export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login immediately
    router.replace('/login');
  }, [router]);

  // Show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white text-lg">Loading...</p>
      </div>
    </div>
  );
}
