'use client';

// Phase III - AI-Powered Todo Chatbot
// Robot Avatar - Animated robot icon for chat interface

import React from 'react';

interface RobotAvatarProps {
  size?: number;
  isThinking?: boolean;
  className?: string;
}

const RobotAvatar: React.FC<RobotAvatarProps> = ({
  size = 40,
  isThinking = false,
  className = ''
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* Glow effect */}
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      {/* Robot Head */}
      <rect
        x="25"
        y="20"
        width="50"
        height="55"
        rx="8"
        fill="#6366f1"
        className={isThinking ? 'animate-pulse' : ''}
      />

      {/* Antenna */}
      <line x1="50" y1="20" x2="50" y2="10" stroke="#6366f1" strokeWidth="3" />
      <circle
        cx="50"
        cy="8"
        r="4"
        fill="#ec4899"
        className={isThinking ? 'animate-ping' : ''}
      />

      {/* Eyes - Animated blinking */}
      <g className={isThinking ? 'animate-bounce' : ''}>
        <ellipse cx="38" cy="42" rx="8" ry="10" fill="#ffffff" />
        <ellipse cx="62" cy="42" rx="8" ry="10" fill="#ffffff" />

        {/* Pupils - Move when thinking */}
        <circle
          cx="38"
          cy={isThinking ? 44 : 42}
          r="4"
          fill="#1e293b"
          className={isThinking ? 'animate-pulse' : ''}
        >
          <animate
            attributeName="cx"
            values="38;40;38"
            dur={isThinking ? '1s' : '3s'}
            repeatCount="indefinite"
          />
        </circle>
        <circle
          cx="62"
          cy={isThinking ? 44 : 42}
          r="4"
          fill="#1e293b"
          className={isThinking ? 'animate-pulse' : ''}
        >
          <animate
            attributeName="cx"
            values="62;60;62"
            dur={isThinking ? '1s' : '3s'}
            repeatCount="indefinite"
          />
        </circle>
      </g>

      {/* Mouth - Animated when talking */}
      <path
        d="M 40 60 Q 50 {isThinking ? 65 : 62} 60 60"
        stroke="#ffffff"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
        filter="url(#glow)"
      >
        <animate
          attributeName="d"
          values={`M 40 60 Q 50 ${isThinking ? 65 : 62} 60 60;M 40 60 Q 50 ${isThinking ? 60 : 64} 60 60;M 40 60 Q 50 ${isThinking ? 65 : 62} 60 60`}
          dur="0.5s"
          repeatCount="indefinite"
        />
      </path>

      {/* Cheeks - Blink when happy */}
      <ellipse
        cx="30"
        cy="52"
        rx="4"
        ry="2"
        fill="#f472b6"
        opacity="0.6"
        className="animate-pulse"
      />
      <ellipse
        cx="70"
        cy="52"
        rx="4"
        ry="2"
        fill="#f472b6"
        opacity="0.6"
        className="animate-pulse"
      />

      {/* Ears */}
      <rect x="18" y="35" width="10" height="20" rx="4" fill="#4f46e5" />
      <rect x="72" y="35" width="10" height="20" rx="4" fill="#4f46e5" />
    </svg>
  );
};

export default RobotAvatar;
