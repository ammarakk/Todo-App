import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

import { AuthProvider } from '@/hooks/use-auth';
import { SplashWrapper } from '@/components/common/SplashWrapper';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo App - Premium Task Management',
  description: 'Manage your tasks efficiently with AI-powered todo application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-white`}>
        <ErrorBoundary>
          <SplashWrapper>
            <AuthProvider>
              {children}
            </AuthProvider>
          </SplashWrapper>
        </ErrorBoundary>
      </body>
    </html>
  );
}
