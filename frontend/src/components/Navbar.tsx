import React from 'react';
import { Logo } from './Logo';
import { Play, Cpu, GitFork, Github, ExternalLink, Terminal } from 'lucide-react';

interface NavbarProps {
  onRecordedReplay?: (demoId: string) => void;
  isLiveTokenFactory?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onRecordedReplay, isLiveTokenFactory = false }) => {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 text-slate-800 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 sm:h-15 flex items-center justify-between gap-3">
        
        {/* Brand & Logo */}
        <Logo />

        {/* Real-time Engine Diagnostic Chips (Desktop >= 1024px) */}
        <div className="hidden lg:flex items-center space-x-2 text-xs font-mono">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-50 border border-slate-200 text-slate-700">
            <Cpu className="w-3.5 h-3.5 text-slate-600" />
            <span>Nemotron 120B / 30B</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-50 border border-slate-200 text-slate-700">
            <GitFork className="w-3.5 h-3.5 text-slate-600" />
            <span>AST Blast Radius</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-50/80 border border-emerald-200 text-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span>{isLiveTokenFactory ? 'Live Nebius API' : 'Deterministic Sandbox'}</span>
          </div>
        </div>

        {/* Action Controls & GitHub Repo Button */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          {onRecordedReplay && (
            <button
              onClick={() => onRecordedReplay('billing_ripple')}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium shadow-2xs transition active:scale-98"
              title="Instant replay of the ripple catch proof loop"
            >
              <Play className="w-3 h-3 fill-white" />
              <span>Instant Replay</span>
            </button>
          )}

          {/* GitHub Repository Link */}
          <a
            href="https://github.com/DevKumar005/Emend"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 rounded-md border border-slate-300 transition shadow-2xs group"
            title="View DevKumar005/Emend on GitHub"
          >
            <Github className="w-3.5 h-3.5 text-slate-700 group-hover:text-slate-900" />
            <span className="font-mono text-xs font-semibold text-slate-800">
              GitHub Repo
            </span>
            <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-slate-600 hidden xs:inline" />
          </a>
        </div>

      </div>
    </header>
  );
};
