'use client';

import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

/**
 * Theme toggle component with light/dark/system options.
 *
 * Allows users to switch between light, dark, and system themes.
 * Uses next-themes for theme management.
 */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Button variant="ghost" size="icon" disabled>
        <Sun className="h-5 w-5" />
        <span className="sr-only">Toggle theme</span>
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="dark:hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] dark:hover:bg-cyan-500/10 transition-all">
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 dark:text-cyan-400" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 dark:text-cyan-400 dark:drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="dark:bg-gray-900 dark:border-cyan-500/30 dark:shadow-[0_0_20px_rgba(6,182,212,0.3)]">
        <DropdownMenuItem onClick={() => setTheme('light')} className="dark:text-gray-300 dark:hover:bg-cyan-500/10 dark:hover:shadow-[0_0_10px_rgba(6,182,212,0.3)]">
          <Sun className="mr-2 h-4 w-4" />
          <span>Light</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')} className="dark:text-gray-300 dark:hover:bg-cyan-500/10 dark:hover:shadow-[0_0_10px_rgba(6,182,212,0.3)]">
          <Moon className="mr-2 h-4 w-4 dark:text-cyan-400" />
          <span>Dark</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')} className="dark:text-gray-300 dark:hover:bg-cyan-500/10 dark:hover:shadow-[0_0_10px_rgba(6,182,212,0.3)]">
          <span className="mr-2 h-4 w-4">💻</span>
          <span>System</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
