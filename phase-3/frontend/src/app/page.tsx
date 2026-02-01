import { redirect } from 'next/navigation';

/**
 * Root page that redirects based on authentication state.
 *
 * This page serves as the entry point and will:
 * - Redirect authenticated users to /dashboard
 * - Redirect unauthenticated users to /login
 *
 * Authentication checking will be implemented with middleware or client-side state.
 */
export default function RootPage() {
  // For now, redirect to login (auth will be implemented in Phase 3)
  redirect('/login');
}

/**
 * Metadata for the root page.
 */
export const metadata = {
  title: 'Todo App',
  description: 'Premium task management with AI assistance',
};
