import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 28, showText = true }) => {
  return (
    <div className={`flex items-center space-x-2.5 ${className}`}>
      {/* Authentic Engineering Mark: Precision Delta & Code Repair Node */}
      <div className="flex-shrink-0 flex items-center justify-center">
        <svg
          width={size}
          height={size}
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="rounded-md"
        >
          {/* Solid Container */}
          <rect width="32" height="32" rx="6" fill="#1f2328" />
          
          {/* Clean Git / AST Delta Structure */}
          <path
            d="M9 22L16 9L23 22H9Z"
            stroke="#ffffff"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <path
            d="M13 18H19"
            stroke="#0969da"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <circle cx="16" cy="9" r="2" fill="#2da44e" />
          <circle cx="9" cy="22" r="2" fill="#0969da" />
          <circle cx="23" cy="22" r="2" fill="#2da44e" />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-tight">
          <div className="flex items-center space-x-1.5">
            <span className="text-base font-bold text-slate-900 tracking-tight font-sans">
              Emend
            </span>
            <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded border border-slate-200">
              agent
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-sans hidden sm:inline">
            Automated Code Repair & Blast-Radius Engine
          </span>
        </div>
      )}
    </div>
  );
};
