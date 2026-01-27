'use client';

import { motion } from 'framer-motion';
import { MessageCircle, Sparkles, X } from 'lucide-react';

/**
 * T019: AIChatButton component
 * Floating button to open AI chat panel
 */
export interface AIChatButtonProps {
  isOpen: boolean;
  onClick: () => void;
  unreadCount?: number;
}

export function AIChatButton({ isOpen, onClick, unreadCount = 0 }: AIChatButtonProps) {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      className="fixed bottom-20 right-4 z-50 md:bottom-6 md:right-6"
    >
      <motion.button
        onClick={onClick}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`
          relative w-14 h-14 md:w-16 md:h-16 rounded-full flex items-center justify-center
          bg-gradient-to-br shadow-lg
          transition-all duration-300
          ${
            isOpen
              ? 'from-red-500 to-pink-600 hover:from-red-400 hover:to-pink-500 dark:shadow-[0_0_20px_rgba(239,68,68,0.5)]'
              : 'from-cyan-500 to-purple-600 hover:from-cyan-400 hover:to-purple-500 dark:shadow-[0_0_20px_rgba(6,182,212,0.5)]'
          }
        `}
        aria-label={isOpen ? 'Close AI chat' : 'Open AI chat'}
      >
        {/* Animated background glow */}
        {!isOpen && (
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 opacity-50 blur-xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}

        {/* Pulsing ring effect */}
        {!isOpen && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-cyan-400 dark:border-cyan-300"
            animate={{
              scale: [1, 1.5, 1.5],
              opacity: [1, 0, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        )}

        {/* Icon */}
        <motion.div
          initial={false}
          animate={{
            rotate: isOpen ? 90 : 0,
            scale: isOpen ? [1, 0.8, 1] : 1,
          }}
          transition={{ duration: 0.2 }}
        >
          {isOpen ? (
            <X className="w-7 h-7 text-white" strokeWidth={2.5} />
          ) : (
            <>
              <MessageCircle className="w-7 h-7 text-white" strokeWidth={2.5} />
              <Sparkles
                className="w-3 h-3 text-yellow-300 absolute top-3 right-3"
                fill="currentColor"
              />
            </>
          )}
        </motion.div>

        {/* Unread badge */}
        {unreadCount > 0 && !isOpen && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold border-2 border-white dark:border-gray-900"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </motion.span>
        )}
      </motion.button>
    </motion.div>
  );
}
