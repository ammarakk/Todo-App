'use client';

// ChatWidgetProvider - Provides JWT token to FloatingChatWidget
// This component is a client wrapper that extracts auth state

'use client';

import { useAuth } from '@/hooks/use-auth';
import FloatingChatWidget from './FloatingChatWidget';

export default function ChatWidgetProvider() {
  const { token } = useAuth();

  return <FloatingChatWidget jwtToken={token} />;
}
