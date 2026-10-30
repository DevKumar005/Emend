import React, { useState } from 'react';
import { RepairAttempt } from '../types';
import { FileCode, AlertCircle, CheckCircle, Cpu, Copy, Check, RotateCcw } from 'lucide-react';

interface CodeDiffProps {
  attempts: RepairAttempt[];
}

export const CodeDiff: React.FC<CodeDiffProps> = ({ attempts }) => {
  const [activeAttemptIdx, setActiveAttemptIdx] = useState(
    attempts && attempts.length > 0 ? attempts.length - 1 : 0
  );
  const [copied, setCopied] = useState(false);

  if (!attempts || attempts.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400 text-xs font-mono shadow-sm">
        No code patches generated yet.
      </div>
    );
  }

  const currentAttempt = attempts[activeAttemptIdx] || attempts[0];

  const handleCopyDiff = () => {
    if (!currentAttempt?.diff) return;
    navigator.clipboard.writeText(currentAttempt.diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderDiffLines = (rawDiff: string) => {
    if (!rawDiff || !rawDiff.trim()) {
      return (
        <div className="text-slate-400 italic p-4 text-xs font-mono">
          No diff content available for this attempt.
        </div>
      );
    }

    return rawDiff.split('\n').map((line, idx) => {
      let lineStyle = 'text-slate-700';
      let bgStyle = '';

      if (line.startsWith('+') && !line.startsWith('+++')) {
        lineStyle = 'text-emerald-900 font-semibold';
        bgStyle = 'bg-emerald-50/90 border-l-2 border-emerald-500';
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        lineStyle = 'text-rose-900 font-semibold';
        bgStyle = 'bg-rose-50/90 border-l-2 border-rose-500';
      } else if (line.startsWith('@@')) {
        lineStyle = 'text-blue-700 font-bold';
        bgStyle = 'bg-blue-50/60';
      } else if (line.startsWith('diff --git') || line.startsWith('index ')) {
        lineStyle = 'text-slate-400 font-mono';
      }

      return (
        <div key={idx} className={`px-4 py-0.5 font-mono text-xs whitespace-pre ${lineStyle} ${bgStyle}`}>
          {line || ' '}
        </div>
      );
    });
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 font-mono shadow-sm space-y-3.5">
      
      {/* Header and Attempt Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-100 text-xs">
        <div className="flex items-center space-x-2">
          <FileCode className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-bold uppercase text-slate-800">
            Patch Inspector
          </span>
          <span className="text-slate-500 text-[11px]">
            ({attempts.length} attempts)
          </span>
        </div>

        {/* Attempt Tabs */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          {attempts.map((att, idx) => {
            const isActive = idx === activeAttemptIdx;
            const isAccepted = att.status === 'accepted' || att.status === 'verified';
            const isReverted = att.status === 'reverted' || att.status === 'regression';

            return (
              <button
                key={att.n || idx}
                onClick={() => setActiveAttemptIdx(idx)}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs transition ${
                  isActive
                    ? 'bg-white text-slate-900 font-bold shadow-xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span>Attempt {att.n || idx + 1}</span>
                {isAccepted && <CheckCircle className="w-3 h-3 text-emerald-600" />}
                {isReverted && <RotateCcw className="w-3 h-3 text-amber-600" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Rationale & Diagnosis Box */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1.5">
        <div className="flex items-center justify-between text-slate-500 text-[11px]">
          <div className="flex items-center space-x-1.5 text-slate-700 font-semibold">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
            <span>Nemotron Hypothesis</span>
          </div>
          <span className="text-slate-500 font-mono">
            {currentAttempt.model.split('/').pop()} · {currentAttempt.tokens_in} in / {currentAttempt.tokens_out} out
          </span>
        </div>

        <p className="text-slate-700 font-sans leading-relaxed text-xs">
          {currentAttempt.rationale || 'No rationale logged.'}
        </p>

        {currentAttempt.regressions && currentAttempt.regressions.length > 0 && (
          <div className="p-2 rounded bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2 mt-1">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Regression caught by Blast Radius cascade:</span>
              <ul className="list-disc pl-4 mt-0.5 font-mono text-[11px]">
                {currentAttempt.regressions.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
              <span className="text-[10px] text-amber-800 font-sans block mt-0.5">
                Working tree reverted automatically before next attempt.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Unified Diff View */}
      <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
        <div className="bg-slate-50 px-3.5 py-1.5 border-b border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <span className="font-semibold">Unified Diff</span>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 uppercase font-bold text-slate-700">
              {currentAttempt.status}
            </span>
            <button
              onClick={handleCopyDiff}
              className="text-slate-500 hover:text-slate-800 flex items-center space-x-1 text-[11px]"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>

        <div className="py-2 overflow-x-auto max-h-[380px]">
          {renderDiffLines(currentAttempt.diff)}
        </div>
      </div>

    </div>
  );
};
