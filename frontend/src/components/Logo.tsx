import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 28, showText = true }) => {
  return (
    <div className={`flex items-center space-x-2.5 ${className}`}>
      <div className="flex-shrink-0 flex items-center justify-center">
        <svg
          width={size}
          height={size}
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="rounded-md"
          aria-hidden="true"
        >
          <rect width="32" height="32" rx="6" fill="#0f172a" />
          <path
            d="M9 22L16 9L23 22H9Z"
            stroke="#ffffff"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <path
            d="M13 18H19"
            stroke="#2563eb"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
          <circle cx="16" cy="9" r="2" fill="#10b981" />
          <circle cx="9" cy="22" r="2" fill="#2563eb" />
          <circle cx="23" cy="22" r="2" fill="#10b981" />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-tight">
          <div className="flex items-center space-x-1.5">
            <span className="text-sm font-bold text-slate-900 tracking-tight">
              Emend
            </span>
            <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded border border-slate-200">
              v1.0
            </span>
          </div>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Automated Code Repair & Blast-Radius Engine
          </span>
        </div>
      )}
    </div>
  );
};
