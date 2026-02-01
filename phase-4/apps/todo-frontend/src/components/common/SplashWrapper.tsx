'use client';

import { useEffect, useState } from 'react';
import { SplashScreen } from './SplashScreen';

export function SplashWrapper({ children }: { children: React.ReactNode }) {
  const [showSplash, setShowSplash] = useState(true); // Always show for now

  useEffect(() => {
    // Show splash screen every time for now
    // Later we can make it show only once:
    // const hasSeenSplash = localStorage.getItem('has_seen_splash');
    // if (!hasSeenSplash) {
    //   setShowSplash(true);
    //   localStorage.setItem('has_seen_splash', 'true');
    // }
  }, []);

  return (
    <>
      {showSplash && <SplashScreen onComplete={() => setShowSplash(false)} />}
      {children}
    </>
  );
}
